/** Tests for the API client: the URL it calls, how it reads /health answers, and how
 * request() turns backend errors into ApiError codes. */
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, apiUrl, BackendUnreachableError, getHealth, request } from "./client";
import { errorKey } from "./errors";

function mockFetch(response: Response | Error) {
  const fn = vi.fn(() =>
    response instanceof Error ? Promise.reject(response) : Promise.resolve(response),
  );
  vi.stubGlobal("fetch", fn);
  return fn;
}

function jsonResponse(body: unknown, status: number): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("apiUrl", () => {
  it("puts the base URL in front of the path", () => {
    expect(apiUrl("/health", "/api")).toBe("/api/health");
  });

  it("does not double the slash when the base URL ends with one", () => {
    expect(apiUrl("/health", "http://localhost:8000/")).toBe("http://localhost:8000/health");
  });
});

describe("getHealth", () => {
  it("calls /health on the backend", async () => {
    const fetchMock = mockFetch(jsonResponse({ status: "ok", database: "ok" }, 200));
    await getHealth();
    expect(fetchMock).toHaveBeenCalledWith(apiUrl("/health"), expect.anything());
  });

  it("returns the body when everything works (200)", async () => {
    mockFetch(jsonResponse({ status: "ok", database: "ok" }, 200));
    expect(await getHealth()).toEqual({ status: "ok", database: "ok" });
  });

  it("returns the body when the database is down (503)", async () => {
    mockFetch(jsonResponse({ status: "error", database: "unreachable" }, 503));
    expect(await getHealth()).toEqual({ status: "error", database: "unreachable" });
  });

  it("throws BackendUnreachableError when the backend can't be reached", async () => {
    mockFetch(new TypeError("Failed to fetch"));
    await expect(getHealth()).rejects.toMatchObject({ name: "BackendUnreachableError" });
  });

  it("throws BackendUnreachableError when the answer is not a health answer", async () => {
    mockFetch(new Response("<html>proxy error</html>", { status: 502 }));
    await expect(getHealth()).rejects.toMatchObject({ name: "BackendUnreachableError" });
  });
});

describe("request", () => {
  it("sends JSON with the login cookie and returns the answer", async () => {
    const fetchMock = mockFetch(jsonResponse({ id: "1" }, 200));
    expect(await request("POST", "/auth/login", { email: "a@b.co" })).toEqual({
      id: "1",
    });
    expect(fetchMock).toHaveBeenCalledWith(
      apiUrl("/auth/login"),
      expect.objectContaining({
        method: "POST",
        credentials: "same-origin",
        body: JSON.stringify({ email: "a@b.co" }),
      }),
    );
  });

  it("returns undefined for 204 No Content", async () => {
    mockFetch(new Response(null, { status: 204 }));
    expect(await request("POST", "/auth/logout")).toBeUndefined();
  });

  it("throws the backend's error code", async () => {
    mockFetch(jsonResponse({ detail: { code: "email_taken" } }, 409));
    await expect(request("POST", "/auth/signup")).rejects.toEqual(new ApiError(409, "email_taken"));
  });

  it("calls FastAPI's validation answer invalid_input", async () => {
    mockFetch(jsonResponse({ detail: [{ type: "string_too_short" }] }, 422));
    await expect(request("POST", "/auth/signup")).rejects.toMatchObject({
      code: "invalid_input",
    });
  });

  it("says the backend is unreachable when there is no answer, or the proxy's 502", async () => {
    mockFetch(new TypeError("Failed to fetch"));
    await expect(request("GET", "/auth/me")).rejects.toBeInstanceOf(BackendUnreachableError);
    mockFetch(new Response("Bad Gateway", { status: 502 }));
    await expect(request("GET", "/auth/me")).rejects.toBeInstanceOf(BackendUnreachableError);
  });
});

describe("errorKey", () => {
  it("maps a backend code to errors.<code>", () => {
    expect(errorKey(new ApiError(403, "wrong_password"))).toBe("errors.wrong_password");
  });

  it("falls back to errors.unknown for codes and errors it doesn't know", () => {
    expect(errorKey(new ApiError(400, "brand_new_code"))).toBe("errors.unknown");
    expect(errorKey(new Error("boom"))).toBe("errors.unknown");
  });

  it("says when the backend can't be reached", () => {
    expect(errorKey(new BackendUnreachableError())).toBe("errors.backend_unreachable");
  });
});
