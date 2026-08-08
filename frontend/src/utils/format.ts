import type { IsoDate, IsoDateTime } from "../api/types.ts";

const currencyFormatter = new Intl.NumberFormat("en-US", {
  currency: "USD",
  maximumFractionDigits: 0,
  style: "currency",
});

const dateFormatter = new Intl.DateTimeFormat("en-US", {
  dateStyle: "medium",
  timeZone: "UTC",
});

const dateTimeFormatter = new Intl.DateTimeFormat("en-US", {
  dateStyle: "medium",
  timeStyle: "short",
});

export function formatCents(cents: number) {
  return currencyFormatter.format(cents / 100);
}

export function formatDate(date: IsoDate) {
  return dateFormatter.format(new Date(`${date}T00:00:00Z`));
}

export function formatDateTime(dateTime: IsoDateTime | null) {
  if (dateTime === null) {
    return "Not available";
  }
  return dateTimeFormatter.format(new Date(dateTime));
}

export function formatPercent(value: number) {
  return `${value.toFixed(0)}%`;
}
