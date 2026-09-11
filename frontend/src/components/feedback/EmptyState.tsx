import type { ReactNode } from "react";

type EmptyStateProps = {
  action?: ReactNode;
  description?: string;
  title: string;
};

export function EmptyState({ action, description, title }: EmptyStateProps) {
  return (
    <div className="empty-state">
      <h2>{title}</h2>
      {description ? <p>{description}</p> : null}
      {action === undefined ? null : <div className="empty-state-action">{action}</div>}
    </div>
  );
}
