type RouteLoadingProps = {
  fullPage?: boolean;
  label?: string;
};

export function RouteLoading({ fullPage = true, label = "Loading" }: RouteLoadingProps) {
  return (
    <div className={fullPage ? "route-loading-shell" : "route-loading-shell inline"}>
      <div className="route-loading" role="status" aria-live="polite">
        <span className="loading-dot" aria-hidden="true" />
        <span>{label}</span>
      </div>
    </div>
  );
}
