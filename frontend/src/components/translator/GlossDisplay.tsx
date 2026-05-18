"use client";

import React, { useState, useEffect } from "react";
import { Copy, Check } from "lucide-react";
import { motion } from "framer-motion";

interface GlossDisplayProps {
  glosses: string[];
}

export default function GlossDisplay({ glosses }: GlossDisplayProps) {
  const [copied, setCopied] = useState(false);
  const [displayText, setDisplayText] = useState("");
  const fullText = glosses.map(g => `[${g.toUpperCase()}]`).join(" ");

  useEffect(() => {
    let current = 0;
    const interval = setInterval(() => {
      if (current <= fullText.length) {
        setDisplayText(fullText.substring(0, current));
        current++;
      } else {
        clearInterval(interval);
      }
    }, 20);
    return () => clearInterval(interval);
  }, [fullText]);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="group relative">
      <div className="flex items-center justify-between mb-4">
        <span className="text-[11px] font-bold text-text-muted uppercase tracking-[0.08em]">
          Sign Language Gloss
        </span>
      </div>
      
      <div className="relative overflow-hidden bg-surface-elevated border-l-[3px] border-accent rounded-sm px-6 py-5">
        <p className="font-mono text-[18px] text-text-primary tracking-wide min-h-[1.5em]">
          {displayText}
          <motion.span
            animate={{ opacity: [1, 0] }}
            transition={{ repeat: Infinity, duration: 0.8 }}
            className="inline-block w-1 h-5 bg-accent ml-1 align-middle"
          />
        </p>

        <button
          onClick={copyToClipboard}
          className="absolute top-4 right-4 p-2 text-text-muted hover:text-text-primary transition-colors bg-white/50 backdrop-blur-sm rounded-sm"
          title="Copy gloss string"
        >
          {copied ? <Check size={14} className="text-success" /> : <Copy size={14} />}
        </button>
      </div>
    </div>
  );
}
