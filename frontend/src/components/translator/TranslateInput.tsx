"use client";

import React, { useState, useRef, useEffect } from "react";
import { Command } from "lucide-react";
import { cn } from "@/lib/utils";

interface TranslateInputProps {
  onTranslate: (text: string) => void;
  isLoading?: boolean;
}

const EXAMPLES = [
  "Sourav is eating breakfast",
  "Where is the hospital?",
  "I don't like cold weather",
  "She is happy today"
];

export default function TranslateInput({ onTranslate, isLoading }: TranslateInputProps) {
  const [text, setText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.max(160, textarea.scrollHeight)}px`;
    }
  };

  useEffect(() => {
    adjustHeight();
  }, [text]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      if (text.trim() && !isLoading) {
        onTranslate(text);
      }
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-4">
        <label className="text-[13px] font-bold text-text-muted uppercase tracking-[0.08em]">
          English Text
        </label>
        
        <div className="relative group">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a sentence in English...&#10;e.g. Sourav is eating breakfast at home yesterday"
            className={cn(
              "w-full bg-surface-elevated border border-border rounded-md px-5 py-4 text-[15px] leading-relaxed transition-all duration-200 outline-none resize-none",
              "focus:bg-white focus:border-accent focus:ring-1 focus:ring-accent/10 focus:shadow-sm"
            )}
          />
          <div className="absolute bottom-4 right-5 text-[11px] text-text-muted">
            {text.length} characters
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        <span className="text-[13px] font-medium text-text-secondary">Try an example:</span>
        <div className="flex flex-wrap gap-2">
          {EXAMPLES.map((example) => (
            <button
              key={example}
              onClick={() => {
                setText(example);
                textareaRef.current?.focus();
              }}
              className="text-[13px] px-4 py-1.5 bg-surface-elevated border border-border rounded-full hover:bg-border transition-colors text-text-secondary hover:text-text-primary"
            >
              {example}
            </button>
          ))}
        </div>
      </div>

      <button
        onClick={() => onTranslate(text)}
        disabled={!text.trim() || isLoading}
        className={cn(
          "w-full py-4 bg-accent text-white rounded-md font-medium text-[15px] transition-all flex items-center justify-center gap-3",
          "hover:bg-accent-hover active:scale-[0.99]",
          "disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100"
        )}
      >
        {isLoading ? (
          <>
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            <span>Translating...</span>
          </>
        ) : (
          <span>Translate</span>
        )}
      </button>

      <div className="flex items-center justify-center gap-1.5 text-[11px] text-text-muted">
        <Command size={10} />
        <span>+ Enter to translate</span>
      </div>
    </div>
  );
}
