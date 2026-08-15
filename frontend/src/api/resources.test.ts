import { afterEach, describe, expect, it, vi } from "vitest";

import { clearCsrfToken, setCsrfToken } from "./csrf.ts";
import { archiveGoal } from "./resources.ts";

describe("API resources", () => {
  afterEach(() => {
    clearCsrfToken();
    vi.unstubAllGlobals();
  });

  it("archives goals through the CSRF-protected archive endpoint", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ item: null }), {
        headers: { "Content-Type": "application/json" },
        status: 200,
      }),
    );
    vi.stubGlobal("fetch", fetchMock);
    setCsrfToken("csrf-token");

    await archiveGoal("goal-123");

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    const headers = init.headers as Headers;
    expect(url.endsWith("/api/v1/goals/goal-123/archive")).toBe(true);
    expect(init.method).toBe("POST");
    expect(init.credentials).toBe("include");
    expect(headers.get("X-CSRF-Token")).toBe("csrf-token");
  });
});
