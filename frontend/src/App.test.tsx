/**
 * Tests for signing up, logging in and out, and pages only logged-in users can open
 * (M3.2). The whole app runs against a pretend backend (src/test/fakeBackend.ts).
 */
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, useLocation } from "react-router";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";
import { i18n } from "./i18n";
import ar from "./locales/ar.json";
import en from "./locales/en.json";
import fr from "./locales/fr.json";
import { fakeBackend } from "./test/fakeBackend";

const PASSWORD = "a long enough password";

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

function Where() {
  const location = useLocation();
  return <output data-testid="path">{location.pathname}</output>;
}

function start(path: string) {
  render(
    <MemoryRouter initialEntries={[path]}>
      <App />
      <Where />
    </MemoryRouter>,
  );
}

const path = () => screen.getByTestId("path").textContent;

function fill(email: string, password: string) {
  fireEvent.change(screen.getByLabelText(en.auth.email), {
    target: { value: email },
  });
  fireEvent.change(screen.getByLabelText(en.auth.password), {
    target: { value: password },
  });
}

async function submit(label: string) {
  fireEvent.click(await screen.findByRole("button", { name: label }));
}

describe("pages for logged-in users", () => {
  it("sends anonymous visitors to the login page", async () => {
    fakeBackend();
    start("/");
    expect(await screen.findByRole("heading", { name: en.auth.log_in })).toBeTruthy();
    expect(path()).toBe("/login");
  });

  it("shows the home page to a logged-in user", async () => {
    const backend = fakeBackend();
    backend.addUser("me@example.com", PASSWORD);
    backend.logIn("me@example.com");
    start("/");
    expect(await screen.findByText("me@example.com")).toBeTruthy();
    expect(path()).toBe("/");
  });

  it("sends a logged-in user away from the login page", async () => {
    const backend = fakeBackend();
    backend.addUser("me@example.com", PASSWORD);
    backend.logIn("me@example.com");
    start("/login");
    expect(await screen.findByText("me@example.com")).toBeTruthy();
    expect(path()).toBe("/");
  });
});

describe("logging in", () => {
  it("logs in and goes to the home page", async () => {
    const backend = fakeBackend();
    backend.addUser("me@example.com", PASSWORD);
    start("/login");
    await screen.findByRole("heading", { name: en.auth.log_in });

    fill("me@example.com", PASSWORD);
    await submit(en.auth.log_in);

    expect(await screen.findByText("me@example.com")).toBeTruthy();
    expect(path()).toBe("/");
  });

  it("goes back to the page first asked for", async () => {
    const backend = fakeBackend();
    backend.addUser("me@example.com", PASSWORD);
    start("/somewhere");
    // Unknown pages go home, and home needs a login.
    await screen.findByRole("heading", { name: en.auth.log_in });
    fill("me@example.com", PASSWORD);
    await submit(en.auth.log_in);
    expect(await screen.findByText("me@example.com")).toBeTruthy();
  });

  it("says when the email or password is wrong", async () => {
    const backend = fakeBackend();
    backend.addUser("me@example.com", PASSWORD);
    start("/login");
    await screen.findByRole("heading", { name: en.auth.log_in });

    fill("me@example.com", "not the password");
    await submit(en.auth.log_in);

    expect((await screen.findByRole("alert")).textContent).toBe(en.errors.invalid_credentials);
    expect(path()).toBe("/login");
  });

  it("asks for both fields before sending anything", async () => {
    const backend = fakeBackend();
    start("/login");
    await screen.findByRole("heading", { name: en.auth.log_in });

    await submit(en.auth.log_in);

    expect((await screen.findByRole("alert")).textContent).toBe(en.auth.validation.required);
    expect(backend.calls).toEqual(["GET /auth/me"]);
  });

  it("says when the backend can't be reached", async () => {
    const backend = fakeBackend();
    start("/login");
    await screen.findByRole("heading", { name: en.auth.log_in });
    backend.goDown();

    fill("me@example.com", PASSWORD);
    await submit(en.auth.log_in);

    expect((await screen.findByRole("alert")).textContent).toBe(en.errors.backend_unreachable);
  });

  it("switches the interface to the account's language", async () => {
    const backend = fakeBackend();
    backend.addUser("me@example.com", PASSWORD, "ar");
    start("/login");
    await screen.findByRole("heading", { name: en.auth.log_in });

    fill("me@example.com", PASSWORD);
    await submit(en.auth.log_in);

    expect(await screen.findByRole("button", { name: ar.auth.log_out })).toBeTruthy();
    expect(document.documentElement.dir).toBe("rtl");
  });
});

