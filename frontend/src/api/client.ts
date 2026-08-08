import { getCsrfToken } from "./csrf.ts";
import { toApiError } from "./errors.ts";

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

type ApiRequestOptions = {
  method?: HttpMethod;
  body?: unknown;
  headers?: HeadersInit;
  signal?: AbortSignal;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";
const UNSAFE_METHODS = new Set<HttpMethod>(["POST", "PUT", "PATCH", "DELETE"]);

export async function apiRequest<TResponse>(
  path: string,
  { method = "GET", body, headers, signal }: ApiRequestOptions = {},
): Promise<TResponse> {
  const requestHeaders = new Headers(headers);
  requestHeaders.set("Accept", "application/json");

  const requestInit: RequestInit = {
    method,
    credentials: "include",
    headers: requestHeaders,
    signal,
  };

  if (body !== undefined) {
    requestHeaders.set("Content-Type", "application/json");
    requestInit.body = JSON.stringify(body);
  }

  const csrfToken = getCsrfToken();
  if (csrfToken !== null && UNSAFE_METHODS.has(method)) {
    requestHeaders.set("X-CSRF-Token", csrfToken);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, requestInit);

  if (response.status === 204) {
    if (!response.ok) {
      throw toApiError(response.status, null);
    }
    return undefined as TResponse;
  }

  const responseBody = await readResponseBody(response);
  if (!response.ok) {
    throw toApiError(response.status, responseBody);
  }

  return responseBody as TResponse;
}

async function readResponseBody(response: Response) {
  const contentType = response.headers.get("Content-Type");
  if (contentType?.includes("application/json") !== true) {
    return null;
  }

  return response.json();
}
