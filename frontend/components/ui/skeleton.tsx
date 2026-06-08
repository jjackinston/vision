import { cn } from "@/lib/utils";

/* ── Base shimmer ─────────────────────────────────────────────────────── */
export function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-md bg-white/5",
        className,
      )}
      {...props}
    />
  );
}

/* ── KPI card skeleton ────────────────────────────────────────────────── */
export function KpiSkeleton() {
  return (
    <div className="bg-[#111218] border border-white/5 rounded-xl p-5">
      <div className="flex items-center justify-between mb-3">
        <Skeleton className="h-3 w-24" />
        <Skeleton className="h-7 w-7 rounded-lg" />
      </div>
      <Skeleton className="h-8 w-32 mb-1.5" />
      <Skeleton className="h-2.5 w-20" />
    </div>
  );
}

/* ── Table row skeleton ───────────────────────────────────────────────── */
export function TableRowSkeleton({ cols = 5 }: { cols?: number }) {
  return (
    <tr>
      {Array.from({ length: cols }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <Skeleton className="h-3" style={{ width: `${60 + Math.random() * 40}%` }} />
        </td>
      ))}
    </tr>
  );
}

/* ── Card skeleton ────────────────────────────────────────────────────── */
export function CardSkeleton({ lines = 3 }: { lines?: number }) {
  return (
    <div className="bg-[#111218] border border-white/5 rounded-xl p-5 space-y-3">
      <Skeleton className="h-4 w-2/3" />
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton key={i} className="h-3" style={{ width: `${50 + Math.random() * 50}%` }} />
      ))}
    </div>
  );
}

/* ── Full page KPI grid skeleton ─────────────────────────────────────── */
export function KpiGridSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div className={`grid grid-cols-2 xl:grid-cols-${count} gap-4`}>
      {Array.from({ length: count }).map((_, i) => (
        <KpiSkeleton key={i} />
      ))}
    </div>
  );
}
