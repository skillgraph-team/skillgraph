/**
 * The page to go back to after logging in. RequireLogin (guards.tsx) puts it in the
 * router's state as `{ from }`; this checks it is a path inside the app.
 */

export interface FromState {
  from?: string;
}

/** Only a path inside this app ("/x", not "//other.site" or "https://..."). */
export function safeReturnPath(state: unknown): string {
  const from = (state as FromState | null)?.from;
  return typeof from === "string" && from.startsWith("/") && !from.startsWith("//") ? from : "/";
}
