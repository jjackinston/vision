"use client";

/**
 * Sheet — slide-in overlay panel built on @radix-ui/react-dialog.
 * Usage: <Sheet open={open} onClose={onClose} side="left">...</Sheet>
 */

import * as React from "react";
import * as Dialog from "@radix-ui/react-dialog";
import { cn } from "@/lib/utils";
import { X } from "lucide-react";

type Side = "left" | "right" | "bottom";

interface SheetProps {
  open: boolean;
  onClose: () => void;
  side?: Side;
  className?: string;
  children: React.ReactNode;
  /** Show the × close button in the top-right corner */
  showClose?: boolean;
}

const slideIn: Record<Side, string> = {
  left:   "inset-y-0 left-0 h-full w-[280px] sm:w-[320px] data-[state=open]:animate-sheet-in-left  data-[state=closed]:animate-sheet-out-left",
  right:  "inset-y-0 right-0 h-full w-[280px] sm:w-[320px] data-[state=open]:animate-sheet-in-right data-[state=closed]:animate-sheet-out-right",
  bottom: "inset-x-0 bottom-0 w-full rounded-t-2xl        data-[state=open]:animate-sheet-in-bottom data-[state=closed]:animate-sheet-out-bottom",
};

export function Sheet({
  open, onClose, side = "left", className, children, showClose = true,
}: SheetProps) {
  return (
    <Dialog.Root open={open} onOpenChange={(v) => !v && onClose()}>
      <Dialog.Portal>
        {/* Backdrop */}
        <Dialog.Overlay
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm
            data-[state=open]:animate-fade-in data-[state=closed]:animate-fade-out"
        />
        {/* Panel */}
        <Dialog.Content
          className={cn(
            "fixed z-50 bg-[#0D0E12] border border-white/8 shadow-2xl",
            "focus:outline-none overflow-y-auto",
            slideIn[side],
            className,
          )}
          aria-describedby={undefined}
        >
          {showClose && (
            <Dialog.Close
              className="absolute top-4 right-4 p-1.5 rounded-lg text-gray-500
                hover:text-white hover:bg-white/10 transition-all z-10"
              aria-label="Close"
            >
              <X className="w-4 h-4" />
            </Dialog.Close>
          )}
          {children}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
