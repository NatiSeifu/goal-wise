import type { ReactNode } from "react";

type PageShellProps = {
  children: ReactNode;
};

export function PageShell({ children }: PageShellProps) {
  return (
    <main className="page-shell">
      <div className="brand-lockup" aria-label="GoalWise">
        <span className="brand-mark" aria-hidden="true">
          G
        </span>
        <span>GoalWise</span>
      </div>
      {children}
    </main>
  );
}
