"use client";

import React, { useState, useRef, useEffect } from "react";
import { Command } from "lucide-react";
import { cn } from "@/lib/utils";

interface TranslateInputProps {
  onTranslate: (text: string, simplify: boolean) => void;
  isLoading?: boolean;
}

const EXAMPLES = [
  "The examination was a piece of cake.",
  "He is under the weather today.",
  "She was delighted and on cloud nine.",
  "The new vehicle cost an arm and a leg.",
];

export default function TranslateInput({ onTranslate, isLoading }: TranslateInputProps) {
  const [text, setText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = () => {
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = "auto";
      ta.style.height = `${Math.max(140, ta.scrollHeight)}px`;
    }
  };

  useEffect(() => { adjustHeight(); }, [text]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      if (text.trim() && !isLoading) onTranslate(text, true);
    }
  };

  return (
    <div className="flex flex-col gap-5">
      {/* Title */}
      <div>
        <h2 className="text-xl font-bold text-stone-900">Text → Sign Language</h2>
        <p className="text-[13px] text-stone-500 mt-1 leading-relaxed">
          Type an English sentence and convert it to ISL gloss with emoji visuals.
        </p>
      </div>

      {/* Textarea */}
      <div className="relative">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={"Type a sentence in English...\ne.g. She is going to school today."}
          className={cn(
            "w-full bg-white border-2 border-stone-200 rounded-xl px-4 py-4 text-[15px] leading-relaxed",
            "transition-all duration-200 outline-none resize-none text-stone-800 placeholder:text-stone-400",
            "focus:border-stone-800 focus:ring-4 focus:ring-stone-800/5"
          )}
        />
        {text.length > 0 && (
          <span className="absolute bottom-3 right-4 text-[11px] text-stone-400">{text.length} chars</span>
        )}
      </div>

      {/* Examples */}
      <div className="flex flex-col gap-2">
        <span className="text-[11px] font-bold text-stone-400 uppercase tracking-wider">Quick examples</span>
        <div className="flex flex-wrap gap-1.5">
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              onClick={() => { setText(ex); textareaRef.current?.focus(); }}
              className="text-[12px] px-3 py-1.5 bg-stone-100 hover:bg-stone-200 border border-stone-200 rounded-full transition-colors text-stone-600 hover:text-stone-900 text-left"
            >
              {ex}
            </button>
          ))}
        </div>
      </div>

      {/* Translate Button */}
      <button
        onClick={() => onTranslate(text, true)}
        disabled={!text.trim() || isLoading}
        className={cn(
          "w-full py-4 bg-stone-900 text-white rounded-xl font-semibold text-[15px]",
          "flex items-center justify-center gap-3 transition-all shadow-md",
          "hover:bg-stone-800 hover:shadow-lg active:scale-[0.99]",
          "disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none disabled:active:scale-100"
        )}
      >
        {isLoading ? (
          <>
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            <span>Translating...</span>
          </>
        ) : (
          <span>Translate to Sign Language</span>
        )}
      </button>

      <div className="flex items-center justify-center gap-1.5 text-[11px] text-stone-400">
        <Command size={10} />
        <span>+ Enter to translate quickly</span>
      </div>
    </div>
  );
}
