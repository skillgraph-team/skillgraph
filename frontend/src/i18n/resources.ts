/**
 * The translation files, and the check that they all have the same keys.
 *
 * en.json is the source. `satisfies` makes `npm run check` (tsc) fail when fr.json or
 * ar.json misses a key from en.json, and the second pair of checks fails when they have a
 * key en.json doesn't. The error names the missing key.
 */
import ar from "../locales/ar.json";
import en from "../locales/en.json";
import fr from "../locales/fr.json";

export type Messages = typeof en;

export const resources = {
  en: { translation: en },
  fr: { translation: fr satisfies Messages },
  ar: { translation: ar satisfies Messages },
};

// The other direction: no extra keys in fr.json or ar.json that en.json doesn't have.
en satisfies typeof fr;
en satisfies typeof ar;
