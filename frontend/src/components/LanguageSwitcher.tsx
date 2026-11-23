/**
 * Language switcher: a drop-down with the three languages, each written in its own
 * language. Picking one changes every text at once; src/i18n saves the choice and
 * flips the page to right-to-left for Arabic.
 */
import { useTranslation } from "react-i18next";

import { LANGUAGES } from "../i18n/languages";

export function LanguageSwitcher() {
  const { t, i18n } = useTranslation();

  return (
    <label className="language-switcher">
      {t("language.label")}
      <select
        value={i18n.resolvedLanguage}
        onChange={(event) => void i18n.changeLanguage(event.target.value)}
      >
        {LANGUAGES.map(({ code, name }) => (
          // lang: screen readers pronounce each name in its own language.
          <option key={code} value={code} lang={code}>
            {name}
          </option>
        ))}
      </select>
    </label>
  );
}
