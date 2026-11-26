/**
 * Sign up, log in, log out and "who am I" (backend/app/api/auth.py).
 *
 * The login itself is an HttpOnly cookie the backend sets (D-015): the frontend never
 * sees the token, it only learns who is logged in from these answers.
 */
import type { Language } from "../i18n/languages";
import { ApiError, request } from "./client";

/** The backend's UserOut. */
export interface User {
  id: string;
  email: string;
  preferred_language: Language;
}

export function signUp(email: string, password: string, language: Language): Promise<User> {
  return request<User>("POST", "/auth/signup", {
    email,
    password,
    preferred_language: language,
  });
}

export function logIn(email: string, password: string): Promise<User> {
  return request<User>("POST", "/auth/login", { email, password });
}

export function logOut(): Promise<void> {
  return request<void>("POST", "/auth/logout");
}

/** The logged-in user, or null when nobody is (no cookie, or an expired or invalid one). */
export async function getMe(): Promise<User | null> {
  try {
    return await request<User>("GET", "/auth/me");
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) return null;
    throw error;
  }
}

/** Saves the interface language to the account (D-012). */
export async function saveLanguage(language: Language): Promise<void> {
  await request<unknown>("PATCH", "/profile", { preferred_language: language });
}