describe("signing up", () => {
  async function openSignUp() {
    const backend = fakeBackend();
    start("/signup");
    await screen.findByRole("heading", { name: en.auth.sign_up });
    return backend;
  }

  it("creates the account in the interface's language and logs in", async () => {
    await i18n.changeLanguage("fr");
    const backend = fakeBackend();
    start("/signup");
    await screen.findByRole("heading", { name: fr.auth.sign_up });

    fireEvent.change(screen.getByLabelText(fr.auth.email), {
      target: { value: "new@example.com" },
    });
    fireEvent.change(screen.getByLabelText(fr.auth.password), {
      target: { value: PASSWORD },
    });
    await submit(fr.auth.sign_up);

    expect(await screen.findByText("new@example.com")).toBeTruthy();
    expect(backend.loggedIn?.preferred_language).toBe("fr");
  });

  it("shows the privacy notice", async () => {
    await openSignUp();
    expect(screen.getByRole("heading", { name: en.privacy.title })).toBeTruthy();
    expect(screen.getByText(en.privacy.stored)).toBeTruthy();
    expect(screen.getByText(en.privacy.used)).toBeTruthy();
    expect(screen.getByText(en.privacy.deleted)).toBeTruthy();
  });

  it("checks the email and password before sending", async () => {
    const backend = await openSignUp();

    fill("not-an-email", PASSWORD);
    await submit(en.auth.sign_up);
    expect((await screen.findByRole("alert")).textContent).toBe(en.auth.validation.email_invalid);

    fill("new@example.com", "short");
    await submit(en.auth.sign_up);
    expect((await screen.findByRole("alert")).textContent).toBe(
      en.auth.validation.password_too_short,
    );
    expect(backend.calls).toEqual(["GET /auth/me"]);
  });

  it("says when the email already has an account", async () => {
    const backend = await openSignUp();
    backend.addUser("taken@example.com", PASSWORD);

    fill("taken@example.com", PASSWORD);
    await submit(en.auth.sign_up);

    expect((await screen.findByRole("alert")).textContent).toBe(en.errors.email_taken);
  });
});

describe("logging out", () => {
  it("logs out and goes to the login page", async () => {
    const backend = fakeBackend();
    backend.addUser("me@example.com", PASSWORD);
    backend.logIn("me@example.com");
    start("/");

    await submit(en.auth.log_out);

    expect(await screen.findByRole("heading", { name: en.auth.log_in })).toBeTruthy();
    expect(backend.loggedIn).toBeNull();
    expect(path()).toBe("/login");
  });
});

describe("the account's language", () => {
  it("saves a language change to the account while logged in", async () => {
    const backend = fakeBackend();
    backend.addUser("me@example.com", PASSWORD, "en");
    backend.logIn("me@example.com");
    start("/");
    await screen.findByText("me@example.com");

    fireEvent.change(screen.getByLabelText(en.language.label), {
      target: { value: "fr" },
    });

    await vi.waitFor(() => expect(backend.loggedIn?.preferred_language).toBe("fr"));
  });

  it("doesn't call the backend for a language change while logged out", async () => {
    const backend = fakeBackend();
    start("/login");
    await screen.findByRole("heading", { name: en.auth.log_in });

    fireEvent.change(screen.getByLabelText(en.language.label), {
      target: { value: "fr" },
    });

    expect(await screen.findByRole("heading", { name: fr.auth.log_in })).toBeTruthy();
    expect(backend.calls).toEqual(["GET /auth/me"]);
  });
});
