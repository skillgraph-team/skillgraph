/** Login page (/login). After logging in, AnonymousOnly (auth/guards.tsx) moves the user on. */
import { useTranslation } from "react-i18next";
import { Link, useLocation } from "react-router";

import { useAuth } from "../auth/context";
import { AuthForm } from "../components/AuthForm";

export function LoginPage() {
  const { t } = useTranslation();
  const auth = useAuth();
  const location = useLocation();

  return (
    <main className="auth-page">
      <h1>{t("auth.log_in")}</h1>
      <AuthForm mode="login" onSubmit={auth.logIn} />
      {/* state: keep the page to come back to when switching to sign-up. */}
      <p>
        {t("auth.no_account")}{" "}
        <Link to="/signup" state={location.state}>
          {t("auth.sign_up")}
        </Link>
      </p>
    </main>
  );
}
