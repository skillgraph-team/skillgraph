/**
 * Sources: the CV upload, the GitHub import and its consent, and the list of sources
 * (backend/app/api/sources.py, github.py, github_consent.py).
 *
 * The CV upload uses XMLHttpRequest instead of fetch: fetch can't report how much of
 * the file has been sent, and the screen shows a progress bar. Its errors are the same
 * ApiError / BackendUnreachableError as every other call.
 */
import { apiError, apiUrl, BackendUnreachableError, request } from "./client";

/** The backend's SourceSummary: no text, which can be large. */
export interface SourceSummary {
  id: string;
  kind: "cv" | "github_repo" | "certificate" | "manual_project";
  title: string;
  language: "en" | "fr" | "ar" | "other" | null;
  /** A repo's GitHub page; null for other kinds. */
  url: string | null;
  created_at: string;
}

export interface GitHubConsent {
  consented_at: string | null;
  github_username: string | null;
}

export function listSources(): Promise<SourceSummary[]> {
  return request<SourceSummary[]>("GET", "/sources");
}

export function deleteSource(id: string): Promise<void> {
  return request<void>("DELETE", `/sources/${encodeURIComponent(id)}`);
}

export function getGitHubConsent(): Promise<GitHubConsent> {
  return request<GitHubConsent>("GET", "/profile/github-consent");
}

export function giveGitHubConsent(): Promise<GitHubConsent> {
  return request<GitHubConsent>("PUT", "/profile/github-consent");
}

/** Also deletes everything imported from GitHub. */
export function withdrawGitHubConsent(): Promise<void> {
  return request<void>("DELETE", "/profile/github-consent");
}

/** Imports the username's public repos; answers with one source per repo. */
export function importGitHub(username: string): Promise<unknown[]> {
  return request<unknown[]>("POST", "/sources/github", { username });
}

/**
 * Uploads a CV (PDF or .docx). `onProgress` gets the share sent so far, 0 to 1.
 * Resolves when the backend has read the file and stored it as a source.
 */
export function uploadCv(file: File, onProgress?: (sent: number) => void): Promise<void> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", apiUrl("/sources/cv"));
    // Same origin (the Vite proxy in dev), so the login cookie goes along by itself.
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable && event.total > 0) onProgress?.(event.loaded / event.total);
    };
    xhr.onerror = () => reject(new BackendUnreachableError());
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) return resolve();
      let json: unknown = null;
      try {
        json = JSON.parse(xhr.responseText);
      } catch {
        // Not JSON: handled below.
      }
      if (json === null && xhr.status >= 500) return reject(new BackendUnreachableError(xhr));
      reject(apiError(xhr.status, json));
    };
    const form = new FormData();
    form.append("file", file);
    xhr.send(form);
  });
}
