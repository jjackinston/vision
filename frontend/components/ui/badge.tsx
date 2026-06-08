import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-purple-600/20 text-purple-300 hover:bg-purple-600/30",
        secondary:
          "border-transparent bg-white/10 text-white/70 hover:bg-white/15",
        destructive:
          "border-transparent bg-red-500/20 text-red-400 hover:bg-red-500/30",
        outline:
          "border-white/20 text-white/70",
        success:
          "border-transparent bg-emerald-500/20 text-emerald-400",
        warning:
          "border-transparent bg-amber-500/20 text-amber-400",
        info:
          "border-transparent bg-blue-500/20 text-blue-400",
        purple:
          "border-transparent bg-purple-500/20 text-purple-300",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
