/** Home page (/), for logged-in users only. A placeholder until the profile screens (M3.4). */
import { useTranslation } from "react-i18next";

import { useAuth } from "../auth/context";

export function HomePage() {
  const { t } = useTranslation();
  const { state } = useAuth();
  const email = state.status === "logged-in" ? state.user.email : "";

  return (
    <main>
      <h1>{t("app.name")}</h1>
      <p>
        {/* <bdi>: a Latin email inside an Arabic sentence keeps its own direction. */}
        {t("home.logged_in_as")} <bdi>{email}</bdi>
      </p>
      <p>{t("home.coming")}</p>
    </main>
  );
}
