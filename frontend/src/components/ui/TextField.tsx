import type { InputHTMLAttributes } from "react";

type TextFieldProps = Omit<InputHTMLAttributes<HTMLInputElement>, "id"> & {
  error?: string;
  id: string;
  label: string;
};

export function TextField({ error, id, label, ...inputProps }: TextFieldProps) {
  const errorId = error === undefined ? undefined : `${id}-error`;

  return (
    <label className="field" htmlFor={id}>
      <span className="field-label">{label}</span>
      <input
        {...inputProps}
        aria-describedby={errorId}
        aria-invalid={error === undefined ? undefined : true}
        className="field-input"
        id={id}
      />
      {error === undefined ? null : (
        <span className="field-error" id={errorId}>
          {error}
        </span>
      )}
    </label>
  );
}
