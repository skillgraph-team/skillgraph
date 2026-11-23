/**
 * Health page: shows whether the backend and its database are working.
 *
 * The first screen and the example every later page follows: call the API client in an
 * effect, keep the result in one state value, render one element per state.
 */
import { useEffect, useState } from "react";

import { BackendUnreachableError, getHealth } from "../api/client";

type HealthState = "loading" | "ok" | "database-unreachable" | "backend-unreachable";

// TEMPORARY: English only. M0.7 moves these texts into src/locales/{en,fr,ar}.json.
const LABELS: Record<HealthState, string> = {
  loading: "Checking the backend…",
  ok: "Backend and database are working.",
  "database-unreachable": "The backend is running, but it can't reach the database.",
  "backend-unreachable": "The backend can't be reached. Is it running?",
};

export function HealthPage() {
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
      <h1>SkillGraph</h1>
      <p data-testid="health-status" data-state={state} role="status">
        {LABELS[state]}
      </p>
    </main>
  );
}
