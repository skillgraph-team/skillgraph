/**
 * The three interface languages (D-012), in the order the switcher shows them.
 *
 * Each name is written in its own language ("Français", not "French"), the usual
 * convention for a language switcher, so it is the same in every translation and is
 * kept here rather than in the locale files.
 */
export const LANGUAGES = [
  { code: "en", name: "English" },
  { code: "fr", name: "Français" },
  { code: "ar", name: "العربية" },
] as const;

export type Language = (typeof LANGUAGES)[number]["code"];

export const LANGUAGE_CODES: Language[] = LANGUAGES.map((l) => l.code);

/** The source language, and the fallback for a missing translation or another browser language. */
export const DEFAULT_LANGUAGE: Language = "en";
