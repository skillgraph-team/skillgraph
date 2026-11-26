/**
 * Sign-up page (/signup), with the privacy notice (what we store, what for, how to delete
 * it). The account gets the language the interface is in now.
 */
import { useTranslation } from "react-i18next";
import { Link, useLocation } from "react-router";

import { useAuth } from "../auth/context";
import { AuthForm } from "../components/AuthForm";

export function SignUpPage() {
  const { t } = useTranslation();
  const auth = useAuth();
  const location = useLocation();

  return (
    <main className="auth-page">
      <h1>{t("auth.sign_up")}</h1>
      <AuthForm mode="signup" onSubmit={auth.signUp}>
        <section className="privacy-notice" aria-labelledby="privacy-title">
          <h2 id="privacy-title">{t("privacy.title")}</h2>
          <ul>
            <li>{t("privacy.stored")}</li>
            <li>{t("privacy.used")}</li>
            <li>{t("privacy.deleted")}</li>
          </ul>
        </section>
      </AuthForm>
      <p>
        {t("auth.have_account")}{" "}
        <Link to="/login" state={location.state}>
          {t("auth.log_in")}
        </Link>
      </p>
    </main>
  );
}
