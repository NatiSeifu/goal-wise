import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  getCurrentUser,
  login as loginRequest,
  logout as logoutRequest,
  register as registerRequest,
} from "../../api/auth.ts";
import { ApiError } from "../../api/errors.ts";
import type { LoginRequest, RegisterRequest, UserResponse } from "../../api/types.ts";

type AuthStatus = "checking" | "authenticated" | "unauthenticated";

type AuthContextValue = {
  error: string | null;
  login: (payload: LoginRequest) => Promise<UserResponse>;
  logout: () => Promise<void>;
  register: (payload: RegisterRequest) => Promise<UserResponse>;
  status: AuthStatus;
  user: UserResponse | null;
};

const AuthContext = createContext<AuthContextValue | null>(null);

type AuthProviderProps = {
  children: ReactNode;
};

export function AuthProvider({ children }: AuthProviderProps) {
  const [status, setStatus] = useState<AuthStatus>("checking");
  const [user, setUser] = useState<UserResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isCurrent = true;

    async function checkSession() {
      try {
        const response = await getCurrentUser();
        if (!isCurrent) {
          return;
        }
        setUser(response.item.user);
        setError(null);
        setStatus("authenticated");
      } catch (sessionError) {
        if (!isCurrent) {
          return;
        }

        setUser(null);
        setStatus("unauthenticated");
        setError(
          sessionError instanceof ApiError && sessionError.status === 401
            ? null
            : "We could not verify your session. Try signing in again.",
        );
      }
    }

    void checkSession();

    return () => {
      isCurrent = false;
    };
  }, []);

  const login = useCallback(async (payload: LoginRequest) => {
    const response = await loginRequest(payload);
    setUser(response.item.user);
    setError(null);
    setStatus("authenticated");
    return response.item.user;
  }, []);

  const register = useCallback(async (payload: RegisterRequest) => {
    const response = await registerRequest(payload);
    setUser(response.item.user);
    setError(null);
    setStatus("authenticated");
    return response.item.user;
  }, []);

  const logout = useCallback(async () => {
    await logoutRequest();
    setUser(null);
    setError(null);
    setStatus("unauthenticated");
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ error, login, logout, register, status, user }),
    [error, login, logout, register, status, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const auth = useContext(AuthContext);
  if (auth === null) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return auth;
}
