"use client";

import React, { useState } from "react";
import { Play } from "lucide-react";
import EmojiCard, { SemanticRole } from "@/components/translator/EmojiCard";
import TranslateInput from "@/components/translator/TranslateInput";
import GlossDisplay from "@/components/translator/GlossDisplay";
import GlossToEmojiConverter from "@/components/translator/GlossToEmojiConverter";
import { LoadingState, EmptyState } from "@/components/translator/States";
import { motion, AnimatePresence } from "framer-motion";
import labelToEmojiData from "@/data/label_to_emoji.json";

interface TranslationResult {
  glosses: string[];
  cards: {
    emoji: string;
    word: string;
    role: SemanticRole;
    confidence: number;
    method: string;
    lottieSrc?: string;
  }[];
  confidence: number;
  processingTimeMs?: number;
  rawMlPrediction?: string;
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

function getEmojiForLabel(label: string): string {
  const cleanLabel = label.replace(/[\[\]]/g, "").trim().toLowerCase();
  
  if (cleanLabel in labelToEmojiData) {
    return (labelToEmojiData as Record<string, string>)[cleanLabel];
  }
  
  for (const [key, val] of Object.entries(labelToEmojiData)) {
    if (key.split("_")[0] === cleanLabel) {
      return val;
    }
  }
  
  return "❓";
}

function cleanLabelWord(label: string): string {
  let cleaned = label.replace(/[\[\]]/g, "").replace(/_/g, " ").trim();
  cleaned = cleaned.replace(/\s+(emotion|activity|device|object|place|food|concept|animal|pathogen|sports|broken|financial|finance|broken)$/i, "");
  return cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
}

function resolveSemanticRole(word: string): SemanticRole {
  const w = word.toUpperCase();
  
  const COMMON_ROLES: Record<string, SemanticRole> = {
    "YESTERDAY": "TIME", "TODAY": "TIME", "TOMORROW": "TIME",
    "MORNING": "TIME", "NIGHT": "TIME", "AFTERNOON": "TIME", "EVENING": "TIME",
    "WEEK": "TIME", "YEAR": "TIME", "MONTH": "TIME", "DAILY": "TIME",
    "I": "SUBJECT", "YOU": "SUBJECT", "HE": "SUBJECT", "SHE": "SUBJECT",
    "WE": "SUBJECT", "THEY": "SUBJECT", "MY": "SUBJECT", "YOUR": "SUBJECT",
    "ME": "SUBJECT", "US": "SUBJECT", "THEM": "SUBJECT",
    "SOURAV": "SUBJECT", "PRIYA": "SUBJECT", "AMIT": "SUBJECT",
    "NOT": "NEGATION", "NEVER": "NEGATION", "NO": "NEGATION",
    "EAT": "VERB", "GO": "VERB", "RUN": "VERB", "PLAY": "VERB", "COOK": "VERB",
    "DRINK": "VERB", "SLEEP": "VERB", "WALK": "VERB", "DRIVE": "VERB",
    "HOME": "LOCATION", "SCHOOL": "LOCATION", "BANK": "LOCATION", "HOSPITAL": "LOCATION"
  };

  if (w in COMMON_ROLES) {
    return COMMON_ROLES[w];
  }
  
  if (w.includes("TIME") || w.includes("DAY") || w.includes("MONTH") || w.includes("YEAR")) return "TIME";
  if (w.includes("GO") || w.includes("EAT") || w.includes("DRINK") || w.includes("PLAY") || w.includes("WALK") || w.includes("RUN")) return "VERB";
  if (w.includes("HOME") || w.includes("OFFICE") || w.includes("SCHOOL") || w.includes("PLACE") || w.includes("BUILDING")) return "LOCATION";
  
  return "OBJECT";
}

export default function TranslatorPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<TranslationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeCardIndex, setActiveCardIndex] = useState(-1);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isConverted, setIsConverted] = useState(false);

  const handleTranslate = async (text: string) => {
    setIsLoading(true);
    setResult(null);
    setError(null);
    setActiveCardIndex(-1);
    setIsPlaying(false);
    setIsConverted(false);

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
      
      const cardsData = data.raw_ml_prediction
        ? data.raw_ml_prediction.split(/\s+/).filter(Boolean).map((token: string) => {
            const cleanWord = token.replace(/[\[\]]/g, "");
            return {
              emoji: getEmojiForLabel(token),
              word: cleanLabelWord(token),
              role: resolveSemanticRole(cleanWord),
              confidence: 0.95,
              method: "ml-model",
              lottieSrc: undefined,
            };
          })
        : (data.emoji_sequence && data.emoji_sequence.length > 0
            ? data.emoji_sequence.map((card: any) => ({
                emoji: card.emoji || "❓",
                word: card.word,
                role: card.semantic_role as SemanticRole,
                confidence: card.confidence,
                method: card.method,
                lottieSrc: undefined,
              }))
            : []);
      
      const mappedResult: TranslationResult = {
        glosses: (data.gloss_string || "").split(" ").map((g: string) => g.replace(/[\[\]]/g, "")).filter(Boolean),
        cards: cardsData,
        confidence: data.confidence_score ?? 0,
        processingTimeMs: data.processing_time_ms ?? 0,
        rawMlPrediction: data.raw_ml_prediction,
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
      
      if (!data.raw_ml_prediction) {
        setIsConverted(true);
        setTimeout(() => startSequence(mappedResult.cards.length), 1000);
      }
    } catch (error) {
      console.error("Translation error:", error);
      setIsLoading(false);
      setError(error instanceof Error ? error.message : "Translation failed. Please try again.");
    }
  };

  const startSequence = (len?: number) => {
    const cardsLength = len !== undefined ? len : (result ? result.cards.length : 0);
    if (cardsLength > 0) {
      setActiveCardIndex(0);
      setIsPlaying(true);
    }
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
        <div className="w-full md:w-[40%] p-6 md:p-12 overflow-y-auto">
          <TranslateInput onTranslate={handleTranslate} isLoading={isLoading} />
        </div>

        <div className="hidden md:block w-[1px] bg-stone-200 self-stretch" />

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
                  <GlossDisplay glosses={result.glosses} />

                  {result.rawMlPrediction && !isConverted && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.98 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="bg-white border border-stone-200 rounded-xl p-6 md:p-8 shadow-xs flex flex-col gap-6"
                    >
                      <div className="flex flex-col gap-2">
                        <span className="text-[11px] font-bold text-text-muted uppercase tracking-[0.08em]">
                          🔮 Raw ML Token Sequence
                        </span>
                        <p className="text-[13px] text-text-secondary">
                          The sequence-to-sequence model generated this raw text label sequence:
                        </p>
                      </div>
                      
                      <div className="flex flex-wrap gap-2.5 p-4 bg-stone-50 border border-stone-100 rounded-lg font-mono text-[14px] text-accent font-semibold justify-center">
                        {result.rawMlPrediction.split(" ").map((token, idx) => (
                          <span 
                            key={idx}
                            className="px-2.5 py-1 bg-white border border-stone-200 rounded shadow-2xs text-stone-800"
                          >
                            {token}
                          </span>
                        ))}
                      </div>

                      <button
                        onClick={() => {
                          setIsConverted(true);
                          setTimeout(() => startSequence(result.cards.length), 300);
                        }}
                        className="w-full flex items-center justify-center gap-2 py-3.5 px-6 bg-accent hover:bg-accent-hover text-white text-[14px] font-medium rounded-lg shadow-xs transition-all hover:shadow active:scale-[0.98]"
                      >
                        ✨ Convert Sequence to Unicode Emoji
                      </button>
                    </motion.div>
                  )}

                  {result.rawMlPrediction && isConverted && (
                    <div className="flex items-center gap-2 bg-stone-50 border border-stone-200 px-3.5 py-2.5 rounded-lg text-[12px] text-text-secondary">
                      <span className="font-bold text-[10px] text-text-muted uppercase tracking-wider">Raw ML Sequence:</span>
                      <code className="font-mono bg-white px-1.5 py-0.5 border border-stone-100 rounded text-stone-700">{result.rawMlPrediction}</code>
                      <button 
                        onClick={() => {
                          setIsConverted(false);
                          setActiveCardIndex(-1);
                          setIsPlaying(false);
                        }}
                        className="ml-auto text-accent hover:underline text-[11px] font-medium"
                      >
                        Reset to text sequence
                      </button>
                    </div>
                  )}

                  {(isConverted || !result.rawMlPrediction) && (
                    <>
                      {result.cards.length > 0 && (
                        <div>
                          <div className="flex items-center justify-between mb-6">
                            <span className="text-[11px] font-bold text-text-muted uppercase tracking-[0.08em]">
                              Visual Representation
                            </span>
                            <button
                              onClick={() => startSequence()}
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
                      )}

                      <div className="pt-8 border-t border-stone-200">
                        <GlossToEmojiConverter
                          glossText={result.glosses.join(" ")}
                        />
                      </div>

                      {result.cards.length > 0 && (
                        <div className="pt-8 border-t border-stone-200">
                          <div className="flex items-center justify-between mb-4">
                            <span className="text-[11px] font-bold text-text-muted uppercase tracking-[0.08em]">
                              Translation Engine Diagnostics
                            </span>
                            <span className="px-2.5 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px] font-semibold rounded-full uppercase tracking-wider">
                              Active
                            </span>
                          </div>
                          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
                            <div className="bg-white border border-stone-200 p-4 rounded-md shadow-xs">
                              <span className="text-[11px] text-text-muted block mb-1">Model Name</span>
                              <span className="text-[14px] font-semibold text-text-primary">FLAN-T5-small</span>
                            </div>
                            <div className="bg-white border border-stone-200 p-4 rounded-md shadow-xs">
                              <span className="text-[11px] text-text-muted block mb-1">Inference Speed</span>
                              <span className="text-[14px] font-semibold text-text-primary">{result.processingTimeMs ?? 0} ms</span>
                            </div>
                            <div className="bg-white border border-stone-200 p-4 rounded-md shadow-xs">
                              <span className="text-[11px] text-text-muted block mb-1">Confidence Score</span>
                              <span className="text-[14px] font-semibold text-text-primary">{((result.confidence ?? 0.9) * 100).toFixed(0)}%</span>
                            </div>
                            <div className="bg-white border border-stone-200 p-4 rounded-md shadow-xs">
                              <span className="text-[11px] text-text-muted block mb-1">Vocabulary Size</span>
                              <span className="text-[14px] font-semibold text-text-primary">34,615 tokens</span>
                            </div>
                          </div>
                          
                          <div className="mt-4 overflow-x-auto bg-white border border-stone-200 rounded-md">
                            <table className="min-w-full divide-y divide-stone-200 text-left text-[12px]">
                              <thead className="bg-stone-50 text-text-muted uppercase tracking-wider text-[10px]">
                                <tr>
                                  <th className="px-4 py-2.5 font-semibold">Gloss Word</th>
                                  <th className="px-4 py-2.5 font-semibold">Emoji</th>
                                  <th className="px-4 py-2.5 font-semibold">Token Confidence</th>
                                  <th className="px-4 py-2.5 font-semibold">Mapping Method</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-stone-100 text-text-secondary">
                                {result.cards.map((card, index) => (
                                  <tr key={index}>
                                    <td className="px-4 py-3 font-bold font-mono text-text-primary">{card.word}</td>
                                    <td className="px-4 py-3 text-base">{card.emoji}</td>
                                    <td className="px-4 py-3">
                                      <span className={
                                        `px-1.5 py-0.5 rounded-sm text-[10px] font-semibold ${(card.confidence ?? 0.7) >= 0.9 
                                          ? "bg-emerald-50 text-emerald-700 border border-emerald-100"
                                          : "bg-amber-50 text-amber-700 border border-amber-100"
                                        }`
                                      }>
                                        {((card.confidence ?? 0.7) * 100).toFixed(0)}%
                                      </span>
                                    </td>
                                    <td className="px-4 py-3 font-mono text-[11px]">
                                      {card.method === "ml-model" ? "Seq2Seq Model Generation" : "Word Dictionary Fallback"}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )}
                    </>
                  )}
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
