"use client";

import React, { useState, useEffect } from "react";
import TranslateInput from "@/components/translator/TranslateInput";
import GlossDisplay from "@/components/translator/GlossDisplay";
import EmojiCard, { SemanticRole } from "@/components/translator/EmojiCard";
import ConfidenceIndicator from "@/components/translator/ConfidenceIndicator";
import NLPAnalysisTable from "@/components/translator/NLPAnalysisTable";
import { LoadingState, EmptyState } from "@/components/translator/States";
import { Volume2, Play } from "lucide-react";
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

const MOCK_RESULT: TranslationResult = {
  glosses: ["yesterday", "home", "sourav", "breakfast", "eat"],
  cards: [
    { emoji: "⬅️", word: "Yesterday", role: "TIME" },
    { emoji: "🏠", word: "Home", role: "LOCATION" },
    { emoji: "👤", word: "Sourav", role: "SUBJECT" },
    { emoji: "🥣", word: "Breakfast", role: "OBJECT" },
    { emoji: "🍽️", word: "Eat", role: "VERB" },
  ],
  confidence: 0.94,
  analysis: {
    subject: "Sourav",
    verb: "Eat",
    object: "Breakfast",
    time: "Yesterday",
    location: "Home",
    negation: false
  },
  reconstructed: "Yesterday at home, Sourav ate breakfast."
};

export default function TranslatorPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<TranslationResult | null>(null);
  const [activeCardIndex, setActiveCardIndex] = useState(-1);
  const [isPlaying, setIsPlaying] = useState(false);

  const handleTranslate = async (text: string) => {
    setIsLoading(true);
    setResult(null);
    setActiveCardIndex(-1);
    
    try {
      const response = await fetch("http://localhost:8000/api/v1/translate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text,
          sign_language: "ASL", // Or from a state if you add a selector
          include_details: true,
        }),
      });

      if (!response.ok) {
        throw new Error("Translation failed");
      }

      const data = await response.json();
      
      // Map API response to our UI state
      const mappedResult: TranslationResult = {
        glosses: data.gloss_string.split(" ").map((g: string) => g.replace(/[\[\]]/g, "")),
        cards: data.emoji_sequence.map((card: any) => ({
          emoji: card.emoji,
          word: card.word,
          role: (card.semantic_role || "OBJECT") as SemanticRole,
          lottieSrc: card.lottie_file,
        })),
        confidence: data.confidence_score,
        analysis: {
          subject: data.analysis?.semantic_roles?.SUBJECT?.[0],
          verb: data.analysis?.semantic_roles?.VERB?.[0],
          object: data.analysis?.semantic_roles?.OBJECT?.[0],
          time: data.analysis?.semantic_roles?.TIME?.[0],
          location: data.analysis?.semantic_roles?.LOCATION?.[0],
          negation: data.analysis?.semantic_roles?.NEGATION?.length > 0,
        },
        reconstructed: data.preprocessed_text, // Or a properly reconstructed sentence
      };

      setResult(mappedResult);
      setIsLoading(false);
      
      // Start sequence automatically after a short delay
      setTimeout(() => startSequence(), 1000);
    } catch (error) {
      console.error("Translation error:", error);
      setIsLoading(false);
      // You could add an error state here if desired
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
    <div className="pt-24 min-h-screen bg-white">
      <div className="max-w-[1200px] mx-auto h-[calc(100vh-96px)] flex flex-col md:flex-row">
        {/* Left Panel (Input) */}
        <div className="w-full md:w-[40%] p-6 md:p-12 overflow-y-auto">
          <TranslateInput onTranslate={handleTranslate} isLoading={isLoading} />
        </div>

        {/* Divider */}
        <div className="hidden md:block w-[1px] bg-border self-stretch" />

        {/* Right Panel (Output) */}
        <div className="w-full md:w-[60%] p-6 md:p-12 overflow-y-auto bg-background/30">
          <div className="flex flex-col gap-10">
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

                  {/* Emoji Cards */}
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
                        />
                      ))}
                    </div>
                  </div>

                  {/* Confidence */}
                  <ConfidenceIndicator score={result.confidence} />

                  {/* NLP Analysis */}
                  <NLPAnalysisTable analysis={result.analysis} />

                  {/* Readable Output */}
                  <div className="pt-8 border-t border-border">
                    <span className="text-[11px] font-bold text-text-muted uppercase tracking-[0.08em] block mb-4">
                      Readable Output
                    </span>
                    <div className="flex items-center justify-between gap-4 bg-white border border-border p-5 rounded-md shadow-xs">
                      <p className="text-[16px] text-text-primary leading-relaxed italic">
                        "{result.reconstructed}"
                      </p>
                      <button className="p-3 text-text-secondary hover:text-accent transition-colors bg-surface-elevated rounded-full">
                        <Volume2 size={20} />
                      </button>
                    </div>
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
