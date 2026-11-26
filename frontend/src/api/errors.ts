/**
 * Turns any error from an API call into the translation key of its message.
 *
 * Backend codes map to `errors.<code>` by name (docs/design/localization.md §4). A code
 * the locale files don't know yet shows `errors.unknown` rather than a raw code.
 */
import en from "../locales/en.json";
import { ApiError, BackendUnreachableError } from "./client";

export type ErrorKey = `errors.${keyof typeof en.errors}`;

function isKnown(code: string): code is keyof typeof en.errors {
  return Object.hasOwn(en.errors, code);
}

export function errorKey(error: unknown): ErrorKey {
  if (error instanceof BackendUnreachableError) return "errors.backend_unreachable";
  if (error instanceof ApiError && isKnown(error.code)) return `errors.${error.code}`;
  return "errors.unknown";
}
