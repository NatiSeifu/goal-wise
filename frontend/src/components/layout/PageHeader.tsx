import type { ReactNode } from "react";

type PageHeaderProps = {
  actions?: ReactNode;
  description: string;
  title: string;
  titleId: string;
};

export function PageHeader({ actions, description, title, titleId }: PageHeaderProps) {
  return (
    <header className="page-header">
      <div>
        <h1 id={titleId}>{title}</h1>
        <p>{description}</p>
      </div>
      {actions === undefined ? null : <div className="page-header-actions">{actions}</div>}
    </header>
  );
}
