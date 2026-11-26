/**
 * Route guards.
 * - <RequireLogin>: anonymous visitors go to /login, which sends them back afterwards.
 * - <AnonymousOnly>: the login and sign-up pages send a logged-in user on: back to the
 *   page they first asked for, or home. This is also what moves them on right after
 *   logging in, so the forms themselves never navigate.
 *
 * The page to come back to travels in the router's state, not in the URL, so a link from
 * another site can't send someone elsewhere after they log in.
 */
import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { Navigate, useLocation } from "react-router";

import { useAuth } from "./context";
import { type FromState, safeReturnPath } from "./returnPath";

function Checking() {
  const { t } = useTranslation();
  return (
    <main>
      <p role="status">{t("auth.checking")}</p>
    </main>
  );
}

export function RequireLogin({ children }: { children: ReactNode }) {
  const { state } = useAuth();
  const location = useLocation();
  if (state.status === "loading") return <Checking />;
  if (state.status === "anonymous") {
    const from: FromState = { from: location.pathname + location.search };
    return <Navigate to="/login" replace state={from} />;
  }
  return children;
}

export function AnonymousOnly({ children }: { children: ReactNode }) {
  const { state } = useAuth();
  const location = useLocation();
  if (state.status === "loading") return <Checking />;
  if (state.status === "logged-in") {
    return <Navigate to={safeReturnPath(location.state)} replace />;
  }
  return children;
}
