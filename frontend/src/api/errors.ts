export type FieldErrors = Record<string, string[]>;
export type ApiIssue = { row: number; field: string; code: string; message: string };

export type ApiErrorBody = {
  error?: {
    code?: string;
    message?: string;
    fields?: FieldErrors;
    issues?: ApiIssue[];
  };
};

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly fields: FieldErrors | null;
  readonly issues: ApiIssue[];

  constructor({
    status,
    code,
    message,
    fields = null,
    issues = [],
  }: {
    status: number;
    code: string;
    message: string;
    fields?: FieldErrors | null;
    issues?: ApiIssue[];
  }) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.fields = fields;
    this.issues = issues;
  }
}

export function toApiError(status: number, body: unknown) {
  const parsed = isApiErrorBody(body) ? body.error : null;

  return new ApiError({
    status,
    code: parsed?.code ?? "request_failed",
    message: parsed?.message ?? "Request failed. Please try again.",
    fields: parsed?.fields ?? null,
    issues: parsed?.issues ?? [],
  });
}

function isApiErrorBody(value: unknown): value is ApiErrorBody {
  if (value === null || typeof value !== "object" || !("error" in value)) {
    return false;
  }

  const error = (value as ApiErrorBody).error;
  return error === undefined || (error !== null && typeof error === "object");
}
