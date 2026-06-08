"use client";
import Link from "next/link";
import { Search, Home, ArrowLeft } from "lucide-react";

export default function NotFound() {
  return (
    <div className="bg-[#0D0E13] min-h-screen flex items-center justify-center p-8">
      <div className="text-center max-w-md">
        <p className="text-[120px] font-black text-white/5 leading-none select-none mb-4">404</p>
        <div className="w-14 h-14 rounded-2xl bg-violet-500/10 flex items-center justify-center mx-auto -mt-6 mb-6">
          <Search className="w-7 h-7 text-violet-400" />
        </div>
        <h1 className="text-2xl font-bold text-white mb-2">Page not found</h1>
        <p className="text-white/40 text-sm mb-8">
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
        </p>
        <div className="flex gap-3 justify-center">
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-1.5 bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            <Home className="w-3.5 h-3.5" />
            Dashboard
          </Link>
          <button
            onClick={() => window.history.back()}
            className="inline-flex items-center gap-1.5 bg-white/5 hover:bg-white/10 border border-white/10 text-white/60 hover:text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Go back
          </button>
        </div>
      </div>
    </div>
  );
}
