import React from "react";
import { cn } from "@/lib/utils";

interface DictionaryCardProps {
  word: string;
  emoji: string;
  category: string;
  example: string;
  confidence?: number;
}

export default function DictionaryCard({ word, emoji, category, example, confidence = 0.95 }: DictionaryCardProps) {
  return (
    <div className="bg-white border border-border rounded-md p-6 shadow-sm hover:shadow-md transition-all duration-300 group">
      <div className="flex justify-between items-start mb-4">
        <span className="text-[40px]" role="img">{emoji}</span>
        <div className="px-2 py-1 bg-success/10 text-success text-[10px] font-bold rounded-full uppercase tracking-wider">
          {Math.round(confidence * 100)}% Match
        </div>
      </div>
      
      <h3 className="text-[18px] font-semibold text-text-primary mb-1 group-hover:text-accent transition-colors">
        {word}
      </h3>
      <span className="text-[12px] font-medium text-text-muted uppercase tracking-wider block mb-4">
        {category}
      </span>
      
      <div className="pt-4 border-t border-border">
        <p className="text-[13px] text-text-secondary leading-relaxed italic">
          "{example}"
        </p>
      </div>
    </div>
  );
}
