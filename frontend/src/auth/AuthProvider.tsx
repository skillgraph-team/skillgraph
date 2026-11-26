/**
 * Keeps track of who is logged in, and keeps the interface language in step with the
 * account (D-012).
 *
 * - On start it asks the backend (`GET /auth/me`); the login cookie is HttpOnly, so
 *   that's the only way to know.
 * - Logging in switches the interface to the account's language.
 * - Signing up saves the language the interface is in now.
 * - While logged in, every language change (the switcher) is saved to the account.
 */
import { type ReactNode, useCallback, useEffect, useMemo, useRef, useState } from "react";

import * as api from "../api/auth";
import { i18n } from "../i18n";
import { DEFAULT_LANGUAGE, type Language, LANGUAGE_CODES } from "../i18n/languages";
import { type Auth, AuthContext, type AuthState } from "./context";

function currentLanguage(): Language {
  const language = i18n.resolvedLanguage;
  return LANGUAGE_CODES.find((code) => code === language) ?? DEFAULT_LANGUAGE;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({ status: "loading" });
  // The listener below needs the latest user without re-subscribing on every change.
  const userRef = useRef<api.User | null>(null);

  const enter = useCallback(async (user: api.User) => {
    userRef.current = user;
    setState({ status: "logged-in", user });
    await i18n.changeLanguage(user.preferred_language);
  }, []);

  useEffect(() => {
    let active = true;
    api
      .getMe()
      .then((user) => {
        if (!active) return;
        if (user) void enter(user);
        else setState({ status: "anonymous" });
      })
      // Backend down: show the login page, which says so when the user tries.
      .catch(() => active && setState({ status: "anonymous" }));
    return () => {
      active = false;
    };
  }, [enter]);

  useEffect(() => {
    const save = (language: string) => {
      const user = userRef.current;
      const code = LANGUAGE_CODES.find((c) => c === language);
      if (!user || !code || code === user.preferred_language) return;
      userRef.current = { ...user, preferred_language: code };
      setState({ status: "logged-in", user: userRef.current });
      // The language is already switched and remembered in this browser; failing to
      // save it to the account only matters on another device, so don't interrupt.
      api.saveLanguage(code).catch((error: unknown) => {
        console.error("Couldn't save the language to the account", error);
      });
    };
    i18n.on("languageChanged", save);
    return () => i18n.off("languageChanged", save);
  }, []);

  const auth = useMemo<Auth>(
    () => ({
      state,
      logIn: async (email, password) => enter(await api.logIn(email, password)),
      signUp: async (email, password) =>
        enter(await api.signUp(email, password, currentLanguage())),
      logOut: async () => {
        await api.logOut();
        userRef.current = null;
        setState({ status: "anonymous" });
      },
    }),
    [state, enter],
  );

  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>;
}
