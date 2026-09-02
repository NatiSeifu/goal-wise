import { useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { ApiError } from "../../api/errors.ts";
import { routes } from "../../app/routes.ts";
import { FormError } from "../../components/feedback/FormError.tsx";
import { RouteLoading } from "../../components/feedback/RouteLoading.tsx";
import { Button } from "../../components/ui/Button.tsx";
import { SelectField } from "../../components/ui/SelectField.tsx";
import { TextField } from "../../components/ui/TextField.tsx";
import { useAuth } from "../../features/auth/AuthProvider.tsx";

const DEFAULT_TIME_ZONE = "America/Los_Angeles";
const timeZoneOptions = [
  { label: "Pacific Time (Los Angeles)", value: "America/Los_Angeles" },
  { label: "Mountain Time (Denver)", value: "America/Denver" },
  { label: "Central Time (Chicago)", value: "America/Chicago" },
  { label: "Eastern Time (New York)", value: "America/New_York" },
  { label: "Atlantic Time (Halifax)", value: "America/Halifax" },
  { label: "UTC", value: "UTC" },
  { label: "Western European Time (London)", value: "Europe/London" },
  { label: "Central European Time (Berlin)", value: "Europe/Berlin" },
  { label: "Eastern European Time (Athens)", value: "Europe/Athens" },
  { label: "India Standard Time (Kolkata)", value: "Asia/Kolkata" },
  { label: "China Standard Time (Shanghai)", value: "Asia/Shanghai" },
  { label: "Japan Standard Time (Tokyo)", value: "Asia/Tokyo" },
  { label: "Australian Eastern Time (Sydney)", value: "Australia/Sydney" },
  { label: "New Zealand Time (Auckland)", value: "Pacific/Auckland" },
];

function getBrowserTimeZone() {
  const browserTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  return timeZoneOptions.some((option) => option.value === browserTimeZone)
    ? browserTimeZone
    : DEFAULT_TIME_ZONE;
}

export function RegisterRoute() {
  const auth = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [timeZone, setTimeZone] = useState(getBrowserTimeZone);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [registrationCompleted, setRegistrationCompleted] = useState(false);

  if (auth.status === "checking") {
    return <RouteLoading label="Checking your session" />;
  }

  if (auth.status === "authenticated" && !registrationCompleted) {
    return <Navigate replace to={routes.dashboard} />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await auth.register({ email, password, time_zone: timeZone });
      setRegistrationCompleted(true);
      navigate(routes.goal, { replace: true });
    } catch (registerError) {
      setError(
        registerError instanceof ApiError
          ? registerError.status === 409
            ? "An account with this email already exists."
            : registerError.message
          : "We could not create the account. Check your details and try again.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-panel" aria-labelledby="register-title">
        <div>
          <Link className="brand-lockup brand-link" to={routes.landing}>
            <span className="brand-mark" aria-hidden="true">
              G
            </span>
            <span>GoalWise</span>
          </Link>
          <h1 id="register-title">Create account</h1>
          <p className="auth-copy">
            Start with one active goal and a few planning assumptions.
          </p>
        </div>
        <form className="auth-form" onSubmit={(event) => void handleSubmit(event)}>
          <FormError message={error ?? auth.error} />
          <TextField
            autoComplete="email"
            id="register-email"
            label="Email"
            name="email"
            onChange={(event) => setEmail(event.target.value)}
            required
            type="email"
            value={email}
          />
          <TextField
            autoComplete="new-password"
            id="register-password"
            label="Password"
            minLength={12}
            name="password"
            onChange={(event) => setPassword(event.target.value)}
            required
            type="password"
            value={password}
          />
          <SelectField
            id="register-time-zone"
            label="Time zone"
            name="time-zone"
            onChange={(event) => setTimeZone(event.target.value)}
            options={timeZoneOptions}
            required
            value={timeZone}
          />
          <Button className="auth-submit" disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating account" : "Create account"}
          </Button>
        </form>
        <p className="auth-switch">
          Already have an account? <Link to={routes.login}>Sign in</Link>
        </p>
      </section>
    </main>
  );
}
