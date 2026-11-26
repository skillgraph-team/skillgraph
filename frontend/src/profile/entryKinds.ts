/**
 * The fields of each profile list, as the backend defines them (backend/app/api/
 * education.py, experience.py, projects.py). EntrySection and EntryForm build their
 * screens from this, so adding a field to a kind is one line here plus its label.
 *
 * - `type`: "short" (one line, up to 200), "long" (several lines, up to 5000), "date",
 *   or "url" (must start with http:// or https://).
 * - `required`: the backend refuses the entry without it.
 * - Labels are the translation keys `profile.fields.<name>`.
 */
import type { EntryKind } from "../api/profile";
import type en from "../locales/en.json";

export type FieldType = "short" | "long" | "date" | "url";

/** A field name that has a label in the locale files. */
export type FieldName = keyof typeof en.profile.fields;

export interface FieldSpec {
  name: FieldName;
  type: FieldType;
  required?: boolean;
}

export interface KindSpec {
  kind: EntryKind;
  fields: FieldSpec[];
  /** The field shown as the entry's title in the list. */
  titleField: FieldName;
  /** Shown after the title, when filled in. */
  subtitleField?: FieldName;
}

export const MAX_LENGTH: Record<FieldType, number> = {
  short: 200,
  long: 5000,
  date: 10,
  url: 2048,
};

export const ENTRY_KINDS: KindSpec[] = [
  {
    kind: "education",
    titleField: "institution",
    subtitleField: "degree",
    fields: [
      { name: "institution", type: "short", required: true },
      { name: "degree", type: "short" },
      { name: "field_of_study", type: "short" },
      { name: "start_date", type: "date" },
      { name: "end_date", type: "date" },
      { name: "description", type: "long" },
    ],
  },
  {
    kind: "experience",
    titleField: "organization",
    subtitleField: "role",
    fields: [
      { name: "organization", type: "short", required: true },
      { name: "role", type: "short" },
      { name: "start_date", type: "date" },
      { name: "end_date", type: "date" },
      { name: "description", type: "long" },
    ],
  },
  {
    kind: "projects",
    titleField: "title",
    fields: [
      { name: "title", type: "short", required: true },
      { name: "description", type: "long", required: true },
      { name: "url", type: "url" },
    ],
  },
];
