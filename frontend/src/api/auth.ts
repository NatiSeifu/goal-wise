import { apiRequest } from "./client.ts";
import { clearCsrfToken, setCsrfToken } from "./csrf.ts";
import { endpoints } from "./endpoints.ts";
import type { AuthResponse, LoginRequest, RegisterRequest } from "./types.ts";

export async function register(payload: RegisterRequest) {
  const response = await apiRequest<AuthResponse>(endpoints.auth.register, {
    method: "POST",
    body: payload,
  });
  setCsrfToken(response.item.csrf_token);
  return response;
}

export async function login(payload: LoginRequest) {
  const response = await apiRequest<AuthResponse>(endpoints.auth.login, {
    method: "POST",
    body: payload,
  });
  setCsrfToken(response.item.csrf_token);
  return response;
}

export async function logout() {
  await apiRequest<void>(endpoints.auth.logout, { method: "POST" });
  clearCsrfToken();
}

export async function getCurrentUser() {
  const response = await apiRequest<AuthResponse>(endpoints.auth.me);
  setCsrfToken(response.item.csrf_token);
  return response;
}
