/** In the header: nothing while logged out; links to the pages and log out while logged in. */
import { useTranslation } from "react-i18next";
import { NavLink } from "react-router";

import { useAuth } from "../auth/context";

export function AccountMenu() {
  const { t } = useTranslation();
  const auth = useAuth();
  if (auth.state.status !== "logged-in") return null;

  return (
    <nav className="account-menu" aria-label={t("nav.label")}>
      <NavLink to="/" end>
        {t("nav.home")}
      </NavLink>
      <NavLink to="/profile">{t("nav.profile")}</NavLink>
      <button type="button" onClick={() => void auth.logOut()}>
        {t("auth.log_out")}
      </button>
    </nav>
  );
}
