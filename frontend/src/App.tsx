/**
 * The app's frame and its pages.
 *
 * /        home, logged-in users only (anonymous visitors go to /login)
 * /profile the user's profile, lists and password (logged-in users only)
 * /login   log in       /signup  sign up      (logged-in users are sent on)
 * /health  whether the backend and database work (anyone)
 *
 * The router itself (BrowserRouter) is added in main.tsx, so tests can use a MemoryRouter.
 */
import { Navigate, Route, Routes } from "react-router";

import { AuthProvider } from "./auth/AuthProvider";
import { AnonymousOnly, RequireLogin } from "./auth/guards";
import { AccountMenu } from "./components/AccountMenu";
import { LanguageSwitcher } from "./components/LanguageSwitcher";
import { HealthPage } from "./pages/HealthPage";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { ProfilePage } from "./pages/ProfilePage";
import { SignUpPage } from "./pages/SignUpPage";

export function App() {
  return (
    <AuthProvider>
      <header className="app-header">
        <LanguageSwitcher />
        <AccountMenu />
      </header>
      <Routes>
        <Route
          path="/"
          element={
            <RequireLogin>
              <HomePage />
            </RequireLogin>
          }
        />
        <Route
          path="/profile"
          element={
            <RequireLogin>
              <ProfilePage />
            </RequireLogin>
          }
        />
        <Route
          path="/login"
          element={
            <AnonymousOnly>
              <LoginPage />
            </AnonymousOnly>
          }
        />
        <Route
          path="/signup"
          element={
            <AnonymousOnly>
              <SignUpPage />
            </AnonymousOnly>
          }
        />
        <Route path="/health" element={<HealthPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}
