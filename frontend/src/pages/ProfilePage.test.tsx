/**
 * Tests for the profile page (M3.4): name and headline, adding, editing and deleting
 * each kind of entry, mistakes shown under their field, and changing the password.
 * The whole app runs against the pretend backend (src/test/fakeBackend.ts).
 */
import { fireEvent, render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "../App";
import { i18n } from "../i18n";
import ar from "../locales/ar.json";
import en from "../locales/en.json";
import { fakeBackend } from "../test/fakeBackend";

const EMAIL = "me@example.com";
const PASSWORD = "a long enough password";
const F = en.profile.fields;

afterEach(() => {
  vi.unstubAllGlobals();
});

async function openProfile() {
  const backend = fakeBackend();
  backend.addUser(EMAIL, PASSWORD);
  backend.logIn(EMAIL);
  render(
    <MemoryRouter initialEntries={["/profile"]}>
      <App />
    </MemoryRouter>,
  );
  await screen.findByRole("heading", { name: en.profile.title });
  return backend;
}

function section(title: string) {
  return within(screen.getByRole("region", { name: title }));
}

function type(scope: ReturnType<typeof section>, label: string, value: string) {
  fireEvent.change(scope.getByLabelText(label, { exact: false }), { target: { value } });
}

const click = (scope: ReturnType<typeof section>, name: string) =>
  fireEvent.click(scope.getByRole("button", { name }));

describe("ProfilePage", () => {
  it("is linked from the header", async () => {
    await openProfile();
    expect(screen.getByRole("link", { name: en.nav.profile })).toBeTruthy();
  });

  it("saves the name and headline", async () => {
    await openProfile();
    const page = within(screen.getByRole("main"));

    fireEvent.change(page.getByLabelText(F.display_name), { target: { value: "Amina" } });
    fireEvent.change(page.getByLabelText(F.headline), { target: { value: "Data student" } });
    fireEvent.click(page.getAllByRole("button", { name: en.profile.save })[0]!);

    expect(await screen.findByText(en.profile.saved)).toBeTruthy();
  });

  it.each([
    [en.profile.education, F.institution, "Université de Lyon"],
    [en.profile.experience, F.organization, "Acme"],
  ])("adds, edits and deletes an entry in %s", async (texts, titleLabel, title) => {
    const backend = await openProfile();
    let list = section(texts.title);
    expect(list.getByText(texts.empty)).toBeTruthy();

    // Add
    click(list, texts.add);
    type(list, titleLabel, title);
    type(list, F.start_date, "2024-09-01");
    click(list, en.profile.save);
    expect(await list.findByText(title)).toBeTruthy();
    expect(list.getByText(/September 2024/)).toBeTruthy();

    // Edit
    click(list, `Edit ${title}`);
    type(list, titleLabel, `${title} (2)`);
    click(list, en.profile.save);
    expect(await list.findByText(`${title} (2)`)).toBeTruthy();

    // Delete, after confirming
    click(list, `Delete ${title} (2)`);
    click(list, en.profile.delete_yes);
    list = section(texts.title);
    expect(await list.findByText(texts.empty)).toBeTruthy();
    expect(Object.values(backend.lists(EMAIL) ?? {}).flat()).toEqual([]);
  });

  it("adds a project with its link", async () => {
    const backend = await openProfile();
    const list = section(en.profile.projects.title);

    click(list, en.profile.projects.add);
    type(list, F.title, "Library app");
    type(list, F.description, "A FastAPI app for a school library.");
    type(list, F.url, "https://github.com/example/library");
    click(list, en.profile.save);

    expect(await list.findByText("Library app")).toBeTruthy();
    expect(backend.lists(EMAIL)?.projects[0]?.url).toBe("https://github.com/example/library");
  });

  it("cancelling a delete keeps the entry", async () => {
    await openProfile();
    const list = section(en.profile.projects.title);
    click(list, en.profile.projects.add);
    type(list, F.title, "Keep me");
    type(list, F.description, "Still here.");
    click(list, en.profile.save);
    await list.findByText("Keep me");

    click(list, "Delete Keep me");
    click(list, en.profile.cancel);

    expect(list.getByText("Keep me")).toBeTruthy();
  });

  it("shows mistakes under their field before sending", async () => {
    const backend = await openProfile();
    const list = section(en.profile.projects.title);

    click(list, en.profile.projects.add);
    type(list, F.title, "No description");
    type(list, F.url, "javascript:alert(1)");
    click(list, en.profile.save);

    expect(list.getByText(en.profile.problems.required)).toBeTruthy();
    expect(list.getByText(en.profile.problems.url)).toBeTruthy();
    expect(list.getByLabelText(F.url).getAttribute("aria-invalid")).toBe("true");
    expect(backend.calls.filter((call) => call.startsWith("POST /profile"))).toEqual([]);
  });

  it("refuses an end date before the start date", async () => {
    await openProfile();
    const list = section(en.profile.education.title);

    click(list, en.profile.education.add);
    type(list, F.institution, "School");
    type(list, F.start_date, "2024-09-01");
    type(list, F.end_date, "2023-06-30");
    click(list, en.profile.save);

    expect(list.getByText(en.profile.problems.end_before_start)).toBeTruthy();
  });

  it("shows the backend's validation errors under their field", async () => {
    const backend = await openProfile();
    const list = section(en.profile.experience.title);
    click(list, en.profile.experience.add);
    type(list, F.organization, "Acme");
    backend.answerNextWith(422, {
      detail: [{ loc: ["body", "role"], type: "string_too_long", msg: "too long" }],
    });

    click(list, en.profile.save);

    const problem = await list.findByText(en.profile.problems.too_long);
    expect(problem.id).toBe(list.getByLabelText(F.role).getAttribute("aria-describedby"));
  });

  it("says when an entry can't be deleted", async () => {
    const backend = await openProfile();
    const list = section(en.profile.projects.title);
    click(list, en.profile.projects.add);
    type(list, F.title, "Gone elsewhere");
    type(list, F.description, "Deleted in another tab.");
    click(list, en.profile.save);
    await list.findByText("Gone elsewhere");
    backend.answerNextWith(404, { detail: { code: "not_found" } });

    click(list, "Delete Gone elsewhere");
    click(list, en.profile.delete_yes);

    expect((await list.findByRole("alert")).textContent).toBe(en.errors.not_found);
  });

  it("works in Arabic, with typed text in its own direction", async () => {
    await i18n.changeLanguage("ar");
    const backend = fakeBackend();
    backend.addUser(EMAIL, PASSWORD, "ar");
    backend.logIn(EMAIL);
    render(
      <MemoryRouter initialEntries={["/profile"]}>
        <App />
      </MemoryRouter>,
    );
    await screen.findByRole("heading", { name: ar.profile.title });

    const list = section(ar.profile.education.title);
    click(list, ar.profile.education.add);
    expect(list.getByLabelText(ar.profile.fields.institution, { exact: false }).dir).toBe("auto");
    expect(document.documentElement.dir).toBe("rtl");
  });
});

describe("changing the password", () => {
  const passwordSection = () => section(en.password.title);

  it("changes it and says so", async () => {
    const backend = await openProfile();
    type(passwordSection(), en.password.current, PASSWORD);
    type(passwordSection(), en.password.new, "a brand new password");

    click(passwordSection(), en.password.change);

    expect(await passwordSection().findByText(en.password.changed)).toBeTruthy();
    expect(backend.passwordOf(EMAIL)).toBe("a brand new password");
    // Still logged in.
    expect(screen.getByRole("button", { name: en.auth.log_out })).toBeTruthy();
  });

  it("says when the current password is wrong, and stays logged in", async () => {
    const backend = await openProfile();
    type(passwordSection(), en.password.current, "not my password");
    type(passwordSection(), en.password.new, "a brand new password");

    click(passwordSection(), en.password.change);

    expect((await passwordSection().findByRole("alert")).textContent).toBe(
      en.errors.wrong_password,
    );
    expect(backend.passwordOf(EMAIL)).toBe(PASSWORD);
    expect(screen.getByRole("heading", { name: en.profile.title })).toBeTruthy();
  });

  it("checks the new password's length first", async () => {
    await openProfile();
    type(passwordSection(), en.password.current, PASSWORD);
    type(passwordSection(), en.password.new, "short");

    click(passwordSection(), en.password.change);

    expect(passwordSection().getByRole("alert").textContent).toBe(
      en.auth.validation.password_too_short,
    );
  });
});
