/**
 * Who is logged in, for any component: `const auth = useAuth();`.
 *
 * `auth.state.status` is "loading" (asking the backend), "anonymous" or "logged-in"
 * (then `auth.state.user` is set). The provider is AuthProvider.tsx.
 */
import { createContext, useContext } from "react";

import type { User } from "../api/auth";

export type AuthState =
  | { status: "loading" }
  | { status: "anonymous" }
  | { status: "logged-in"; user: User };

export interface Auth {
  state: AuthState;
  /** These throw the API's errors (ApiError, BackendUnreachableError) for the form to show. */
  logIn(email: string, password: string): Promise<void>;
  signUp(email: string, password: string): Promise<void>;
  logOut(): Promise<void>;
}

export const AuthContext = createContext<Auth | null>(null);

export function useAuth(): Auth {
  const auth = useContext(AuthContext);
  if (!auth) throw new Error("useAuth() needs an <AuthProvider> around the app");
  return auth;
}
