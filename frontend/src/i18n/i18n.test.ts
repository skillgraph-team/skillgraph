/** Tests for the translation setup: page language and direction, fallback, remembered choice. */
import { describe, expect, it } from "vitest";

import { createI18n, i18n, STORAGE_KEY } from ".";

describe("i18n", () => {
  it("sets lang and dir on the page for each language", async () => {
    await i18n.changeLanguage("ar");
    expect(document.documentElement.lang).toBe("ar");
    expect(document.documentElement.dir).toBe("rtl");

    await i18n.changeLanguage("fr");
    expect(document.documentElement.lang).toBe("fr");
    expect(document.documentElement.dir).toBe("ltr");
  });

  it("remembers the chosen language", async () => {
    await i18n.changeLanguage("fr");
    expect(localStorage.getItem(STORAGE_KEY)).toBe("fr");
  });

  it("uses the saved language on the next visit", () => {
    localStorage.setItem(STORAGE_KEY, "ar");
    const fresh = createI18n();
    expect(fresh.resolvedLanguage).toBe("ar");
  });

  it("uses the browser language on a first visit when it is one of the three", () => {
    const fresh = createI18n({ browserLanguages: ["fr-CA", "en"] });
    expect(fresh.resolvedLanguage).toBe("fr");
  });

  it("falls back to English for any other browser language", () => {
    const fresh = createI18n({ browserLanguages: ["de-DE"] });
    expect(fresh.resolvedLanguage).toBe("en");
  });
});
