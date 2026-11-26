/**
 * The email + password form shared by the login and sign-up pages.
 *
 * `noValidate` turns off the browser's own checks, whose messages are in the browser's
 * language rather than the interface's. Sign-up checks the same rules as the backend
 * (T-069) before sending; anything the backend refuses is shown from its error code.
 * Email and password are always typed left to right, also in Arabic (`dir="ltr"`).
 */
import { type FormEvent, type ReactNode, useId, useState } from "react";
import { useTranslation } from "react-i18next";

import { type ErrorKey, errorKey } from "../api/errors";

// The backend's rule (backend/app/api/auth.py): something@something.something.
const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
export const PASSWORD_MIN = 8;
export const PASSWORD_MAX = 128;

type Problem =
  | ErrorKey
  | "auth.validation.email_invalid"
  | "auth.validation.password_too_short"
  | "auth.validation.password_too_long"
  | "auth.validation.required";

interface Props {
  mode: "login" | "signup";
  onSubmit(email: string, password: string): Promise<void>;
  /** Shown between the fields and the button (the sign-up privacy notice). */
  children?: ReactNode;
}

function check(mode: Props["mode"], email: string, password: string): Problem | null {
  if (!email.trim() || !password) return "auth.validation.required";
  if (mode === "login") return null;
  if (!EMAIL.test(email.trim())) return "auth.validation.email_invalid";
  if (password.length < PASSWORD_MIN) return "auth.validation.password_too_short";
  if (password.length > PASSWORD_MAX) return "auth.validation.password_too_long";
  return null;
}

export function AuthForm({ mode, onSubmit, children }: Props) {
  const { t } = useTranslation();
  const id = useId();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [problem, setProblem] = useState<Problem | null>(null);
  const [sending, setSending] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    const found = check(mode, email, password);
    setProblem(found);
    if (found) return;
    setSending(true);
    try {
      await onSubmit(email.trim(), password);
    } catch (error) {
      setProblem(errorKey(error));
      setSending(false);
    }
  }

  return (
    <form className="auth-form" noValidate onSubmit={(event) => void submit(event)}>
      <label htmlFor={`${id}-email`}>{t("auth.email")}</label>
      <input
        id={`${id}-email`}
        type="email"
        dir="ltr"
        autoComplete="email"
        value={email}
        onChange={(event) => setEmail(event.target.value)}
      />
      <label htmlFor={`${id}-password`}>{t("auth.password")}</label>
      <input
        id={`${id}-password`}
        type="password"
        dir="ltr"
        autoComplete={mode === "login" ? "current-password" : "new-password"}
        aria-describedby={mode === "signup" ? `${id}-hint` : undefined}
        value={password}
        onChange={(event) => setPassword(event.target.value)}
      />
      {mode === "signup" && (
        <p id={`${id}-hint`} className="hint">
          {t("auth.password_hint", { min: PASSWORD_MIN })}
        </p>
      )}
      {children}
      {problem && (
        <p className="form-error" role="alert">
          {t(problem)}
        </p>
      )}
      <button type="submit" disabled={sending}>
        {t(mode === "login" ? "auth.log_in" : "auth.sign_up")}
      </button>
    </form>
  );
}
