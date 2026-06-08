"use client";

import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
  compact?: boolean;
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  className,
  compact = false,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center text-center",
        compact ? "py-8 px-4" : "py-16 px-8",
        className,
      )}
    >
      {Icon && (
        <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center mb-4">
          <Icon className="w-6 h-6 text-white/20" />
        </div>
      )}
      <p className={cn("font-semibold text-white/60", compact ? "text-sm" : "text-base")}>
        {title}
      </p>
      {description && (
        <p className={cn("text-white/30 mt-1 max-w-xs", compact ? "text-xs" : "text-sm")}>
          {description}
        </p>
      )}
      {action && (
        <Button
          size="sm"
          onClick={action.onClick}
          className="mt-4 bg-violet-600 hover:bg-violet-500"
        >
          {action.label}
        </Button>
      )}
    </div>
  );
}

/* ── Table empty state ────────────────────────────────────────────────── */
export function EmptyTableRow({
  cols,
  icon: Icon,
  message = "No data yet",
}: {
  cols: number;
  icon?: LucideIcon;
  message?: string;
}) {
  return (
    <tr>
      <td colSpan={cols} className="px-4 py-12 text-center">
        <div className="flex flex-col items-center gap-2">
          {Icon && <Icon className="w-6 h-6 text-white/15" />}
          <p className="text-sm text-white/30">{message}</p>
        </div>
      </td>
    </tr>
  );
}
