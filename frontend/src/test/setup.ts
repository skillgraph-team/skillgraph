/**
 * Runs before every test file (vite.config.ts `test.setupFiles`).
 *
 * Starts translations like the real app does, and after each test puts the language
 * back to English and forgets the saved choice, so tests don't affect each other.
 */
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

import { i18n } from "../i18n";

afterEach(async () => {
  cleanup();
  await i18n.changeLanguage("en");
  localStorage.clear();
});
