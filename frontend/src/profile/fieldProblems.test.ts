/** Tests for the field checks and for reading the backend's 422 answer. */
import { describe, expect, it } from "vitest";

import { ApiError } from "../api/client";
import { ENTRY_KINDS } from "./entryKinds";
import { checkEntry, problemsFromApi } from "./fieldProblems";

const projects = ENTRY_KINDS.find((spec) => spec.kind === "projects")!;
const education = ENTRY_KINDS.find((spec) => spec.kind === "education")!;

describe("checkEntry", () => {
  it("accepts a complete entry", () => {
    expect(
      checkEntry(projects, { title: "App", description: "Text", url: "https://x.io" }),
    ).toEqual({});
  });

  it("names each field that is missing, too long or not a link", () => {
    expect(
      checkEntry(projects, { title: "  ", description: "x".repeat(5001), url: "ftp://x" }),
    ).toEqual({
      title: "profile.problems.required",
      description: "profile.problems.too_long",
      url: "profile.problems.url",
    });
  });

  it("refuses an end date before the start date", () => {
    expect(
      checkEntry(education, {
        institution: "School",
        start_date: "2024-09-01",
        end_date: "2024-08-31",
      }),
    ).toEqual({ end_date: "profile.problems.end_before_start" });
  });
});

describe("problemsFromApi", () => {
  it("maps FastAPI's error types to problems", () => {
    const error = new ApiError(422, "invalid_input", {
      title: "string_too_short",
      url: "string_pattern_mismatch",
      start_date: "date_from_datetime_parsing",
      "": "value_error",
    });
    expect(problemsFromApi(error)).toEqual({
      title: "profile.problems.required",
      url: "profile.problems.url",
      start_date: "profile.problems.date",
      "": "profile.problems.end_before_start",
    });
  });

  it("is null for errors that aren't about the fields", () => {
    expect(problemsFromApi(new ApiError(404, "not_found"))).toBeNull();
    expect(problemsFromApi(new Error("boom"))).toBeNull();
  });
});
