/** The app's frame: a header with the language switcher, then the current page. */
import { LanguageSwitcher } from "./components/LanguageSwitcher";
import { HealthPage } from "./pages/HealthPage";

export function App() {
  return (
    <>
      <header className="app-header">
        <LanguageSwitcher />
      </header>
      <HealthPage />
    </>
  );
}
