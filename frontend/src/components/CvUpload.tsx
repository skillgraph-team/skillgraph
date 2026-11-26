/**
 * Uploading a CV (PDF or Word .docx). Shows how much is sent, then "reading" while the
 * backend extracts the text, then done or the error (too large, wrong type, scanned...).
 */
import { type FormEvent, useId, useState } from "react";
import { useTranslation } from "react-i18next";

import { type ErrorKey, errorKey } from "../api/errors";
import { uploadCv } from "../api/sources";

type Stage = { name: "idle" } | { name: "sending"; sent: number } | { name: "reading" };

interface Props {
  onUploaded(): void;
}

export function CvUpload({ onUploaded }: Props) {
  const { t } = useTranslation();
  const id = useId();
  const [file, setFile] = useState<File | null>(null);
  const [stage, setStage] = useState<Stage>({ name: "idle" });
  const [result, setResult] = useState<ErrorKey | "sources.cv.missing" | "done" | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    // Kept now: React empties `event.currentTarget` once the handler awaits.
    const form = event.currentTarget;
    if (!file) return setResult("sources.cv.missing");
    setResult(null);
    setStage({ name: "sending", sent: 0 });
    try {
      await uploadCv(file, (sent) =>
        setStage(sent >= 1 ? { name: "reading" } : { name: "sending", sent }),
      );
      setResult("done");
      setFile(null);
      form.reset();
      onUploaded();
    } catch (error) {
      setResult(errorKey(error));
    }
    setStage({ name: "idle" });
  }

  const busy = stage.name !== "idle";
  return (
    <form className="entry-form" noValidate onSubmit={(event) => void submit(event)}>
      <div className="field">
        <label htmlFor={`${id}-file`}>{t("sources.cv.file")}</label>
        <input
          id={`${id}-file`}
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          aria-describedby={`${id}-hint`}
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
        />
        <p id={`${id}-hint`} className="hint">
          {t("sources.cv.hint")}
        </p>
      </div>
      {stage.name === "sending" && (
        <progress
          max={1}
          value={stage.sent}
          aria-label={t("sources.cv.sending")}
          aria-valuetext={`${Math.round(stage.sent * 100)}%`}
        />
      )}
      {stage.name === "reading" && <p role="status">{t("sources.cv.reading")}</p>}
      {result === "done" && <p role="status">{t("sources.cv.done")}</p>}
      {result && result !== "done" && (
        <p className="form-error" role="alert">
          {t(result)}
        </p>
      )}
      <div className="buttons">
        <button type="submit" disabled={busy}>
          {t("sources.cv.upload")}
        </button>
      </div>
    </form>
  );
}
