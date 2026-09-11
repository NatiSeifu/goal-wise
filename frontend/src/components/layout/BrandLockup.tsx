import { Link } from "react-router-dom";

import { routes } from "../../app/routes.ts";

type BrandLockupProps = {
  linked?: boolean;
};

export function BrandLockup({ linked = false }: BrandLockupProps) {
  const content = (
    <>
      <img className="brand-logo" src="/goalwise-main-logo.png" alt="" aria-hidden="true" />
      <span>GoalWise</span>
    </>
  );

  return linked ? (
    <Link className="brand-lockup brand-link" to={routes.landing}>
      {content}
    </Link>
  ) : (
    <div className="brand-lockup" aria-label="GoalWise">
      {content}
    </div>
  );
}
