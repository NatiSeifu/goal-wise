import type { FieldErrors } from "../api/errors.ts";

export function fieldError(fields: FieldErrors, name: string) {
  return fields[name]?.[0];
}

export function firstFormError(fields: FieldErrors) {
  const [firstError] = Object.values(fields).flat();
  return firstError ?? null;
}
