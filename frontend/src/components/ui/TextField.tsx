import type { InputHTMLAttributes } from "react";

type TextFieldProps = Omit<InputHTMLAttributes<HTMLInputElement>, "id"> & {
  description?: string;
  error?: string;
  id: string;
  label: string;
};

export function TextField({ description, error, id, label, ...inputProps }: TextFieldProps) {
  const descriptionId = description === undefined ? undefined : `${id}-description`;
  const errorId = error === undefined ? undefined : `${id}-error`;
  const describedBy = [descriptionId, errorId].filter(Boolean).join(" ") || undefined;

  return (
    <label className="field" htmlFor={id}>
      <span className="field-label">{label}</span>
      <input
        {...inputProps}
        aria-describedby={describedBy}
        aria-invalid={error === undefined ? undefined : true}
        className="field-input"
        id={id}
      />
      {description === undefined ? null : (
        <span className="field-description" id={descriptionId}>
          {description}
        </span>
      )}
      {error === undefined ? null : (
        <span className="field-error" id={errorId}>
          {error}
        </span>
      )}
    </label>
  );
}
