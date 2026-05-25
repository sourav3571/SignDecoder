"use client";

import React, { useState } from "react";
import TranslateInput from "@/components/translator/TranslateInput";
import GlossDisplay from "@/components/translator/GlossDisplay";
import GlossToEmojiConverter from "@/components/translator/GlossToEmojiConverter";
import EmojiCard, { SemanticRole } from "@/components/translator/EmojiCard";
import { LoadingState, EmptyState } from "@/components/translator/States";
import { Play } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface TranslationResult {
  glosses: string[];
  cards: {
    emoji: string;
    word: string;
    role: SemanticRole;
    lottieSrc?: string;
  }[];
  confidence: number;
  analysis: {
    subject?: string;
    verb?: string;
    object?: string;
    time?: string;
    location?: string;
    negation?: boolean;
  };
  reconstructed: string;
}

const resolveRole = (tokenText: string, roles: Record<string, string[]>): SemanticRole => {
  const cleanWord = tokenText.toLowerCase().replace(/[.,\/#!$%\^&\*;:{}=\-_`~()?]/g, "");
  for (const [roleKey, words] of Object.entries(roles || {})) {
    const list = Array.isArray(words) ? words : [];
    if (list.some(w => w.toLowerCase().replace(/[.,\/#!$%\^&\*;:{}=\-_`~()?]/g, "") === cleanWord)) {
      const upperKey = roleKey.toUpperCase();
      if (upperKey === "SUBJECT") return "SUBJECT";
      if (upperKey === "VERB" || upperKey === "AUXILIARY") return "VERB";
      if (upperKey === "OBJECT" || upperKey === "INDIRECT_OBJECT" || upperKey === "MODIFIER") return "OBJECT";
      if (upperKey === "TIME") return "TIME";
      if (upperKey === "LOCATION") return "LOCATION";
      if (upperKey === "NEGATION") return "NEGATION";
    }
  }

  const upperWord = tokenText.toUpperCase().replace(/[.,\/#!$%\^&\*;:{}=\-_`~()?]/g, "");
  if (["I", "YOU", "HE", "SHE", "WE", "THEY", "MY", "YOUR", "HIS", "HER", "OUR", "THEIR", "ME", "US", "THEM"].includes(upperWord)) return "SUBJECT";
  if (["YESTERDAY", "TODAY", "TOMORROW", "MORNING", "NIGHT", "AFTERNOON", "EVENING", "WEEK", "YEAR", "MONTH", "NOW"].includes(upperWord)) return "TIME";
  if (["HOME", "SCHOOL", "BANK", "OFFICE", "SHOP", "BEACH", "STORE", "CITY", "HOSPITAL", "MARKET", "HOUSE", "RESTROOM"].includes(upperWord)) return "LOCATION";
  if (["NOT", "NEVER", "NO", "DONT", "CANT", "WONT"].includes(upperWord)) return "NEGATION";
  if (["EAT", "GO", "WENT", "RUN", "PLAY", "COOK", "TRAVEL", "SEE", "LOOK", "BUY", "WORK", "STUDY", "LIKE", "LOVE", "DRINK", "SLEEP", "WALK", "DRIVE"].includes(upperWord)) return "VERB";

  return "OBJECT";
};

export default function TranslatorPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<TranslationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeCardIndex, setActiveCardIndex] = useState(-1);
  const [isPlaying, setIsPlaying] = useState(false);

  const handleTranslate = async (text: string) => {
    setIsLoading(true);
    setResult(null);
    setError(null);
    setActiveCardIndex(-1);

    try {
      const response = await fetch("/api/v1/translate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text,
          sign_language: "ISL",
          include_details: true,
        }),
      });

      const responseBody = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(responseBody?.detail || `Translation failed (${response.status})`);
      }

      const data = responseBody;
      const semanticRoles = data.analysis?.semantic_roles || {};
      
      const englishCards = (data.analysis?.tokens && data.analysis.tokens.length > 0
        ? data.analysis.tokens
        : text.split(/\s+/).filter(Boolean).map((w: string) => ({ text: w, emoji: "❓" }))
      ).map((token: any) => {
        const wordText = token.text;
        return {
          emoji: token.emoji || "❓",
          word: wordText,
          role: resolveRole(wordText, semanticRoles),
          lottieSrc: undefined,
        };
      });

      const mappedResult: TranslationResult = {
        glosses: (data.gloss_string || "").split(" ").map((g: string) => g.replace(/[\[\]]/g, "")).filter(Boolean),
        cards: englishCards,
        confidence: data.confidence_score ?? 0,
        analysis: {
          subject: data.analysis?.semantic_roles?.subject?.[0] || data.analysis?.semantic_roles?.SUBJECT?.[0],
          verb: data.analysis?.semantic_roles?.verb?.[0] || data.analysis?.semantic_roles?.VERB?.[0],
          object: data.analysis?.semantic_roles?.object?.[0] || data.analysis?.semantic_roles?.OBJECT?.[0],
          time: data.analysis?.semantic_roles?.time?.[0] || data.analysis?.semantic_roles?.TIME?.[0],
          location: data.analysis?.semantic_roles?.location?.[0] || data.analysis?.semantic_roles?.LOCATION?.[0],
          negation: (data.analysis?.semantic_roles?.negation?.length > 0) || (data.analysis?.semantic_roles?.NEGATION?.length > 0),
        },
        reconstructed: data.preprocessed_text || text,
      };

      setResult(mappedResult);
      setIsLoading(false);
      setTimeout(() => startSequence(), 1000);
    } catch (error) {
      console.error("Translation error:", error);
      setIsLoading(false);
      setError(error instanceof Error ? error.message : "Translation failed. Please try again.");
    }
  };

  const startSequence = () => {
    setActiveCardIndex(0);
    setIsPlaying(true);
  };

  const handleAnimationComplete = () => {
    if (result && activeCardIndex < result.cards.length - 1) {
      setActiveCardIndex(prev => prev + 1);
    } else {
      setActiveCardIndex(-1);
      setIsPlaying(false);
    }
  };

  return (
    <div className="pt-24 min-h-screen bg-stone-50/40">
      <div className="max-w-[1200px] mx-auto h-[calc(100vh-96px)] flex flex-col md:flex-row">
        {/* Left Panel (Input) */}
        <div className="w-full md:w-[40%] p-6 md:p-12 overflow-y-auto">
          <TranslateInput onTranslate={handleTranslate} isLoading={isLoading} />
        </div>

        {/* Divider */}
        <div className="hidden md:block w-[1px] bg-stone-200 self-stretch" />

        {/* Right Panel (Output) */}
        <div className="w-full md:w-[60%] p-6 md:p-12 overflow-y-auto bg-stone-50/20">
          <div className="flex flex-col gap-10">
            {error && (
              <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}
            <AnimatePresence mode="wait">
              {isLoading ? (
                <motion.div
                  key="loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <LoadingState status="Mapping words to visual signs..." />
                </motion.div>
              ) : result ? (
                <motion.div
                  key="result"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex flex-col gap-12"
                >
                  {/* Gloss Output */}
                  <GlossDisplay glosses={result.glosses} />

                  {/* Visual Representation (No Emojis) */}
                  <div>
                    <div className="flex items-center justify-between mb-6">
                      <span className="text-[11px] font-bold text-text-muted uppercase tracking-[0.08em]">
                        Visual Representation
                      </span>
                      <button
                        onClick={startSequence}
                        disabled={isPlaying}
                        className="flex items-center gap-2 text-[13px] font-medium text-accent hover:text-accent-hover transition-colors disabled:opacity-50"
                      >
                        <Play size={14} fill="currentColor" />
                        Play Sequence
                      </button>
                    </div>

                    <div className="flex flex-wrap gap-4 overflow-x-auto pb-4 scrollbar-hide">
                      {result.cards.map((card, index) => (
                        <EmojiCard
                          key={index}
                          {...card}
                          index={index}
                          isActive={activeCardIndex === index}
                          onAnimationComplete={handleAnimationComplete}
                          showEmoji={true}
                        />
                      ))}
                    </div>
                  </div>

                  {/* Gloss to Emoji Converter */}
                  <div className="pt-8 border-t border-stone-200">
                    <span className="text-[11px] font-bold text-text-muted uppercase tracking-[0.08em] block mb-4">
                      Gloss to Emoji Conversion
                    </span>
                    <GlossToEmojiConverter
                      glossText={result.glosses.join(" ")}
                    />
                  </div>
                </motion.div>
              ) : (
                <motion.div
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <EmptyState />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}
