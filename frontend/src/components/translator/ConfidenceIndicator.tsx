"use client";

import React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface ConfidenceIndicatorProps {
  score: number; // 0 to 1
}

export default function ConfidenceIndicator({ score }: ConfidenceIndicatorProps) {
  const percentage = Math.round(score * 100);
  
  const getColor = (s: number) => {
    if (s >= 0.8) return "bg-success";
    if (s >= 0.5) return "bg-warning";
    return "bg-danger";
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex justify-between items-center text-[13px] text-text-secondary">
        <span>Translation confidence</span>
        <span className="font-medium text-text-primary">{percentage}%</span>
      </div>
      <div className="h-1 w-full bg-border rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          className={cn("h-full rounded-full", getColor(score))}
        />
      </div>
    </div>
  );
}
