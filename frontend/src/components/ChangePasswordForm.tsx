/**
 * Changing the password (`POST /auth/password`, M3.10). The user stays logged in.
 *
 * A wrong current password is a 403 `wrong_password` (T-105), shown like any other
 * error. The new password follows the sign-up rules, checked here first (T-069).
 */
import { type FormEvent, useId, useState } from "react";
import { useTranslation } from "react-i18next";

import { type ErrorKey, errorKey } from "../api/errors";
import { changePassword } from "../api/profile";
import { PASSWORD_MAX, PASSWORD_MIN } from "./AuthForm";

type Result =
  | ErrorKey
  | "auth.validation.required"
  | "auth.validation.password_too_short"
  | "auth.validation.password_too_long"
  | "saved";

export function ChangePasswordForm() {
  const { t } = useTranslation();
  const id = useId();
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [sending, setSending] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!current || !next) return setResult("auth.validation.required");
    if (next.length < PASSWORD_MIN) return setResult("auth.validation.password_too_short");
    if (next.length > PASSWORD_MAX) return setResult("auth.validation.password_too_long");
    setSending(true);
    setResult(null);
    try {
      await changePassword(current, next);
      setCurrent("");
      setNext("");
      setResult("saved");
    } catch (error) {
      setResult(errorKey(error));
    }
    setSending(false);
  }

  return (
    <form className="entry-form" noValidate onSubmit={(event) => void submit(event)}>
      <div className="field">
        <label htmlFor={`${id}-current`}>{t("password.current")}</label>
        <input
          id={`${id}-current`}
          type="password"
          dir="ltr"
          autoComplete="current-password"
          value={current}
          onChange={(event) => setCurrent(event.target.value)}
        />
      </div>
      <div className="field">
        <label htmlFor={`${id}-new`}>{t("password.new")}</label>
        <input
          id={`${id}-new`}
          type="password"
          dir="ltr"
          autoComplete="new-password"
          aria-describedby={`${id}-hint`}
          value={next}
          onChange={(event) => setNext(event.target.value)}
        />
        <p id={`${id}-hint`} className="hint">
          {t("auth.password_hint", { min: PASSWORD_MIN })}
        </p>
      </div>
      {result === "saved" && <p role="status">{t("password.changed")}</p>}
      {result && result !== "saved" && (
        <p className="form-error" role="alert">
          {t(result)}
        </p>
      )}
      <div className="buttons">
        <button type="submit" disabled={sending}>
          {t("password.change")}
        </button>
      </div>
    </form>
  );
}
