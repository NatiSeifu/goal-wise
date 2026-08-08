import type { SelectHTMLAttributes } from "react";

type SelectFieldProps = Omit<SelectHTMLAttributes<HTMLSelectElement>, "id"> & {
  error?: string;
  id: string;
  label: string;
  options: Array<{ label: string; value: string }>;
};

export function SelectField({ error, id, label, options, ...selectProps }: SelectFieldProps) {
  const errorId = error === undefined ? undefined : `${id}-error`;

  return (
    <label className="field" htmlFor={id}>
      <span className="field-label">{label}</span>
      <select
        {...selectProps}
        aria-describedby={errorId}
        aria-invalid={error === undefined ? undefined : true}
        className="field-input"
        id={id}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error === undefined ? null : (
        <span className="field-error" id={errorId}>
          {error}
        </span>
      )}
    </label>
  );
}
