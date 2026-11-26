/**
 * Sources page (/sources, logged-in users only): upload a CV, connect GitHub, and see
 * the list of sources. The list reloads after every upload or import.
 */
import { useCallback, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { type ErrorKey, errorKey } from "../api/errors";
import { listSources, type SourceSummary } from "../api/sources";
import { CvUpload } from "../components/CvUpload";
import { GitHubConnect } from "../components/GitHubConnect";
import { SourceList } from "../components/SourceList";

export function SourcesPage() {
  const { t } = useTranslation();
  const [sources, setSources] = useState<SourceSummary[] | null>(null);
  const [failure, setFailure] = useState<ErrorKey | null>(null);

  const reload = useCallback(() => {
    listSources()
      .then((loaded) => {
        setSources(loaded);
        setFailure(null);
      })
      .catch((error: unknown) => setFailure(errorKey(error)));
  }, []);

  useEffect(reload, [reload]);

  return (
    <main className="profile-page">
      <h1>{t("sources.title")}</h1>
      <section className="entry-section" aria-labelledby="section-cv">
        <h2 id="section-cv">{t("sources.cv.title")}</h2>
        <CvUpload onUploaded={reload} />
      </section>
      <section className="entry-section" aria-labelledby="section-github">
        <h2 id="section-github">{t("sources.github.title")}</h2>
        <GitHubConnect onChanged={reload} />
      </section>
      <section className="entry-section" aria-labelledby="section-list">
        <h2 id="section-list">{t("sources.list.title")}</h2>
        {failure && (
          <p className="form-error" role="alert">
            {t(failure)}
          </p>
        )}
        {!sources && !failure && <p role="status">{t("sources.list.loading")}</p>}
        {sources && (
          <SourceList
            sources={sources}
            onDeleted={(id) => setSources(sources.filter((source) => source.id !== id))}
          />
        )}
      </section>
    </main>
  );
}
