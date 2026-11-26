/**
 * One profile list (education, experience or projects): its entries, and buttons to add,
 * edit and delete them. One form is open at a time. Deleting asks to confirm on the spot.
 *
 * The section keeps no copy of the list: after each change it calls `onChange` with the
 * new list, and the profile page holds it.
 */
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { type ErrorKey, errorKey } from "../api/errors";
import { addEntry, deleteEntry, type Entry, type EntryValues, replaceEntry } from "../api/profile";
import { formatDate } from "../i18n/format";
import { DEFAULT_LANGUAGE, type Language, LANGUAGE_CODES } from "../i18n/languages";
import type { KindSpec } from "../profile/entryKinds";
import { EntryForm } from "./EntryForm";

interface Props {
  spec: KindSpec;
  entries: Entry[];
  onChange(entries: Entry[]): void;
}

/** "new", an entry's id, or null when no form is open. */
type Editing = "new" | string | null;

function text(entry: Entry, field: string | undefined): string | null {
  const value = field ? entry[field] : null;
  return typeof value === "string" ? value : null;
}

export function EntrySection({ spec, entries, onChange }: Props) {
  const { t, i18n } = useTranslation();
  const [editing, setEditing] = useState<Editing>(null);
  const [confirming, setConfirming] = useState<string | null>(null);
  const [failure, setFailure] = useState<ErrorKey | null>(null);
  const language: Language =
    LANGUAGE_CODES.find((code) => code === i18n.resolvedLanguage) ?? DEFAULT_LANGUAGE;
  const headingId = `section-${spec.kind}`;

  // "2024-09-01" → "September 2024". Read as UTC so no time zone can shift the day.
  const month = (iso: string | null) =>
    iso
      ? formatDate(new Date(`${iso}T00:00:00Z`), language, {
          month: "long",
          year: "numeric",
          timeZone: "UTC",
        })
      : null;

  async function save(values: EntryValues) {
    if (editing === "new") {
      onChange([...entries, await addEntry(spec.kind, values)]);
    } else if (editing) {
      const saved = await replaceEntry(spec.kind, editing, values);
      onChange(entries.map((entry) => (entry.id === saved.id ? saved : entry)));
    }
    setEditing(null);
  }

  async function remove(id: string) {
    setFailure(null);
    try {
      await deleteEntry(spec.kind, id);
      onChange(entries.filter((entry) => entry.id !== id));
    } catch (error) {
      setFailure(errorKey(error));
    }
    setConfirming(null);
  }

  function open(target: Editing) {
    setEditing(target);
    setConfirming(null);
    setFailure(null);
  }

  return (
    <section className="entry-section" aria-labelledby={headingId}>
      <h2 id={headingId}>{t(`profile.${spec.kind}.title`)}</h2>
      {entries.length === 0 && editing !== "new" && <p>{t(`profile.${spec.kind}.empty`)}</p>}
      <ul className="entries">
        {entries.map((entry) =>
          editing === entry.id ? (
            <li key={entry.id}>
              <EntryForm spec={spec} entry={entry} onSave={save} onCancel={() => open(null)} />
            </li>
          ) : (
            <li key={entry.id} className="entry">
              <div>
                <strong dir="auto">{text(entry, spec.titleField)}</strong>
                {text(entry, spec.subtitleField) && (
                  <span dir="auto"> · {text(entry, spec.subtitleField)}</span>
                )}
                {(entry.start_date || entry.end_date) && (
                  <div className="dates">
                    {month(text(entry, "start_date")) ?? "…"} –{" "}
                    {month(text(entry, "end_date")) ?? t("profile.present")}
                  </div>
                )}
              </div>
              {confirming === entry.id ? (
                <div className="buttons" role="group" aria-label={t("profile.confirm_delete")}>
                  <span>{t("profile.confirm_delete")}</span>
                  <button type="button" onClick={() => void remove(entry.id)}>
                    {t("profile.delete_yes")}
                  </button>
                  <button type="button" onClick={() => setConfirming(null)}>
                    {t("profile.cancel")}
                  </button>
                </div>
              ) : (
                <div className="buttons">
                  <button
                    type="button"
                    aria-label={t("profile.edit_named", { name: text(entry, spec.titleField) })}
                    onClick={() => open(entry.id)}
                  >
                    {t("profile.edit")}
                  </button>
                  <button
                    type="button"
                    aria-label={t("profile.delete_named", { name: text(entry, spec.titleField) })}
                    onClick={() => setConfirming(entry.id)}
                  >
                    {t("profile.delete")}
                  </button>
                </div>
              )}
            </li>
          ),
        )}
      </ul>
      {failure && (
        <p className="form-error" role="alert">
          {t(failure)}
        </p>
      )}
      {editing === "new" ? (
        <EntryForm spec={spec} entry={null} onSave={save} onCancel={() => open(null)} />
      ) : (
        <button type="button" onClick={() => open("new")}>
          {t(`profile.${spec.kind}.add`)}
        </button>
      )}
    </section>
  );
}
