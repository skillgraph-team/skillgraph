/**
 * The dashboard (/), the first page after logging in (M3.8).
 *
 * Four sections, in a grid that becomes one column on a narrow screen:
 * - Skills, Opportunities, Gaps: placeholders until M4 (skills), M5 (opportunities and
 *   matching) and M7 (gaps) fill them in;
 * - Recent activity: the latest sources added (`GET /sources`), or a prompt to add a CV
 *   or GitHub when there are none yet.
 * Each later milestone replaces its placeholder with a component; the layout stays.
 */
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router";

import { type ErrorKey, errorKey } from "../api/errors";
import { listSources, type SourceSummary } from "../api/sources";
import { useAuth } from "../auth/context";
import { formatDate } from "../i18n/format";
import { DEFAULT_LANGUAGE, LANGUAGE_CODES } from "../i18n/languages";

const RECENT = 5;

const PLACEHOLDERS = ["skills", "opportunities", "gaps"] as const;

function RecentActivity() {
  const { t, i18n } = useTranslation();
  const [sources, setSources] = useState<SourceSummary[] | null>(null);
  const [failure, setFailure] = useState<ErrorKey | null>(null);
  const language =
    LANGUAGE_CODES.find((code) => code === i18n.resolvedLanguage) ?? DEFAULT_LANGUAGE;

  useEffect(() => {
    let active = true;
    listSources()
      .then((loaded) => active && setSources(loaded.slice(0, RECENT)))
      .catch((error: unknown) => active && setFailure(errorKey(error)));
    return () => {
      active = false;
    };
  }, []);

  if (failure) {
    return (
      <p className="form-error" role="alert">
        {t(failure)}
      </p>
    );
  }
  if (!sources) return <p role="status">{t("sources.list.loading")}</p>;
  if (sources.length === 0) {
    return (
      <p>
        {t("dashboard.activity.empty")} <Link to="/sources">{t("dashboard.activity.start")}</Link>
      </p>
    );
  }
  return (
    <>
      <ul className="entries">
        {sources.map((source) => (
          <li key={source.id} className="entry">
            <span dir="auto">{source.title}</span>
            <span className="dates">
              {t(`sources.kind.${source.kind}`)} ·{" "}
              {formatDate(new Date(source.created_at), language, { dateStyle: "medium" })}
            </span>
          </li>
        ))}
      </ul>
      <p>
        <Link to="/sources">{t("dashboard.activity.all")}</Link>
      </p>
    </>
  );
}

export function HomePage() {
  const { t } = useTranslation();
  const { state } = useAuth();
  const email = state.status === "logged-in" ? state.user.email : "";

  return (
    <main className="dashboard">
      <h1>{t("dashboard.title")}</h1>
      <p>
        {/* <bdi>: a Latin email inside an Arabic sentence keeps its own direction. */}
        {t("home.logged_in_as")} <bdi>{email}</bdi>
      </p>
      <div className="dashboard-grid">
        {PLACEHOLDERS.map((name) => (
          <section key={name} className="card" aria-labelledby={`dash-${name}`}>
            <h2 id={`dash-${name}`}>{t(`dashboard.${name}.title`)}</h2>
            <p>{t(`dashboard.${name}.placeholder`)}</p>
          </section>
        ))}
        <section className="card" aria-labelledby="dash-activity">
          <h2 id="dash-activity">{t("dashboard.activity.title")}</h2>
          <RecentActivity />
        </section>
      </div>
    </main>
  );
}
