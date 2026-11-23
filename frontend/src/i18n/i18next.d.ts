/**
 * Tells TypeScript which translation keys exist, so `t("health.typo")` fails
 * `npm run check` instead of showing the raw key on screen.
 */
import "i18next";

import type { Messages } from "./resources";

declare module "i18next" {
  interface CustomTypeOptions {
    defaultNS: "translation";
    resources: { translation: Messages };
  }
}
