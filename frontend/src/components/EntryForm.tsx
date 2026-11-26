/**
 * The form to add or edit one profile entry, built from its kind's fields
 * (src/profile/entryKinds.ts).
 *
 * Mistakes show under their field, from our own check first and from the backend's 422
 * answer otherwise (src/profile/fieldProblems.ts). Any other error (backend down, entry
 * deleted elsewhere) shows above the buttons. Text the user typed is shown with
 * `dir="auto"`, so a French entry in the Arabic interface still reads left to right.
 */
import { type FormEvent, useId, useState } from "react";
import { useTranslation } from "react-i18next";

import { type ErrorKey, errorKey } from "../api/errors";
import type { Entry, EntryValues } from "../api/profile";
import { type FieldSpec, type KindSpec, MAX_LENGTH } from "../profile/entryKinds";
import { checkEntry, problemsFromApi, type Problems } from "../profile/fieldProblems";

interface Props {
  spec: KindSpec;
  /** The entry being edited, or null to add a new one. */
  entry: Entry | null;
  onSave(values: EntryValues): Promise<void>;
  onCancel(): void;
}

function startValues(spec: KindSpec, entry: Entry | null): Record<string, string> {
  return Object.fromEntries(
    spec.fields.map(({ name }) => {
      const value = entry?.[name];
      return [name, typeof value === "string" ? value : ""];
    }),
  );
}

export function EntryForm({ spec, entry, onSave, onCancel }: Props) {
  const { t } = useTranslation();
  const id = useId();
  const [values, setValues] = useState(() => startValues(spec, entry));
  const [problems, setProblems] = useState<Problems>({});
  const [failure, setFailure] = useState<ErrorKey | null>(null);
  const [sending, setSending] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    const body: EntryValues = Object.fromEntries(
      Object.entries(values).map(([name, value]) => [name, value.trim() ? value : null]),
    );
    const found = checkEntry(spec, body);
    setProblems(found);
    setFailure(null);
    if (Object.keys(found).length > 0) return;
    setSending(true);
    try {
      await onSave(body);
    } catch (error) {
      const fromApi = problemsFromApi(error);
      if (fromApi) setProblems(fromApi);
      else setFailure(errorKey(error));
      setSending(false);
    }
  }

  function input(field: FieldSpec) {
    const inputId = `${id}-${field.name}`;
    const problem = problems[field.name];
    const common = {
      id: inputId,
      value: values[field.name] ?? "",
      "aria-invalid": problem ? true : undefined,
      "aria-describedby": problem ? `${inputId}-problem` : undefined,
      onChange: (event: { target: { value: string } }) =>
        setValues((old) => ({ ...old, [field.name]: event.target.value })),
    };
    return (
      <div className="field" key={field.name}>
        <label htmlFor={inputId}>
          {t(`profile.fields.${field.name}`)}
          {field.required && <span aria-hidden="true"> *</span>}
        </label>
        {field.type === "long" ? (
          <textarea {...common} dir="auto" rows={4} maxLength={MAX_LENGTH.long} />
        ) : field.type === "date" ? (
          <input {...common} type="date" />
        ) : field.type === "url" ? (
          <input {...common} type="url" dir="ltr" maxLength={MAX_LENGTH.url} />
        ) : (
          <input {...common} type="text" dir="auto" maxLength={MAX_LENGTH.short} />
        )}
        {problem && (
          <p id={`${inputId}-problem`} className="form-error">
            {t(problem)}
          </p>
        )}
      </div>
    );
  }

  const formProblem = problems[""];
  return (
    <form className="entry-form" noValidate onSubmit={(event) => void submit(event)}>
      {spec.fields.map(input)}
      {(formProblem || failure) && (
        <p className="form-error" role="alert">
          {t(formProblem ?? failure ?? "errors.unknown")}
        </p>
      )}
      <div className="buttons">
        <button type="submit" disabled={sending}>
          {t("profile.save")}
        </button>
        <button type="button" onClick={onCancel}>
          {t("profile.cancel")}
        </button>
      </div>
    </form>
  );
}
