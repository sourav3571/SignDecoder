"use client";

import React from "react";
import { motion } from "framer-motion";

export function LoadingState({ status }: { status?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-6">
      <div className="relative w-12 h-12">
        <div className="absolute inset-0 border-2 border-border rounded-full" />
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
          className="absolute inset-0 border-2 border-transparent border-t-accent rounded-full"
        />
      </div>
      <p className="text-[15px] text-text-secondary font-medium animate-pulse">
        {status || "Analyzing language..."}
      </p>
    </div>
  );
}

export function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-6 border-2 border-dashed border-border rounded-md">
      <div className="w-12 h-12 bg-surface-elevated rounded-full flex items-center justify-center mb-4 text-text-muted">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          <path d="m8 9 3 3 3-3" />
        </svg>
      </div>
      <p className="text-[15px] text-text-secondary text-center max-w-[280px]">
        Your translation will appear here once you enter some text.
      </p>
    </div>
  );
}
