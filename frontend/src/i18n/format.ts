/**
 * Numbers and dates written the way the current language expects, using the browser's
 * built-in `Intl`. Always Western digits 0-9, also in Arabic (D-012): "-u-nu-latn" in
 * the locale tag means "numbering system: Latin digits".
 */
import type { Language } from "./languages";

function locale(language: Language): string {
  return `${language}-u-nu-latn`;
}

export function formatNumber(
  value: number,
  language: Language,
  options?: Intl.NumberFormatOptions,
): string {
  return new Intl.NumberFormat(locale(language), options).format(value);
}

export function formatDate(
  date: Date,
  language: Language,
  options: Intl.DateTimeFormatOptions = { dateStyle: "long" },
): string {
  return new Intl.DateTimeFormat(locale(language), options).format(date);
}
