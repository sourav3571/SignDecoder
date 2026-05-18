"use client";

import React, { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

interface NLPAnalysis {
  subject?: string;
  verb?: string;
  object?: string;
  time?: string;
  location?: string;
  negation?: boolean;
}

interface NLPAnalysisTableProps {
  analysis: NLPAnalysis;
}

export default function NLPAnalysisTable({ analysis }: NLPAnalysisTableProps) {
  const [isOpen, setIsOpen] = useState(false);

  const rows = [
    { label: "Subject", value: analysis.subject || "—" },
    { label: "Verb", value: analysis.verb || "—" },
    { label: "Object", value: analysis.object || "—" },
    { label: "Time", value: analysis.time || "—" },
    { label: "Location", value: analysis.location || "—" },
    { label: "Negation", value: analysis.negation ? "YES" : "NO" },
  ];

  return (
    <div className="border-t border-border pt-6">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 text-[13px] text-text-secondary hover:text-text-primary transition-colors"
      >
        <span>Show linguistic analysis</span>
        {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="overflow-hidden"
          >
            <div className="pt-6 grid grid-cols-2 sm:grid-cols-3 gap-6">
              {rows.map((row) => (
                <div key={row.label} className="flex flex-col gap-1">
                  <span className="text-[11px] font-bold text-text-muted uppercase tracking-wider">
                    {row.label}
                  </span>
                  <span className="text-[15px] text-text-primary font-medium">
                    {row.value}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
