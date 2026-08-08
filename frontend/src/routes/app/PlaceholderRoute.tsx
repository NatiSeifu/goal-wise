type PlaceholderRouteProps = {
  title: string;
  description: string;
};

export function PlaceholderRoute({ title, description }: PlaceholderRouteProps) {
  return (
    <section className="route-panel" aria-labelledby="route-title">
      <h1 id="route-title">{title}</h1>
      <p>{description}</p>
      <p className="route-boundary">
        Placeholder only. The next slices render backend-owned data for this workflow.
      </p>
    </section>
  );
}
