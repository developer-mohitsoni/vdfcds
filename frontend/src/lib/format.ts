const megawatts = new Intl.NumberFormat("en-GB", { maximumFractionDigits: 1 });
const percent = new Intl.NumberFormat("en-GB", { maximumFractionDigits: 1 });

export function formatMw(value: number | null): string {
  return value === null ? "—" : `${megawatts.format(value)} MW`;
}

export function formatPercent(value: number | null): string {
  return value === null ? "—" : `${percent.format(value)}%`;
}

export function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
}

export function formatLongDate(value: string): string {
  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
}

export function formatDateTime(value: string | null): string {
  if (!value) return "Unavailable";
  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
    timeZoneName: "short",
  }).format(new Date(value));
}
