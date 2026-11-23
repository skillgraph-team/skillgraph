/** Tests for the health page: what it shows for each backend answer. */
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import * as client from "../api/client";
import { HealthPage } from "./HealthPage";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("HealthPage", () => {
  it("says it is checking while waiting for the backend", () => {
    vi.spyOn(client, "getHealth").mockReturnValue(new Promise(() => {}));
    render(<HealthPage />);
    expect(screen.getByTestId("health-status").dataset.state).toBe("loading");
  });

  it("shows ok when backend and database work", async () => {
    vi.spyOn(client, "getHealth").mockResolvedValue({ status: "ok", database: "ok" });
    render(<HealthPage />);
    await vi.waitFor(() =>
      expect(screen.getByTestId("health-status").dataset.state).toBe("ok"),
    );
  });

  it("shows a database problem on a 503 answer", async () => {
    vi.spyOn(client, "getHealth").mockResolvedValue({ status: "error", database: "unreachable" });
    render(<HealthPage />);
    await vi.waitFor(() =>
      expect(screen.getByTestId("health-status").dataset.state).toBe("database-unreachable"),
    );
  });

  it("shows that the backend is unreachable when the call fails", async () => {
    vi.spyOn(client, "getHealth").mockRejectedValue(new client.BackendUnreachableError());
    render(<HealthPage />);
    await vi.waitFor(() =>
      expect(screen.getByTestId("health-status").dataset.state).toBe("backend-unreachable"),
    );
  });
});
