/**
 * What's wrong with a form field, as a translation key `profile.problems.<problem>`.
 *
 * `checkEntry` runs the backend's rules (entryKinds.ts) before sending, so most mistakes
 * show without a round trip. `problemsFromApi` turns the backend's 422 answer into the
 * same keys, for anything the first check missed.
 */
import { ApiError } from "../api/client";
import type { EntryValues } from "../api/profile";
import { type KindSpec, MAX_LENGTH } from "./entryKinds";

export type Problem = "required" | "too_long" | "url" | "date" | "end_before_start" | "invalid";
export type ProblemKey = `profile.problems.${Problem}`;

/** Field name → problem key. The empty name `""` is a problem with the whole entry. */
export type Problems = Record<string, ProblemKey>;

const URL = /^https?:\/\/\S+$/;

export function checkEntry(spec: KindSpec, values: EntryValues): Problems {
  const problems: Problems = {};
  for (const field of spec.fields) {
    const value = values[field.name] ?? "";
    if (!value.trim()) {
      if (field.required) problems[field.name] = "profile.problems.required";
    } else if (value.length > MAX_LENGTH[field.type]) {
      problems[field.name] = "profile.problems.too_long";
    } else if (field.type === "url" && !URL.test(value)) {
      problems[field.name] = "profile.problems.url";
    }
  }
  const start = values.start_date;
  const end = values.end_date;
  // ISO dates (yyyy-mm-dd) compare correctly as text.
  if (start && end && end < start) problems.end_date = "profile.problems.end_before_start";
  return problems;
}

/** FastAPI error types (pydantic) → our problems. */
function problemOf(type: string): Problem {
  if (type === "missing" || type === "string_too_short") return "required";
  if (type === "string_too_long") return "too_long";
  if (type === "string_pattern_mismatch") return "url";
  if (type.startsWith("date")) return "date";
  return "invalid";
}

/** The backend's field errors, or null when the error isn't about the fields. */
export function problemsFromApi(error: unknown): Problems | null {
  if (!(error instanceof ApiError) || error.code !== "invalid_input") return null;
  const problems: Problems = {};
  for (const [field, type] of Object.entries(error.fields)) {
    // The date check runs on the whole body, so the backend can't name the field.
    problems[field] =
      field === "" && type === "value_error"
        ? "profile.problems.end_before_start"
        : `profile.problems.${problemOf(type)}`;
  }
  return problems;
}
