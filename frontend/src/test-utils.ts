import { vi } from "vitest";

export type Reply = { status?: number; body: unknown } | (() => { status?: number; body: unknown });

/**
 * Stubs `fetch` with a route table keyed by "METHOD /path" (query string included when given,
 * otherwise ignored). Unknown routes answer 404 with the standard error body.
 */
export function stubApi(routes: Record<string, Reply>) {
  const calls: string[] = [];
  const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const href = typeof input === "string" ? input : input instanceof URL ? input.href : input.url;
    const url = new URL(href, "http://station.local");
    const method = init?.method ?? "GET";
    const withQuery = `${method} ${url.pathname}${url.search}`;
    const withoutQuery = `${method} ${url.pathname}`;
    calls.push(withQuery);
    const reply = routes[withQuery] ?? routes[withoutQuery];
    const { status = 200, body } =
      reply === undefined
        ? { status: 404, body: { error: { code: "NOT_FOUND", message: "Not found", details: {} } } }
        : typeof reply === "function"
          ? reply()
          : reply;
    return Promise.resolve(
      new Response(JSON.stringify(body), {
        status,
        headers: { "Content-Type": "application/json" },
      }),
    );
  });
  vi.stubGlobal("fetch", fetchMock);
  return { calls, fetchMock };
}

export const apiError = (status: number, code: string, message = code) => ({
  status,
  body: { error: { code, message, details: {} } },
});
