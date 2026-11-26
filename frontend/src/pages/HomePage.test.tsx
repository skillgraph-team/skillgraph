/** Tests for the dashboard (M3.8): its four sections, and recent activity from the sources. */
import { render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "../App";
import ar from "../locales/ar.json";
import en from "../locales/en.json";
import { fakeBackend } from "../test/fakeBackend";

const EMAIL = "me@example.com";

afterEach(() => {
  vi.unstubAllGlobals();
});

function openDashboard(sources = 0, language: "en" | "ar" = "en") {
  const backend = fakeBackend();
  backend.addUser(EMAIL, "a long enough password", language);
  for (let i = 1; i <= sources; i++) {
    backend.addSource(EMAIL, {
      id: `s-${i}`,
      kind: "github_repo",
      title: `me/repo-${i}`,
      language: "en",
      url: `https://github.com/me/repo-${i}`,
      created_at: "2026-11-26T10:00:00Z",
    });
  }
  backend.logIn(EMAIL);
  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );
}

describe("the dashboard", () => {
  it("has the four sections", async () => {
    openDashboard();
    await screen.findByRole("heading", { name: en.dashboard.title });
    for (const name of ["skills", "opportunities", "gaps", "activity"] as const) {
      expect(screen.getByRole("region", { name: en.dashboard[name].title })).toBeTruthy();
    }
    expect(screen.getByText(en.dashboard.skills.placeholder)).toBeTruthy();
  });

  it("asks to add a source when there is none yet", async () => {
    openDashboard();
    const activity = within(
      await screen.findByRole("region", { name: en.dashboard.activity.title }),
    );
    const link = await activity.findByRole("link", { name: en.dashboard.activity.start });
    expect(link.getAttribute("href")).toBe("/sources");
  });

  it("shows the five latest sources", async () => {
    openDashboard(7);
    const activity = within(
      await screen.findByRole("region", { name: en.dashboard.activity.title }),
    );
    await activity.findByText("me/repo-7");
    expect(activity.getAllByRole("listitem")).toHaveLength(5);
    expect(activity.getByRole("link", { name: en.dashboard.activity.all })).toBeTruthy();
  });

  it("is in Arabic, right to left, when the account is", async () => {
    openDashboard(0, "ar");
    expect(await screen.findByRole("heading", { name: ar.dashboard.title })).toBeTruthy();
    expect(document.documentElement.dir).toBe("rtl");
  });
});
