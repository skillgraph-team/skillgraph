/** Tests for where the login page may send someone afterwards: only inside this app. */
import { describe, expect, it } from "vitest";

import { safeReturnPath } from "./returnPath";

describe("safeReturnPath", () => {
  it("keeps a path inside the app", () => {
    expect(safeReturnPath({ from: "/profile?tab=skills" })).toBe("/profile?tab=skills");
  });

  it("goes home for anything else", () => {
    expect(safeReturnPath(null)).toBe("/");
    expect(safeReturnPath({})).toBe("/");
    expect(safeReturnPath({ from: "//evil.example" })).toBe("/");
    expect(safeReturnPath({ from: "https://evil.example" })).toBe("/");
    expect(safeReturnPath({ from: 42 })).toBe("/");
  });
});
