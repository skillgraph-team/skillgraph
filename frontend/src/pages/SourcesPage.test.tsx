/**
 * Tests for the sources page (M3.7): CV upload (progress, success, errors), GitHub
 * consent and import, withdrawing consent, and the list with delete.
 * The app runs against the pretend backend; the upload itself (XMLHttpRequest) is
 * replaced per test, and tested on its own in api/sources.test.ts.
 */
import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "../App";
import { ApiError } from "../api/client";
import * as sourcesApi from "../api/sources";
import en from "../locales/en.json";
import { fakeBackend } from "../test/fakeBackend";

const EMAIL = "me@example.com";
const T = en.sources;

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

async function openSources() {
  const backend = fakeBackend();
  backend.addUser(EMAIL, "a long enough password");
  backend.logIn(EMAIL);
  render(
    <MemoryRouter initialEntries={["/sources"]}>
      <App />
    </MemoryRouter>,
  );
  await screen.findByRole("heading", { name: T.title });
  return backend;
}

const region = (name: string) => within(screen.getByRole("region", { name }));

function chooseFile(name = "cv.pdf") {
  const file = new File(["%PDF-1.7"], name, { type: "application/pdf" });
  fireEvent.change(region(T.cv.title).getByLabelText(T.cv.file), { target: { files: [file] } });
  return file;
}

describe("the CV upload", () => {
  it("shows the progress, then adds the CV to the list", async () => {
    const backend = await openSources();
    let report: (sent: number) => void = () => {};
    let finish: () => void = () => {};
    vi.spyOn(sourcesApi, "uploadCv").mockImplementation((_file, onProgress) => {
      report = onProgress ?? report;
      return new Promise((resolve) => (finish = resolve));
    });
    chooseFile();

    fireEvent.click(region(T.cv.title).getByRole("button", { name: T.cv.upload }));
    act(() => report(0.5));
    expect(region(T.cv.title).getByRole("progressbar").getAttribute("aria-valuetext")).toBe("50%");
    act(() => report(1));
    expect(region(T.cv.title).getByText(T.cv.reading)).toBeTruthy();

    backend.addSource(EMAIL, {
      id: "cv-1",
      kind: "cv",
      title: "cv.pdf",
      language: "fr",
      url: null,
      created_at: "2026-11-26T09:00:00Z",
    });
    await act(async () => finish());

    expect(await region(T.list.title).findByText("cv.pdf")).toBeTruthy();
    expect(region(T.list.title).getByText(/French/)).toBeTruthy();
    expect(region(T.cv.title).getByText(T.cv.done)).toBeTruthy();
  });

  it("asks for a file first", async () => {
    await openSources();
    const upload = vi.spyOn(sourcesApi, "uploadCv");

    fireEvent.click(region(T.cv.title).getByRole("button", { name: T.cv.upload }));

    expect(region(T.cv.title).getByRole("alert").textContent).toBe(T.cv.missing);
    expect(upload).not.toHaveBeenCalled();
  });

  it.each([
    ["no_text_found", en.errors.no_text_found],
    ["unsupported_file_type", en.errors.unsupported_file_type],
    ["file_too_large", en.errors.file_too_large],
  ])("explains the backend's %s", async (code, text) => {
    await openSources();
    vi.spyOn(sourcesApi, "uploadCv").mockRejectedValue(new ApiError(422, code));
    chooseFile();

    fireEvent.click(region(T.cv.title).getByRole("button", { name: T.cv.upload }));

    expect((await region(T.cv.title).findByRole("alert")).textContent).toBe(text);
  });
});

describe("GitHub", () => {
  it("shows the consent text first, then imports after consent", async () => {
    const backend = await openSources();
    const github = () => region(T.github.title);
    expect(await github().findByText(T.github.consent.what)).toBeTruthy();
    expect(github().getByText(T.github.consent.public)).toBeTruthy();
    expect(github().getByText(T.github.consent.withdraw)).toBeTruthy();
    expect(github().queryByLabelText(T.github.username)).toBeNull();

    fireEvent.click(github().getByRole("button", { name: T.github.consent.allow }));
    fireEvent.change(await github().findByLabelText(T.github.username), {
      target: { value: "test-student" },
    });
    fireEvent.click(github().getByRole("button", { name: T.github.import }));

    expect(await github().findByText("Repositories imported: 2.")).toBeTruthy();
    const link = await region(T.list.title).findByRole("link", { name: "test-student/shop-api" });
    expect(link.getAttribute("href")).toBe("https://github.com/test-student/shop-api");
    expect(backend.sources(EMAIL)).toHaveLength(2);
  });

  it("checks the username before asking GitHub", async () => {
    const backend = await openSources();
    const github = () => region(T.github.title);
    fireEvent.click(await github().findByRole("button", { name: T.github.consent.allow }));
    fireEvent.change(await github().findByLabelText(T.github.username), {
      target: { value: "not a name" },
    });

    fireEvent.click(github().getByRole("button", { name: T.github.import }));

    expect(github().getByRole("alert").textContent).toBe(T.github.username_invalid);
    expect(backend.calls).not.toContain("POST /sources/github");
  });

  it("says when the GitHub user doesn't exist", async () => {
    await openSources();
    const github = () => region(T.github.title);
    fireEvent.click(await github().findByRole("button", { name: T.github.consent.allow }));
    fireEvent.change(await github().findByLabelText(T.github.username), {
      target: { value: "nobody-here" },
    });

    fireEvent.click(github().getByRole("button", { name: T.github.import }));

    expect((await github().findByRole("alert")).textContent).toBe(en.errors.github_user_not_found);
  });

  it("withdrawing consent, after confirming, removes the repos", async () => {
    const backend = await openSources();
    const github = () => region(T.github.title);
    fireEvent.click(await github().findByRole("button", { name: T.github.consent.allow }));
    fireEvent.change(await github().findByLabelText(T.github.username), {
      target: { value: "test-student" },
    });
    fireEvent.click(github().getByRole("button", { name: T.github.import }));
    await region(T.list.title).findByText("test-student/notes");

    fireEvent.click(github().getByRole("button", { name: T.github.withdraw }));
    fireEvent.click(github().getByRole("button", { name: T.github.withdraw_yes }));

    expect(await github().findByText(T.github.consent.what)).toBeTruthy();
    expect(await region(T.list.title).findByText(T.list.empty)).toBeTruthy();
    expect(backend.sources(EMAIL)).toEqual([]);
  });
});

describe("the list", () => {
  it("deletes a source after confirming", async () => {
    const backend = fakeBackend();
    backend.addUser(EMAIL, "a long enough password");
    backend.addSource(EMAIL, {
      id: "cv-1",
      kind: "cv",
      title: "old-cv.docx",
      language: "en",
      url: null,
      created_at: "2026-11-20T09:00:00Z",
    });
    backend.logIn(EMAIL);
    render(
      <MemoryRouter initialEntries={["/sources"]}>
        <App />
      </MemoryRouter>,
    );
    await screen.findByRole("heading", { name: T.title });
    const list = () => region(T.list.title);
    await list().findByText("old-cv.docx");

    fireEvent.click(list().getByRole("button", { name: "Delete old-cv.docx" }));
    fireEvent.click(list().getByRole("button", { name: en.profile.delete_yes }));

    expect(await list().findByText(T.list.empty)).toBeTruthy();
    expect(backend.sources(EMAIL)).toEqual([]);
  });
});
