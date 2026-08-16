type FormErrorProps = {
  message: string | null;
};

export function FormError({ message }: FormErrorProps) {
  if (message === null) {
    return null;
  }

  return (
    <p className="form-error" role="alert">
      {message}
    </p>
  );
}
