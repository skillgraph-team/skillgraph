/** Tests for number and date formatting: right conventions, always Western digits (D-012). */
import { describe, expect, it } from "vitest";

import { formatDate, formatNumber } from "./format";

const DATE = new Date(Date.UTC(2026, 10, 23, 12));

describe("formatNumber", () => {
  it("uses each language's separators", () => {
    expect(formatNumber(1234.5, "en")).toBe("1,234.5");
    expect(formatNumber(1234.5, "fr")).toMatch(/^1\s234,5$/u);
  });

  it("uses Western digits in Arabic", () => {
    const text = formatNumber(1234.5, "ar");
    expect(text).toContain("234");
    expect(text).not.toMatch(/[\u0660-\u0669]/u); // no Arabic-Indic digits ٠-٩
  });
});

describe("formatDate", () => {
  it("writes the month in the current language", () => {
    expect(formatDate(DATE, "en")).toContain("November");
    expect(formatDate(DATE, "fr")).toContain("novembre");
  });

  it("uses Western digits in Arabic", () => {
    const text = formatDate(DATE, "ar");
    expect(text).toContain("2026");
    expect(text).not.toMatch(/[\u0660-\u0669]/u); // no Arabic-Indic digits ٠-٩
  });
});
