import { useEffect, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";

import { routes } from "../../app/routes.ts";

export type SetupStepId = "dashboard" | "expenses" | "goal" | "income" | "profile";

type SetupStep = {
  body: string;
  id: SetupStepId;
  label: string;
  to: string;
};

type SetupGuideProps = {
  activeStep: SetupStepId;
  completedSteps?: SetupStepId[];
  compact?: boolean;
};

type CoachTipProps = {
  children: ReactNode;
  title: string;
};

const SETUP_GUIDE_DISMISSED_KEY = "goalwise.setupGuide.dismissed";

const setupSteps: SetupStep[] = [
  {
    body: "Name the target, amount, saved balance, and deadline.",
    id: "goal",
    label: "Goal",
    to: routes.goal,
  },
  {
    body: "Add your current cash position and reserve buffer.",
    id: "profile",
    label: "Cash",
    to: routes.financialInputs,
  },
  {
    body: "Enter expected money coming in before the deadline.",
    id: "income",
    label: "Income",
    to: routes.financialInputs,
  },
  {
    body: "Add known expenses that will happen before the goal date.",
    id: "expenses",
    label: "Expenses",
    to: routes.financialInputs,
  },
  {
    body: "Review the calculated safe-to-spend number.",
    id: "dashboard",
    label: "Dashboard",
    to: routes.dashboard,
  },
];

export function SetupGuide({ activeStep, completedSteps = [], compact = false }: SetupGuideProps) {
  const [isDismissed, setIsDismissed] = useState(() => readDismissedState());

  useEffect(() => {
    setIsDismissed(readDismissedState());
  }, []);

  const completed = new Set(completedSteps);
  const activeIndex = setupSteps.findIndex((step) => step.id === activeStep);

  function dismissGuide() {
    window.localStorage.setItem(SETUP_GUIDE_DISMISSED_KEY, "true");
    setIsDismissed(true);
  }

  function showGuide() {
    window.localStorage.removeItem(SETUP_GUIDE_DISMISSED_KEY);
    setIsDismissed(false);
  }

  if (isDismissed) {
    return (
      <div className="setup-guide-return">
        <button type="button" onClick={showGuide}>
          Show setup guide
        </button>
      </div>
    );
  }

  return (
    <section className={compact ? "setup-guide compact" : "setup-guide"} aria-labelledby="setup-guide-title">
      <div className="setup-guide-copy">
        <h2 id="setup-guide-title">Get to your first safe-to-spend number</h2>
        <p>
          Follow these steps once. GoalWise will use the saved inputs to calculate your weekly plan.
        </p>
      </div>
      <ol className="setup-steps" aria-label="GoalWise setup steps">
        {setupSteps.map((step, index) => {
          const isActive = step.id === activeStep;
          const isComplete = completed.has(step.id) || index < activeIndex;
          return (
            <li className={setupStepClassName({ isActive, isComplete })} key={step.id}>
              <Link to={step.to}>
                <span className="setup-step-marker" aria-hidden="true">
                  {isComplete ? "OK" : index + 1}
                </span>
                <span>
                  <span className="setup-step-title">{step.label}</span>
                  <span className="screen-reader-only">
                    {isActive ? "Current step. " : null}
                    {isComplete ? "Completed. " : null}
                  </span>
                  <span className="setup-step-body">{step.body}</span>
                </span>
              </Link>
            </li>
          );
        })}
      </ol>
      <button className="setup-guide-dismiss" type="button" onClick={dismissGuide}>
        Hide guide
      </button>
    </section>
  );
}

export function CoachTip({ children, title }: CoachTipProps) {
  return (
    <aside className="coach-tip" aria-label={title}>
      <strong>{title}</strong>
      <p>{children}</p>
    </aside>
  );
}

function setupStepClassName({
  isActive,
  isComplete,
}: {
  isActive: boolean;
  isComplete: boolean;
}) {
  return [
    "setup-step",
    isActive ? "active" : undefined,
    isComplete ? "complete" : undefined,
  ]
    .filter(Boolean)
    .join(" ");
}

function readDismissedState() {
  if (typeof window === "undefined") {
    return false;
  }
  return window.localStorage.getItem(SETUP_GUIDE_DISMISSED_KEY) === "true";
}
