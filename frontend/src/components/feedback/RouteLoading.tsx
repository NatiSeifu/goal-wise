type RouteLoadingProps = {
  label?: string;
};

export function RouteLoading({ label = "Loading" }: RouteLoadingProps) {
  return (
    <div className="route-loading-shell">
      <div className="route-loading" role="status" aria-live="polite">
        <span className="loading-dot" aria-hidden="true" />
        <span>{label}</span>
      </div>
    </div>
  );
}
