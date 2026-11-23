/**
 * Translations for the whole app (i18next + react-i18next, T-033).
 *
 * How the language is chosen (D-012):
 * 1. the language saved in this browser (localStorage key STORAGE_KEY), if any;
 * 2. otherwise the browser's language, if it is en, fr or ar ("fr-CA" counts as "fr");
 * 3. otherwise English.
 * Every change is saved, and sets `lang` and `dir` on <html>, so Arabic is right-to-left.
 *
 * Use it in a component with `const { t } = useTranslation();` and `t("health.ok")`.
 */
import i18next, { type i18n as I18n } from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";

import { DEFAULT_LANGUAGE, LANGUAGE_CODES } from "./languages";
import { resources } from "./resources";

export const STORAGE_KEY = "skillgraph.language";

interface Options {
  /** Connect to React and keep <html lang dir> in sync. Only the app's own instance does. */
  connectToPage?: boolean;
  /** Tests only: pretend the browser prefers these languages. */
  browserLanguages?: readonly string[];
}

export function createI18n({ connectToPage = false, browserLanguages }: Options = {}): I18n {
  const instance = i18next.createInstance();

  const detector = new LanguageDetector();
  if (browserLanguages) {
    detector.addDetector({ name: "testBrowser", lookup: () => [...browserLanguages] });
  }
  instance.use(detector);

  if (connectToPage) {
    instance.use(initReactI18next);
    instance.on("languageChanged", () => {
      const language = instance.resolvedLanguage ?? DEFAULT_LANGUAGE;
      document.documentElement.lang = language;
      document.documentElement.dir = instance.dir(language);
    });
  }

  void instance.init({
    resources,
    supportedLngs: LANGUAGE_CODES,
    fallbackLng: DEFAULT_LANGUAGE,
    // The texts are bundled, so start right away instead of waiting a tick.
    initAsync: false,
    // React already escapes text it puts on the page.
    interpolation: { escapeValue: false },
    detection: {
      order: ["localStorage", browserLanguages ? "testBrowser" : "navigator"],
      lookupLocalStorage: STORAGE_KEY,
      caches: ["localStorage"],
      convertDetectedLanguage: (language: string) => language.split("-")[0] ?? language,
    },
  });
  return instance;
}

/** The app's translations. */
export const i18n = createI18n({ connectToPage: true });
