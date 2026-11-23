/** Tests for the language switcher: picking a language changes the text and the direction. */
import { act, fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { LanguageSwitcher } from "./LanguageSwitcher";

describe("LanguageSwitcher", () => {
  it("offers the three languages, written in their own language", () => {
    render(<LanguageSwitcher />);
    const options = screen.getAllByRole("option").map((o) => o.getAttribute("value"));
    expect(options).toEqual(["en", "fr", "ar"]);
    expect(screen.getByRole("option", { name: "العربية" })).toBeTruthy();
  });

  it("switches the page to Arabic, right-to-left", async () => {
    render(<LanguageSwitcher />);
    await act(async () => {
      fireEvent.change(screen.getByRole("combobox"), { target: { value: "ar" } });
    });
    expect(document.documentElement.dir).toBe("rtl");
    expect((screen.getByRole("combobox") as HTMLSelectElement).value).toBe("ar");
  });
});
