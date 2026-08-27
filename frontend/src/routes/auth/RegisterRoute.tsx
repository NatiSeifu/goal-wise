import { useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { ApiError } from "../../api/errors.ts";
import { routes } from "../../app/routes.ts";
import { FormError } from "../../components/feedback/FormError.tsx";
import { RouteLoading } from "../../components/feedback/RouteLoading.tsx";
import { Button } from "../../components/ui/Button.tsx";
import { TextField } from "../../components/ui/TextField.tsx";
import { useAuth } from "../../features/auth/AuthProvider.tsx";

const DEFAULT_TIME_ZONE = "America/Los_Angeles";

function getBrowserTimeZone() {
  return Intl.DateTimeFormat().resolvedOptions().timeZone || DEFAULT_TIME_ZONE;
}

export function RegisterRoute() {
  const auth = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [timeZone, setTimeZone] = useState(getBrowserTimeZone);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (auth.status === "checking") {
    return <RouteLoading label="Checking your session" />;
  }

  if (auth.status === "authenticated") {
    return <Navigate replace to={routes.dashboard} />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await auth.register({ email, password, time_zone: timeZone });
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
          <TextField
            id="register-time-zone"
            label="Time zone"
            name="time-zone"
            onChange={(event) => setTimeZone(event.target.value)}
            required
            type="text"
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
