type ProgressBarProps = {
  label: string;
  value: number;
};

export function ProgressBar({ label, value }: ProgressBarProps) {
  const boundedValue = Math.max(0, Math.min(100, value));

  return (
    <div className="progress-block">
      <div className="progress-label-row">
        <span>{label}</span>
        <span>{boundedValue.toFixed(0)}%</span>
      </div>
      <div
        className="progress-track"
        role="progressbar"
        aria-label={label}
        aria-valuemax={100}
        aria-valuemin={0}
        aria-valuenow={boundedValue}
      >
        <span className="progress-fill" style={{ width: `${boundedValue}%` }} />
      </div>
    </div>
  );
}
