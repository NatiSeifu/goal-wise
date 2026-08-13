import type { ReactNode } from "react";

type PanelProps = {
  children: ReactNode;
  className?: string;
  title?: string;
  titleId?: string;
};

export function Panel({ children, className, title, titleId }: PanelProps) {
  return (
    <section className={["panel", className].filter(Boolean).join(" ")} aria-labelledby={titleId}>
      {title === undefined ? null : <h2 id={titleId}>{title}</h2>}
      {children}
    </section>
  );
}
