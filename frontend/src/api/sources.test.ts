/** Tests for the CV upload call: what it sends, its progress, and its errors. */
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, BackendUnreachableError } from "./client";
import { uploadCv } from "./sources";

/** A stand-in XMLHttpRequest: records what is sent; the test decides the answer. */
class FakeXhr {
  static last: FakeXhr;
  method = "";
  url = "";
  sent: FormData | null = null;
  status = 0;
  responseText = "";
  upload: { onprogress: ((event: ProgressEvent) => void) | null } = { onprogress: null };
  onload: (() => void) | null = null;
  onerror: (() => void) | null = null;

  constructor() {
    FakeXhr.last = this;
  }
  open(method: string, url: string) {
    this.method = method;
    this.url = url;
  }
  send(body: FormData) {
    this.sent = body;
  }
  answer(status: number, body: string) {
    this.status = status;
    this.responseText = body;
    this.onload?.();
  }
}

afterEach(() => {
  vi.unstubAllGlobals();
});

function start(onProgress?: (sent: number) => void) {
  vi.stubGlobal("XMLHttpRequest", FakeXhr);
  const file = new File(["%PDF"], "cv.pdf", { type: "application/pdf" });
  return { file, done: uploadCv(file, onProgress) };
}

describe("uploadCv", () => {
  it("posts the file as the form field `file` and reports progress", async () => {
    const progress: number[] = [];
    const { file, done } = start((sent) => progress.push(sent));
    const xhr = FakeXhr.last;

    xhr.upload.onprogress?.({ lengthComputable: true, loaded: 1, total: 4 } as ProgressEvent);
    xhr.answer(201, "{}");
    await done;

    expect(xhr.method).toBe("POST");
    expect(xhr.url).toMatch(/\/sources\/cv$/);
    expect(xhr.sent?.get("file")).toBe(file);
    expect(progress).toEqual([0.25]);
  });

  it("throws the backend's error code", async () => {
    const { done } = start();
    FakeXhr.last.answer(415, JSON.stringify({ detail: { code: "unsupported_file_type" } }));
    await expect(done).rejects.toEqual(new ApiError(415, "unsupported_file_type"));
  });

  it("says the backend is unreachable when there is no answer", async () => {
    const { done } = start();
    FakeXhr.last.onerror?.();
    await expect(done).rejects.toBeInstanceOf(BackendUnreachableError);
  });

  it("treats the proxy's 502 without JSON as unreachable", async () => {
    const { done } = start();
    FakeXhr.last.answer(502, "Bad Gateway");
    await expect(done).rejects.toBeInstanceOf(BackendUnreachableError);
  });
});
