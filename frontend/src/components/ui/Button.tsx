import { Link, type LinkProps } from "react-router-dom";
import type { ButtonHTMLAttributes } from "react";

type ButtonVariant = "danger" | "primary" | "secondary";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
};

type ButtonLinkProps = LinkProps & {
  variant?: ButtonVariant;
};

export function Button({ className, variant = "primary", ...buttonProps }: ButtonProps) {
  return <button {...buttonProps} className={buttonClassName(variant, className)} />;
}

export function ButtonLink({ className, variant = "secondary", ...linkProps }: ButtonLinkProps) {
  return <Link {...linkProps} className={buttonClassName(variant, className)} />;
}

function buttonClassName(variant: ButtonVariant, className?: string) {
  return ["button", variant, className].filter(Boolean).join(" ");
}
