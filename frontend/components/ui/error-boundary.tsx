"use client";

import React from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Props {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  /** If provided, shown above the default error card */
  label?: string;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error("[ErrorBoundary]", error, info.componentStack);
  }

  reset = () => this.setState({ hasError: false, error: undefined });

  render() {
    if (!this.state.hasError) return this.props.children;
    if (this.props.fallback) return this.props.fallback;

    return (
      <div className="flex flex-col items-center justify-center py-16 px-8 text-center">
        <div className="w-12 h-12 rounded-xl bg-red-500/10 flex items-center justify-center mb-4">
          <AlertTriangle className="w-6 h-6 text-red-400" />
        </div>
        <p className="text-sm font-semibold text-white/60 mb-1">
          {this.props.label ?? "Something went wrong"}
        </p>
        <p className="text-xs text-white/30 max-w-xs mb-4">
          {this.state.error?.message ?? "An unexpected error occurred in this section."}
        </p>
        <Button
          size="sm"
          variant="outline"
          onClick={this.reset}
          className="border-white/10 bg-white/5 text-white/50 hover:text-white"
        >
          <RefreshCw className="w-3 h-3 mr-1.5" />
          Try again
        </Button>
      </div>
    );
  }
}

/* ── Convenience wrapper ──────────────────────────────────────────────── */
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  label?: string,
) {
  const Wrapped = (props: P) => (
    <ErrorBoundary label={label}>
      <Component {...props} />
    </ErrorBoundary>
  );
  Wrapped.displayName = `withErrorBoundary(${Component.displayName ?? Component.name})`;
  return Wrapped;
}
