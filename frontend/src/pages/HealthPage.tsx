/**
 * Health page: shows whether the backend and its database are working.
 *
 * The first screen and the example every later page follows: call the API client in an
 * effect, keep the result in one state value, render one element per state. Each state's
 * text is the translation key `health.<state>` in src/locales/{en,fr,ar}.json.
 */
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { BackendUnreachableError, getHealth } from "../api/client";

type HealthState = "loading" | "ok" | "database-unreachable" | "backend-unreachable";

export function HealthPage() {
  const { t } = useTranslation();
  const [state, setState] = useState<HealthState>("loading");

  useEffect(() => {
    // Abort the call if the page goes away before the answer arrives.
    const controller = new AbortController();
    getHealth(controller.signal)
      .then((health) => setState(health.status === "ok" ? "ok" : "database-unreachable"))
      .catch((error: unknown) => {
        if (controller.signal.aborted) return;
        if (error instanceof BackendUnreachableError) {
          setState("backend-unreachable");
        } else {
          throw error;
        }
      });
    return () => controller.abort();
  }, []);

  return (
    <main>
      <h1>{t("app.name")}</h1>
      <p data-testid="health-status" data-state={state} role="status">
        {t(`health.${state}`)}
      </p>
    </main>
  );
}
