import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { routes } from "../../app/routes.ts";
import { Button } from "../ui/Button.tsx";
import { useAuth } from "../../features/auth/AuthProvider.tsx";

const navItems = [
  { href: routes.dashboard, label: "Dashboard" },
  { href: routes.goal, label: "Goal" },
  { href: routes.financialInputs, label: "Inputs" },
  { href: routes.calculation, label: "Calculation" },
];

export function AppShell() {
  const { logout, user } = useAuth();
  const navigate = useNavigate();
  const [logoutError, setLogoutError] = useState<string | null>(null);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  async function handleLogout() {
    setLogoutError(null);
    setIsLoggingOut(true);

    try {
      await logout();
      navigate(routes.login, { replace: true });
    } catch {
      setLogoutError("We could not sign you out. Try again.");
    } finally {
      setIsLoggingOut(false);
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="GoalWise app navigation">
        <NavLink className="brand-lockup brand-link" to={routes.landing}>
          <span className="brand-mark" aria-hidden="true">
            G
          </span>
          <span>GoalWise</span>
        </NavLink>
        <nav className="sidebar-nav" aria-label="Primary">
          {navItems.map((item) => (
            <NavLink
              className={({ isActive }) => (isActive ? "sidebar-link active" : "sidebar-link")}
              key={item.href}
              to={item.href}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-account">
          <p className="sidebar-user">{user?.email}</p>
          {logoutError === null ? null : (
            <p className="sidebar-error" role="alert">
              {logoutError}
            </p>
          )}
          <Button
            className="sidebar-logout"
            disabled={isLoggingOut}
            variant="secondary"
            type="button"
            onClick={() => void handleLogout()}
          >
            {isLoggingOut ? "Signing out" : "Sign out"}
          </Button>
        </div>
      </aside>
      <main className="workspace">
        <Outlet />
      </main>
    </div>
  );
}
