"use client";

import React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface EmojiCardProps {
  emoji: string;
  word: string;
  role?: string;
  confidence?: number;
  lottie_file?: string;
  alternatives?: string[];
  index: number;
}

export function EmojiCard({
  emoji,
  word,
  role = "UNKNOWN",
  confidence = 1.0,
  index,
}: EmojiCardProps) {
  // Color coding based on semantic role
  const getRoleColor = (role: string) => {
    switch (role.toUpperCase()) {
      case "SUBJECT": return "border-indigo-400 shadow-indigo-400/20";
      case "VERB": return "border-mint-400 shadow-mint-400/20";
      case "OBJECT": return "border-pink-400 shadow-pink-400/20";
      case "TIME": return "border-yellow-400 shadow-yellow-400/20";
      case "LOCATION": return "border-blue-400 shadow-blue-400/20";
      case "NEGATION": return "border-red-400 shadow-red-400/20";
      default: return "border-white/10 shadow-white/5";
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 50, scale: 0.8 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ 
        type: "spring", 
        stiffness: 260, 
        damping: 20, 
        delay: index * 0.15 
      }}
      whileHover={{ scale: 1.05, y: -5 }}
      className={cn(
        "flex flex-col items-center justify-center p-4 rounded-xl",
        "bg-white/5 backdrop-blur-md border-[2px]",
        "transition-colors duration-300 shadow-lg min-w-[120px]",
        getRoleColor(role)
      )}
    >
      <div className="text-6xl mb-2 filter drop-shadow-md">
        {emoji}
      </div>
      <div className="text-sm font-bold tracking-wider text-slate-200">
        {word}
      </div>
      {confidence < 1.0 && (
        <div className="text-[10px] text-slate-400 mt-1">
          {Math.round(confidence * 100)}% match
        </div>
      )}
    </motion.div>
  );
}
