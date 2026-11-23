/** Tests for the API client: the URL it calls and how it reads /health answers. */
import { afterEach, describe, expect, it, vi } from "vitest";

import { apiUrl, getHealth } from "./client";

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
