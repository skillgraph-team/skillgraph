/**
 * The one place the frontend talks to the backend.
 *
 * Every backend call goes through a function here, so the base URL, error handling and
 * response types live in one file. The base URL comes from VITE_API_BASE_URL (default
 * `/api`, which the Vite dev server forwards to the backend; see vite.config.ts).
 */

const DEFAULT_BASE_URL = "/api";

/** Thrown when the backend can't be reached or gives an answer we don't understand. */
export class BackendUnreachableError extends Error {
  constructor(cause?: unknown) {
    super("Backend unreachable", { cause });
    this.name = "BackendUnreachableError";
  }
}

/** What the backend's GET /health returns (backend/app/main.py). */
export type HealthResponse =
  | { status: "ok"; database: "ok" }
  | { status: "error"; database: "unreachable" };

/** Builds the full URL for a backend path such as `/health`. */
export function apiUrl(
  path: string,
  baseUrl: string = import.meta.env.VITE_API_BASE_URL || DEFAULT_BASE_URL,
): string {
  return baseUrl.replace(/\/+$/, "") + path;
}

function isHealthResponse(body: unknown): body is HealthResponse {
  if (typeof body !== "object" || body === null) return false;
  const { status, database } = body as Record<string, unknown>;
  return (
    (status === "ok" && database === "ok") || (status === "error" && database === "unreachable")
  );
}

/**
 * Asks the backend whether it and its database are working.
 *
 * A 503 is a valid answer (backend up, database down), so it is returned, not thrown.
 */
export async function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  let body: unknown;
  try {
    const response = await fetch(apiUrl("/health"), { signal });
    body = await response.json();
  } catch (error) {
    throw new BackendUnreachableError(error);
  }
  if (!isHealthResponse(body)) {
    throw new BackendUnreachableError(body);
  }
  return body;
}
