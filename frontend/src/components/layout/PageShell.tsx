import type { ReactNode } from "react";

import { BrandLockup } from "./BrandLockup.tsx";

type PageShellProps = {
  children: ReactNode;
};

export function PageShell({ children }: PageShellProps) {
  return (
    <main className="page-shell">
      <BrandLockup />
      {children}
    </main>
  );
}
