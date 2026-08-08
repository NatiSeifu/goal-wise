import type { ReactNode } from "react";

type AlertVariant = "error" | "success";

type AlertProps = {
  children: ReactNode;
  title?: string;
  variant: AlertVariant;
};

export function Alert({ children, title, variant }: AlertProps) {
  return (
    <div className={`alert ${variant}`} role={variant === "error" ? "alert" : "status"}>
      {title === undefined ? null : <h2>{title}</h2>}
      <div>{children}</div>
    </div>
  );
}
