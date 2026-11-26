/**
 * The profile and its three lists (backend/app/api/profile.py, education.py,
 * experience.py, projects.py), and changing the password (auth.py).
 *
 * Each list has the same four calls; `kind` picks which: "education", "experience" or
 * "projects". Bodies are plain objects of field values; the fields of each kind are in
 * src/profile/entryKinds.ts.
 */
import { request } from "./client";

export type EntryKind = "education" | "experience" | "projects";

/** A saved entry: its id, its place in the list, and its fields (null = left empty). */
export interface Entry {
  id: string;
  position: number;
  [field: string]: string | number | null;
}

/** What a form sends: every field of the kind, null for an empty one. */
export type EntryValues = Record<string, string | null>;

export interface Profile {
  display_name: string | null;
  headline: string | null;
  preferred_language: string;
  education: Entry[];
  experience: Entry[];
  projects: Entry[];
}

export function getProfile(): Promise<Profile> {
  return request<Profile>("GET", "/profile");
}

/** Changes only the fields sent; null empties one. */
export function updateProfile(fields: {
  display_name: string | null;
  headline: string | null;
}): Promise<Profile> {
  return request<Profile>("PATCH", "/profile", fields);
}

export function addEntry(kind: EntryKind, values: EntryValues): Promise<Entry> {
  return request<Entry>("POST", `/profile/${kind}`, values);
}

/** Replaces every field; the entry keeps its place in the list. */
export function replaceEntry(kind: EntryKind, id: string, values: EntryValues): Promise<Entry> {
  return request<Entry>("PUT", `/profile/${kind}/${encodeURIComponent(id)}`, values);
}

export function deleteEntry(kind: EntryKind, id: string): Promise<void> {
  return request<void>("DELETE", `/profile/${kind}/${encodeURIComponent(id)}`);
}

/** 204 on success; a wrong current password is ApiError 403 `wrong_password`. */
export function changePassword(currentPassword: string, newPassword: string): Promise<void> {
  return request<void>("POST", "/auth/password", {
    current_password: currentPassword,
    new_password: newPassword,
  });
}
