import { useState, type FormEvent } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";

import { ApiError } from "../../api/errors.ts";
import { routes } from "../../app/routes.ts";
import { BrandLockup } from "../../components/layout/BrandLockup.tsx";
import { FormError } from "../../components/feedback/FormError.tsx";
import { RouteLoading } from "../../components/feedback/RouteLoading.tsx";
import { Button } from "../../components/ui/Button.tsx";
import { TextField } from "../../components/ui/TextField.tsx";
import { AuthBrandMark } from "../../components/auth/AuthBrandMark.tsx";
import { type AuthRedirectState } from "../../features/auth/RequireAuth.tsx";
import { useAuth } from "../../features/auth/AuthProvider.tsx";

export function LoginRoute() {
  const auth = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const redirectState = location.state as AuthRedirectState | null;
  const destination =
    redirectState?.from === undefined
      ? routes.dashboard
      : `${redirectState.from.pathname}${redirectState.from.search}`;
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);

  if (auth.status === "checking") {
    return <RouteLoading label="Checking your session" />;
  }

  if (auth.status === "authenticated" && !isSubmitting && !isTransitioning) {
    return <Navigate replace to={routes.dashboard} />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await auth.login({ email, password });
      setIsTransitioning(true);
      window.setTimeout(() => navigate(destination, { replace: true }), 760);
    } catch (loginError) {
      setError(
        loginError instanceof ApiError
          ? loginError.status === 401
            ? "Email or password is not correct."
            : loginError.message
          : "We could not sign you in. Check your details and try again.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className={`auth-page${isTransitioning ? " auth-page-transitioning" : ""}`}>
      <aside className="auth-brand-panel" aria-label="GoalWise overview">
        <div className="auth-brand-panel-header"><BrandLockup linked /></div>
        <div className="auth-brand-copy">
          <p className="auth-kicker">PLAN · TRACK · ACHIEVE</p>
          <h2>Know what you can spend.<br /><span>Stay on track for what matters.</span></h2>
          <p>Goal-based budgeting without the guesswork.</p>
        </div>
        <AuthBrandMark />
        <p className="auth-brand-footer">A more intentional<br />tomorrow.</p>
      </aside>
      <section className="auth-panel" aria-labelledby="login-title">
        <div>
          <div className="auth-form-brand"><AuthBrandMark /><span>GoalWise</span></div>
          <h1 id="login-title">Sign in</h1>
          <p className="auth-subtitle">Welcome back.</p>
        </div>
        <form className="auth-form" onSubmit={(event) => void handleSubmit(event)}>
          <FormError message={error ?? auth.error} />
          <TextField
            autoComplete="email"
            id="login-email"
            label="Email"
            name="email"
            onChange={(event) => setEmail(event.target.value)}
            required
            type="email"
            value={email}
          />
          <TextField
            autoComplete="current-password"
            id="login-password"
            label="Password"
            minLength={12}
            name="password"
            onChange={(event) => setPassword(event.target.value)}
            required
            type="password"
            value={password}
          />
          <Button className="auth-submit" disabled={isSubmitting} type="submit">
            {isSubmitting ? "Signing in" : "Sign in"}
          </Button>
        </form>
        <p className="auth-switch">
          Need an account? <Link to={routes.register}>Create one</Link>
        </p>
      </section>
    </main>
  );
}
