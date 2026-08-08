import { NavLink, Outlet } from "react-router-dom";

import { routes } from "../../app/routes.ts";

const navItems = [
  { href: routes.dashboard, label: "Dashboard" },
  { href: routes.goal, label: "Goal" },
  { href: routes.financialInputs, label: "Inputs" },
  { href: routes.calculation, label: "Calculation" },
];

export function AppShell() {
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
        <p className="sidebar-note">
          MVP scope: one active goal, manual inputs, deterministic backend calculations.
        </p>
      </aside>
      <main className="workspace">
        <Outlet />
      </main>
    </div>
  );
}
