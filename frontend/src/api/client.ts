import { getCsrfToken } from "./csrf.ts";
import { ApiError, toApiError } from "./errors.ts";

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

type ApiRequestOptions = {
  method?: HttpMethod;
  body?: unknown;
  headers?: HeadersInit;
  signal?: AbortSignal;
};

const DEFAULT_API_BASE_URL = import.meta.env.DEV ? "http://localhost:8000" : "";
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL;
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
    if (body instanceof FormData) {
      requestInit.body = body;
    } else {
      requestHeaders.set("Content-Type", "application/json");
      requestInit.body = JSON.stringify(body);
    }
  }

  const csrfToken = getCsrfToken();
  if (csrfToken !== null && UNSAFE_METHODS.has(method)) {
    requestHeaders.set("X-CSRF-Token", csrfToken);
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, requestInit);
  } catch {
    throw new ApiError({
      status: 0,
      code: "network_error",
      message: "Could not reach the GoalWise API. Check that the backend is running.",
    });
  }

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
