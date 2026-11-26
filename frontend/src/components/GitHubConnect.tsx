/**
 * Connecting GitHub (D-009: a public username, no GitHub login).
 *
 * 1. Without consent: the consent text (what is read, that it's public data only, how to
 *    take it back) and an **Allow** button (`PUT /profile/github-consent`).
 * 2. With consent: a username field and **Import** (`POST /sources/github`), and
 *    **Withdraw consent**, which asks to confirm because it deletes every imported repo.
 */
import { type FormEvent, useEffect, useId, useState } from "react";
import { useTranslation } from "react-i18next";

import { type ErrorKey, errorKey } from "../api/errors";
import {
  type GitHubConsent,
  getGitHubConsent,
  giveGitHubConsent,
  importGitHub,
  withdrawGitHubConsent,
} from "../api/sources";

// GitHub's rule, as in backend/app/api/github.py: letters, digits, single hyphens inside.
const USERNAME = /^[A-Za-z0-9](?:-?[A-Za-z0-9])*$/;

type Result = ErrorKey | "sources.github.username_invalid" | { imported: number } | null;

interface Props {
  /** Called after anything that changes the list of sources. */
  onChanged(): void;
}

export function GitHubConnect({ onChanged }: Props) {
  const { t } = useTranslation();
  const id = useId();
  const [consent, setConsent] = useState<GitHubConsent | null>(null);
  const [username, setUsername] = useState("");
  const [result, setResult] = useState<Result>(null);
  const [busy, setBusy] = useState(false);
  const [confirming, setConfirming] = useState(false);

  useEffect(() => {
    let active = true;
    getGitHubConsent()
      .then((loaded) => {
        if (!active) return;
        setConsent(loaded);
        setUsername(loaded.github_username ?? "");
      })
      .catch((error: unknown) => active && setResult(errorKey(error)));
    return () => {
      active = false;
    };
  }, []);

  async function run(action: () => Promise<void>) {
    setBusy(true);
    setResult(null);
    try {
      await action();
    } catch (error) {
      setResult(errorKey(error));
    }
    setBusy(false);
  }

  const allow = () => run(async () => setConsent(await giveGitHubConsent()));

  const withdraw = () =>
    run(async () => {
      setConfirming(false);
      await withdrawGitHubConsent();
      setConsent({ consented_at: null, github_username: null });
      setUsername("");
      onChanged();
    });

  function submit(event: FormEvent) {
    event.preventDefault();
    const name = username.trim();
    if (name.length > 39 || !USERNAME.test(name)) {
      return setResult("sources.github.username_invalid");
    }
    void run(async () => {
      const repos = await importGitHub(name);
      setResult({ imported: repos.length });
      onChanged();
    });
  }

  const message =
    result === null ? null : typeof result === "string" ? (
      <p className="form-error" role="alert">
        {t(result)}
      </p>
    ) : (
      <p role="status">{t("sources.github.imported", { count: result.imported })}</p>
    );

  if (!consent) return message;

  if (!consent.consented_at) {
    return (
      <div className="entry-form">
        <div className="consent">
          <p>{t("sources.github.consent.what")}</p>
          <p>{t("sources.github.consent.public")}</p>
          <p>{t("sources.github.consent.withdraw")}</p>
        </div>
        {message}
        <div className="buttons">
          <button type="button" disabled={busy} onClick={() => void allow()}>
            {t("sources.github.consent.allow")}
          </button>
        </div>
      </div>
    );
  }

  return (
    <form className="entry-form" noValidate onSubmit={submit}>
      <div className="field">
        <label htmlFor={`${id}-username`}>{t("sources.github.username")}</label>
        <input
          id={`${id}-username`}
          dir="ltr"
          autoComplete="off"
          spellCheck={false}
          maxLength={39}
          value={username}
          onChange={(event) => setUsername(event.target.value)}
        />
      </div>
      {busy && <p role="status">{t("sources.github.importing")}</p>}
      {message}
      <div className="buttons">
        <button type="submit" disabled={busy}>
          {t("sources.github.import")}
        </button>
        {confirming ? (
          <span className="buttons" role="group" aria-label={t("sources.github.confirm_withdraw")}>
            <span>{t("sources.github.confirm_withdraw")}</span>
            <button type="button" onClick={() => void withdraw()}>
              {t("sources.github.withdraw_yes")}
            </button>
            <button type="button" onClick={() => setConfirming(false)}>
              {t("profile.cancel")}
            </button>
          </span>
        ) : (
          <button type="button" disabled={busy} onClick={() => setConfirming(true)}>
            {t("sources.github.withdraw")}
          </button>
        )}
      </div>
    </form>
  );
}
