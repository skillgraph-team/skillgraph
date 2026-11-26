/**
 * The list of the user's sources (CVs and GitHub repos), newest first, each with its
 * kind, detected language and date, and a delete button that asks to confirm.
 * Repo titles link to the repo on GitHub.
 */
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { type ErrorKey, errorKey } from "../api/errors";
import { deleteSource, type SourceSummary } from "../api/sources";
import { formatDate } from "../i18n/format";
import { DEFAULT_LANGUAGE, LANGUAGE_CODES } from "../i18n/languages";

interface Props {
  sources: SourceSummary[];
  onDeleted(id: string): void;
}

export function SourceList({ sources, onDeleted }: Props) {
  const { t, i18n } = useTranslation();
  const [confirming, setConfirming] = useState<string | null>(null);
  const [failure, setFailure] = useState<ErrorKey | null>(null);
  const language =
    LANGUAGE_CODES.find((code) => code === i18n.resolvedLanguage) ?? DEFAULT_LANGUAGE;

  async function remove(id: string) {
    setFailure(null);
    try {
      await deleteSource(id);
      onDeleted(id);
    } catch (error) {
      setFailure(errorKey(error));
    }
    setConfirming(null);
  }

  if (sources.length === 0) return <p>{t("sources.list.empty")}</p>;

  return (
    <>
      <ul className="entries">
        {sources.map((source) => (
          <li key={source.id} className="entry">
            <div>
              {source.url ? (
                <a href={source.url} target="_blank" rel="noreferrer" dir="ltr">
                  {source.title}
                </a>
              ) : (
                <strong dir="auto">{source.title}</strong>
              )}
              <div className="dates">
                {t(`sources.kind.${source.kind}`)}
                {source.language && ` · ${t(`sources.language.${source.language}`)}`}
                {" · "}
                {formatDate(new Date(source.created_at), language, { dateStyle: "medium" })}
              </div>
            </div>
            {confirming === source.id ? (
              <div className="buttons" role="group" aria-label={t("sources.list.confirm_delete")}>
                <span>{t("sources.list.confirm_delete")}</span>
                <button type="button" onClick={() => void remove(source.id)}>
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
                  aria-label={t("profile.delete_named", { name: source.title })}
                  onClick={() => setConfirming(source.id)}
                >
                  {t("profile.delete")}
                </button>
              </div>
            )}
          </li>
        ))}
      </ul>
      {failure && (
        <p className="form-error" role="alert">
          {t(failure)}
        </p>
      )}
    </>
  );
}
