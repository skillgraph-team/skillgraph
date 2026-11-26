/** In the header: nothing while logged out; the log-out button while logged in. */
import { useTranslation } from "react-i18next";

import { useAuth } from "../auth/context";

export function AccountMenu() {
  const { t } = useTranslation();
  const auth = useAuth();
  if (auth.state.status !== "logged-in") return null;

  return (
    <button type="button" onClick={() => void auth.logOut()}>
      {t("auth.log_out")}
    </button>
  );
}
