/**
 * The one place the frontend talks to the backend.
 *
 * Every backend call goes through a function here, so the base URL, error handling and
 * response types live in one file. The base URL comes from VITE_API_BASE_URL (default
 * `/api`, which the Vite dev server forwards to the backend; see vite.config.ts).
 *
 * `request()` is the shared helper for JSON calls: it sends the login cookie, and turns a
 * backend error `{"detail": {"code": ...}}` into an `ApiError` with that code. The calls
 * for each part of the backend are in their own file (auth.ts, ...).
 */

const DEFAULT_BASE_URL = "/api";

/** Thrown when the backend can't be reached or gives an answer we don't understand. */
export class BackendUnreachableError extends Error {
  constructor(cause?: unknown) {
    super("Backend unreachable", { cause });
    this.name = "BackendUnreachableError";
  }
}

/** The backend answered with an error. `code` is its error code, or `invalid_input` for
 * FastAPI's validation answer (422 without a code), or `unknown`. */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
  ) {
    super(`Backend error ${status} ${code}`);
    this.name = "ApiError";
  }
}

function errorCode(status: number, body: unknown): string {
  const detail = (body as { detail?: unknown } | null)?.detail;
  const code = (detail as { code?: unknown } | null)?.code;
  if (typeof code === "string") return code;
  return status === 422 ? "invalid_input" : "unknown";
}

/**
 * Calls the backend and returns the JSON answer (or undefined for 204 No Content).
 * Throws ApiError for an error answer, BackendUnreachableError when there is no answer.
 */
export async function request<T>(
  method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE",
  path: string,
  body?: unknown,
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(apiUrl(path), {
      method,
      // Same origin in dev (the Vite proxy), so the login cookie goes along by itself.
      credentials: "same-origin",
      headers: body === undefined ? undefined : { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch (error) {
    throw new BackendUnreachableError(error);
  }
  if (response.status === 204) return undefined as T;
  const json: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    // The Vite proxy answers 502/504 without JSON when the backend isn't running.
    if (json === null && response.status >= 500) throw new BackendUnreachableError(response);
    throw new ApiError(response.status, errorCode(response.status, json));
  }
  return json as T;
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
