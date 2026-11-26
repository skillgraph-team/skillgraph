/**
 * A pretend backend for page tests: replaces `fetch` and answers the auth endpoints the
 * way backend/app/api/auth.py does, keeping accounts and "the login cookie" in memory.
 *
 *   const backend = fakeBackend();             // nobody logged in, no accounts
 *   backend.addUser("a@b.co", "password1", "fr");
 *   backend.calls                              // ["GET /auth/me", "POST /auth/login", ...]
 *
 * Call `vi.unstubAllGlobals()` after the test (the page tests do it in afterEach).
 */
import { vi } from "vitest";

import type { User } from "../api/auth";
import type { Language } from "../i18n/languages";

interface Account {
  user: User;
  password: string;
}

/** The fields the auth endpoints read (each call sends only some of them). */
interface Body {
  email: string;
  password: string;
  preferred_language: Language;
}

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

const error = (status: number, code: string) => json({ detail: { code } }, status);

export function fakeBackend() {
  const accounts = new Map<string, Account>();
  const calls: string[] = [];
  const bodies: unknown[] = [];
  let loggedIn: Account | null = null;
  let down = false;

  function addUser(email: string, password: string, language: Language = "en"): User {
    const user = {
      id: `id-${accounts.size + 1}`,
      email,
      preferred_language: language,
    };
    accounts.set(email, { user, password });
    return user;
  }

  async function handle(url: string, init: RequestInit = {}): Promise<Response> {
    const method = init.method ?? "GET";
    const path = url.replace(/^\/api/, "");
    const body = (init.body ? JSON.parse(String(init.body)) : {}) as Body;
    calls.push(`${method} ${path}`);
    bodies.push(body);
    if (down) throw new TypeError("Failed to fetch");

    switch (`${method} ${path}`) {
      case "GET /auth/me":
        return loggedIn ? json(loggedIn.user) : error(401, "not_authenticated");
      case "POST /auth/signup": {
        if (accounts.has(body.email)) return error(409, "email_taken");
        addUser(body.email, body.password, body.preferred_language);
        loggedIn = accounts.get(body.email) ?? null;
        return json(loggedIn?.user, 201);
      }
      case "POST /auth/login": {
        const account = accounts.get(body.email);
        if (!account || account.password !== body.password) {
          return error(401, "invalid_credentials");
        }
        loggedIn = account;
        return json(account.user);
      }
      case "POST /auth/logout":
        loggedIn = null;
        return new Response(null, { status: 204 });
      case "PATCH /profile": {
        if (!loggedIn) return error(401, "not_authenticated");
        loggedIn.user = {
          ...loggedIn.user,
          preferred_language: body.preferred_language,
        };
        return json({ preferred_language: loggedIn.user.preferred_language });
      }
      default:
        return error(404, "not_found");
    }
  }

  vi.stubGlobal("fetch", vi.fn(handle));

  return {
    addUser,
    calls,
    /** The JSON body of each call, in the same order as `calls`. */
    bodies,
    logIn(email: string) {
      loggedIn = accounts.get(email) ?? null;
    },
    get loggedIn() {
      return loggedIn?.user ?? null;
    },
    /** From now on, every call fails as if the backend weren't running. */
    goDown() {
      down = true;
    },
  };
}
