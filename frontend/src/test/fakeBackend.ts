/**
 * A pretend backend for page tests: replaces `fetch` and answers the auth and profile
 * endpoints the way backend/app/api/ does, keeping accounts, profiles and "the login
 * cookie" in memory. It doesn't re-check every validation rule: to test how a page shows
 * a backend refusal, queue the answer with `answerNextWith(status, body)`.
 *
 *   const backend = fakeBackend();             // nobody logged in, no accounts
 *   backend.addUser("a@b.co", "password1", "fr");
 *   backend.calls                              // ["GET /auth/me", "POST /auth/login", ...]
 *
 * Call `vi.unstubAllGlobals()` after the test (the page tests do it in afterEach).
 */
import { vi } from "vitest";

import type { User } from "../api/auth";
import type { Entry, EntryKind } from "../api/profile";
import type { SourceSummary } from "../api/sources";
import type { Language } from "../i18n/languages";

interface Account {
  user: User;
  password: string;
  display_name: string | null;
  headline: string | null;
  lists: Record<EntryKind, Entry[]>;
  sources: SourceSummary[];
  consentedAt: string | null;
  githubUsername: string | null;
}

/** The fields the endpoints read (each call sends only some of them). */
interface Body {
  email: string;
  password: string;
  preferred_language: Language;
  display_name: string | null;
  headline: string | null;
  current_password: string;
  new_password: string;
  username: string;
  [field: string]: string | null;
}

const ENTRY_PATH = /^\/profile\/(education|experience|projects)(?:\/([^/]+))?$/;

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
  let queued: Response | null = null;
  let nextId = 1;

  function addUser(email: string, password: string, language: Language = "en"): User {
    const user = {
      id: `id-${accounts.size + 1}`,
      email,
      preferred_language: language,
    };
    accounts.set(email, {
      user,
      password,
      display_name: null,
      headline: null,
      lists: { education: [], experience: [], projects: [] },
      sources: [],
      consentedAt: null,
      githubUsername: null,
    });
    return user;
  }

  async function handle(url: string, init: RequestInit = {}): Promise<Response> {
    const method = init.method ?? "GET";
    const path = url.replace(/^\/api/, "");
    const body = (init.body ? JSON.parse(String(init.body)) : {}) as Body;
    calls.push(`${method} ${path}`);
    bodies.push(body);
    if (down) throw new TypeError("Failed to fetch");
    if (queued) {
      const answer = queued;
      queued = null;
      return answer;
    }

    const sourcePath = /^\/sources\/([^/]+)$/.exec(path);
    if (sourcePath && method === "DELETE") {
      if (!loggedIn) return error(401, "not_authenticated");
      const before = loggedIn.sources.length;
      loggedIn.sources = loggedIn.sources.filter((source) => source.id !== sourcePath[1]);
      if (loggedIn.sources.length === before) return error(404, "not_found");
      return new Response(null, { status: 204 });
    }

    const entryPath = ENTRY_PATH.exec(path);
    if (entryPath) {
      if (!loggedIn) return error(401, "not_authenticated");
      return entries(loggedIn, method, entryPath[1] as EntryKind, entryPath[2], body);
    }

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
      case "GET /profile":
        return loggedIn ? json(profileOf(loggedIn)) : error(401, "not_authenticated");
      case "PATCH /profile": {
        if (!loggedIn) return error(401, "not_authenticated");
        if ("preferred_language" in body) {
          loggedIn.user = { ...loggedIn.user, preferred_language: body.preferred_language };
        }
        if ("display_name" in body) loggedIn.display_name = body.display_name;
        if ("headline" in body) loggedIn.headline = body.headline;
        return json(profileOf(loggedIn));
      }
      case "GET /sources":
        return loggedIn ? json(loggedIn.sources) : error(401, "not_authenticated");
      case "GET /profile/github-consent":
      case "PUT /profile/github-consent": {
        if (!loggedIn) return error(401, "not_authenticated");
        if (method === "PUT") loggedIn.consentedAt ??= "2026-11-26T10:00:00Z";
        return json({
          consented_at: loggedIn.consentedAt,
          github_username: loggedIn.githubUsername,
        });
      }
      case "DELETE /profile/github-consent":
        if (!loggedIn) return error(401, "not_authenticated");
        loggedIn.consentedAt = null;
        loggedIn.githubUsername = null;
        loggedIn.sources = loggedIn.sources.filter((source) => source.kind !== "github_repo");
        return new Response(null, { status: 204 });
      case "POST /sources/github": {
        if (!loggedIn) return error(401, "not_authenticated");
        if (!loggedIn.consentedAt) return error(403, "github_consent_required");
        if (body.username === "nobody-here") return error(404, "github_user_not_found");
        const repos = ["shop-api", "notes"].map((name) => ({
          id: `repo-${name}`,
          kind: "github_repo" as const,
          title: `${body.username}/${name}`,
          language: "en" as const,
          url: `https://github.com/${body.username}/${name}`,
          created_at: "2026-11-26T10:00:00Z",
        }));
        loggedIn.githubUsername = body.username;
        loggedIn.sources = [
          ...repos,
          ...loggedIn.sources.filter((source) => source.kind !== "github_repo"),
        ];
        return json(repos);
      }
      case "POST /auth/password":
        if (!loggedIn) return error(401, "not_authenticated");
        if (body.current_password !== loggedIn.password) return error(403, "wrong_password");
        loggedIn.password = body.new_password;
        return new Response(null, { status: 204 });
      default:
        return error(404, "not_found");
    }
  }

  function profileOf(account: Account) {
    return {
      display_name: account.display_name,
      headline: account.headline,
      preferred_language: account.user.preferred_language,
      ...account.lists,
    };
  }

  function entries(
    account: Account,
    method: string,
    kind: EntryKind,
    id: string | undefined,
    body: Body,
  ): Response {
    const list = account.lists[kind];
    if (!id && method === "GET") return json(list);
    if (!id && method === "POST") {
      const entry: Entry = { ...body, id: `entry-${nextId++}`, position: list.length };
      list.push(entry);
      return json(entry, 201);
    }
    const index = list.findIndex((entry) => entry.id === id);
    if (index < 0) return error(404, "not_found");
    if (method === "PUT") {
      const entry: Entry = { ...body, id: id ?? "", position: list[index]?.position ?? 0 };
      list[index] = entry;
      return json(entry);
    }
    if (method === "DELETE") {
      list.splice(index, 1);
      return new Response(null, { status: 204 });
    }
    return error(404, "not_found");
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
    /** The account's saved profile lists, to check what the backend holds. */
    lists(email: string) {
      return accounts.get(email)?.lists;
    },
    /** Adds a source to the account, as an upload would. */
    addSource(email: string, source: SourceSummary) {
      accounts.get(email)?.sources.unshift(source);
    },
    sources(email: string) {
      return accounts.get(email)?.sources ?? [];
    },
    passwordOf(email: string) {
      return accounts.get(email)?.password;
    },
    /** The next call (whatever it is) gets this answer instead. */
    answerNextWith(status: number, body: unknown) {
      queued = json(body, status);
    },
    /** From now on, every call fails as if the backend weren't running. */
    goDown() {
      down = true;
    },
  };
}
