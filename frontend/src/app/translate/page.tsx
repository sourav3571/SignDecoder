"use client";

import React, { useState } from "react";
import { Play } from "lucide-react";
import EmojiCard, { SemanticRole } from "@/components/translator/EmojiCard";
import TranslateInput from "@/components/translator/TranslateInput";
import GlossDisplay from "@/components/translator/GlossDisplay";
import { LoadingState, EmptyState } from "@/components/translator/States";
import EmbeddingCompareWidget from "@/components/translator/EmbeddingCompareWidget";
import SimplificationDetailsWidget from "@/components/translator/SimplificationDetailsWidget";
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
    nearest_neighbors?: {
      word: string;
      similarity: number;
      emoji: string;
    }[];
  }[];
  oovCards?: {
    emoji: string;
    word: string;
    role: SemanticRole;
    confidence: number;
    method: string;
    lottieSrc?: string;
    nearest_neighbors?: {
      word: string;
      similarity: number;
      emoji: string;
    }[];
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
  semanticCluster?: string;
  clusterConfidence?: number;
  vectorSlice?: number[];
  neighbors?: {
    word: string;
    similarity: number;
    emojis: string[];
  }[];
  simplification_details?: any;
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
  const [inputText, setInputText] = useState("");

  // Reverse Translation States
  const [mode, setMode] = useState<"forward" | "reverse">("forward");
  const [emojiInput, setEmojiInput] = useState("");
  const [reverseResult, setReverseResult] = useState<{
    emoji_sequence: string;
    glosses: string[];
    reconstructed_text: string;
    confidence_score: number;
  } | null>(null);

  const handleTranslate = async (text: string, simplify: boolean = false) => {
    setIsLoading(true);
    setInputText(text);
    setResult(null);
    setError(null);
    setActiveCardIndex(-1);
    setIsPlaying(false);
    setIsConverted(false);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 
        (typeof window !== "undefined" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.5.1" || window.location.hostname === "127.0.0.1")
          ? "http://localhost:8000"
          : "");
      const response = await fetch(`${backendUrl}/api/v1/translate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text,
          sign_language: "ISL",
          include_details: true,
          simplify,
        }),
      });

      const responseBody = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(responseBody?.detail ?? `Translation failed (${response.status})`);
      }

      const data = responseBody;

      const cardsData = data.emoji_sequence && data.emoji_sequence.length > 0
        ? data.emoji_sequence.map((card: any) => ({
          emoji: card.emoji || "❓",
          word: card.word,
          role: card.semantic_role as SemanticRole,
          confidence: card.confidence,
          method: card.method,
          lottieSrc: undefined,
          nearest_neighbors: card.nearest_neighbors,
        }))
        : (data.raw_ml_prediction
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
          : []);

      const oovCardsData = data.oov_sequence && data.oov_sequence.length > 0
        ? data.oov_sequence.map((card: any) => ({
          emoji: card.emoji || "❓",
          word: card.word,
          role: card.semantic_role as SemanticRole,
          confidence: card.confidence,
          method: card.method,
          lottieSrc: undefined,
          nearest_neighbors: card.nearest_neighbors,
        }))
        : [];

      const mappedResult: TranslationResult = {
        glosses: (data.gloss_string || "").split(" ").map((g: string) => g.replace(/[\[\]]/g, "")).filter(Boolean),
        cards: cardsData,
        oovCards: oovCardsData,
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
        semanticCluster: data.semantic_cluster,
        clusterConfidence: data.cluster_confidence,
        vectorSlice: data.vector_slice,
        neighbors: data.neighbors,
        simplification_details: data.simplification_details,
      };

      setResult(mappedResult);
      setIsLoading(false);
      setIsConverted(true);
      setTimeout(() => startSequence(mappedResult.cards.length), 1000);
    } catch (error) {
      console.error("Translation error:", error);
      setIsLoading(false);
      setError(error instanceof Error ? error.message : "Translation failed. Please try again.");
    }
  };

  const handleReverseTranslate = async () => {
    if (!emojiInput.trim()) return;
    setIsLoading(true);
    setReverseResult(null);
    setError(null);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 
        (typeof window !== "undefined" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.5.1" || window.location.hostname === "127.0.0.1")
          ? "http://localhost:8000"
          : "");
      const response = await fetch(`${backendUrl}/api/v1/translate/reverse`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          emoji_sequence: emojiInput,
        }),
      });

      const responseBody = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(responseBody?.detail ?? `Reverse translation failed (${response.status})`);
      }

      setReverseResult(responseBody);
    } catch (error) {
      console.error("Reverse translation error:", error);
      setError(error instanceof Error ? error.message : "Failed to decode sign sequence.");
    } finally {
      setIsLoading(false);
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
          {/* Mode Switcher */}
          <div className="flex bg-stone-100 p-1.5 rounded-lg mb-8 border border-stone-200">
            <button
              onClick={() => { setMode("forward"); setResult(null); setReverseResult(null); setError(null); }}
              className={`flex-1 py-2 text-xs font-semibold rounded-md transition-all ${mode === "forward" ? "bg-white shadow-xs text-stone-900" : "text-stone-500 hover:text-stone-800"}`}
            >
              ✍️ Text to Sign
            </button>
            <button
              onClick={() => { setMode("reverse"); setResult(null); setReverseResult(null); setError(null); }}
              className={`flex-1 py-2 text-xs font-semibold rounded-md transition-all ${mode === "reverse" ? "bg-white shadow-xs text-stone-900" : "text-stone-500 hover:text-stone-800"}`}
            >
              🔄 Sign to Text
            </button>
          </div>

          {mode === "forward" ? (
            <TranslateInput onTranslate={handleTranslate} isLoading={isLoading} />
          ) : (
            <div className="flex flex-col gap-6">
              <div className="flex flex-col gap-2">
                <h2 className="text-xl font-bold text-stone-900">Sign to Text Decoder</h2>
                <p className="text-sm text-stone-550">
                  Select signs or enter emojis to decode them back into grammatically correct English.
                </p>
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-xs font-bold text-stone-700 uppercase tracking-wider">
                  Emoji Sequence Input
                </label>
                <textarea
                  value={emojiInput}
                  onChange={(e) => setEmojiInput(e.target.value)}
                  placeholder="Paste or click emojis below..."
                  className="w-full min-h-[100px] p-4 bg-white border border-stone-200 rounded-lg shadow-2xs font-mono text-xl focus:outline-hidden focus:border-accent resize-none text-stone-800"
                />
              </div>

              {/* Emoji Palette / Keyboard */}
              <div className="flex flex-col gap-2.5">
                <span className="text-xs font-bold text-stone-500 uppercase tracking-wider">
                  Quick Emoji Keyboard
                </span>
                <div className="grid grid-cols-5 gap-2">
                  {[
                    { char: "👤", label: "I" },
                    { char: "👉", label: "Him" },
                    { char: "🏠", label: "Home" },
                    { char: "🏫", label: "School" },
                    { char: "🏢", label: "Office" },
                    { char: "🍕", label: "Pizza" },
                    { char: "🍔", label: "Burger" },
                    { char: "🏃", label: "Go/Run" },
                    { char: "🚗", label: "Car" },
                    { char: "☀️", label: "Today" },
                    { char: "🌧️", label: "Rain" },
                    { char: "❤️", label: "Love" },
                    { char: "❌", label: "No" },
                    { char: "🤔", label: "Question" },
                    { char: "🙏", label: "Please" },
                  ].map((em) => (
                    <button
                      key={em.char}
                      onClick={() => setEmojiInput((prev) => (prev ? `${prev} ${em.char}` : em.char))}
                      className="flex flex-col items-center justify-center p-2.5 bg-white border border-stone-200 rounded-lg hover:bg-stone-50 transition-colors shadow-3xs active:scale-[0.95]"
                    >
                      <span className="text-lg">{em.char}</span>
                      <span className="text-[9px] text-stone-400 mt-1 uppercase font-semibold">{em.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setEmojiInput("")}
                  className="px-4 py-3 bg-stone-100 hover:bg-stone-200 text-stone-700 text-sm font-semibold rounded-lg transition-colors"
                >
                  Clear
                </button>
                <button
                  onClick={handleReverseTranslate}
                  disabled={isLoading || !emojiInput.trim()}
                  className="flex-1 py-3 bg-accent hover:bg-accent-hover text-white text-sm font-semibold rounded-lg shadow-xs transition-colors disabled:opacity-50"
                >
                  Decode to English
                </button>
              </div>
            </div>
          )}
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
                  <LoadingState status={mode === "forward" ? "Mapping words to visual signs..." : "Decoding sign grammar..."} />
                </motion.div>
              ) : mode === "reverse" ? (
                reverseResult ? (
                  <motion.div
                    key="reverse-result"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex flex-col gap-8"
                  >
                    <div className="bg-white border border-stone-200 rounded-xl p-8 shadow-xs flex flex-col gap-6">
                      <div className="flex flex-col gap-2">
                        <span className="text-[11px] font-bold text-text-muted uppercase tracking-[0.08em]">
                          📝 Reconstructed English Sentence
                        </span>
                        <h1 className="text-2xl md:text-3xl font-extrabold text-stone-900 tracking-tight leading-tight">
                          {reverseResult.reconstructed_text}
                        </h1>
                      </div>
                    </div>

                    <div className="flex flex-col gap-4">
                      <span className="text-[11px] font-bold text-text-muted uppercase tracking-[0.08em]">
                        🔍 Decoded Gloss Breakdown
                      </span>
                      <div className="bg-white border border-stone-200 rounded-xl p-6 shadow-xs flex flex-col gap-4">
                        <div className="flex flex-wrap gap-4 justify-center">
                          {reverseResult.emoji_sequence.split(" ").map((emoji, index) => {
                            const gloss = reverseResult.glosses[index] || "UNKNOWN";
                            return (
                              <div
                                key={index}
                                className="flex flex-col items-center bg-stone-50 border border-stone-150 p-3 rounded-lg min-w-[70px] shadow-3xs"
                              >
                                <span className="text-2xl">{emoji}</span>
                                <span className="text-[10px] font-bold font-mono text-stone-600 mt-2">
                                  {gloss}
                                </span>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    </div>

                    <div className="pt-8 border-t border-stone-200">
                      <div className="flex items-center justify-between mb-4">
                        <span className="text-[11px] font-bold text-text-muted uppercase tracking-[0.08em]">
                          Reverse Translation Diagnostics
                        </span>
                        <span className="px-2.5 py-0.5 bg-accent-hover/10 text-accent text-[10px] font-semibold rounded-full uppercase tracking-wider">
                          Ready
                        </span>
                      </div>
                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                        <div className="bg-white border border-stone-200 p-4 rounded-md shadow-xs">
                          <span className="text-[11px] text-text-muted block mb-1">Engine Method</span>
                          <span className="text-[14px] font-semibold text-text-primary">Linguistic Grammar Decoder</span>
                        </div>
                        <div className="bg-white border border-stone-200 p-4 rounded-md shadow-xs">
                          <span className="text-[11px] text-text-muted block mb-1">Confidence Score</span>
                          <span className="text-[14px] font-semibold text-text-primary">
                            {(reverseResult.confidence_score * 100).toFixed(0)}%
                          </span>
                        </div>
                        <div className="bg-white border border-stone-200 p-4 rounded-md shadow-xs">
                          <span className="text-[11px] text-text-muted block mb-1">Vocabulary Class</span>
                          <span className="text-[14px] font-semibold text-text-primary">SVO Structured</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ) : (
                  <motion.div
                    key="reverse-empty"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex flex-col items-center justify-center py-20 text-center"
                  >
                    <div className="w-16 h-16 bg-stone-100 rounded-full flex items-center justify-center mb-4 text-stone-400 border border-stone-200">
                      🔄
                    </div>
                    <h3 className="text-md font-semibold text-stone-800 mb-1">No sign sequence decoded</h3>
                    <p className="text-sm text-stone-550 max-w-xs">
                      Enter sign emojis in the left panel and click decode to reconstruct English.
                    </p>
                  </motion.div>
                )
              ) : result ? (
                <motion.div
                  key="result"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex flex-col gap-12"
                >
                  <GlossDisplay glosses={result.glosses} />

                  {/* Lexical Simplification Details Widget */}
                  {result.simplification_details && (
                    <SimplificationDetailsWidget details={result.simplification_details} />
                  )}

                  {/* Clustering Summary - Always Visible */}
                  <motion.div
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white border border-stone-200 rounded-lg p-4 shadow-xs"
                  >
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-[11px] text-text-muted block mb-1.5 font-semibold uppercase tracking-wider">Semantic Cluster</span>
                        <span className="text-[16px] font-bold text-accent uppercase tracking-wider">{result.semanticCluster ?? "NEUTRAL"}</span>
                      </div>
                      <div>
                        <span className="text-[11px] text-text-muted block mb-1.5 font-semibold uppercase tracking-wider">Cluster Confidence</span>
                        <span className="text-[16px] font-bold text-text-primary font-mono">
                          {result.clusterConfidence !== undefined ? `${(result.clusterConfidence * 100).toFixed(0)}%` : "N/A"}
                        </span>
                      </div>
                    </div>
                  </motion.div>

                  {result.rawMlPrediction && (
                    <motion.div
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="bg-white border border-stone-200 rounded-xl p-6 shadow-xs flex flex-col gap-4"
                    >
                      <div className="flex flex-col gap-1">
                        <span className="text-[11px] font-bold text-text-muted uppercase tracking-[0.08em]">
                          🔮 Model Raw Output
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
                    </motion.div>
                  )}

                  {result.cards.length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex flex-col gap-6"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-[11px] font-bold text-text-muted uppercase tracking-[0.08em]">
                          Mapped Sign Gloss Sequence (Visual Representation)
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

                      <div className="flex flex-row flex-nowrap gap-4 overflow-x-auto pb-4 scrollbar-hide">
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
                    </motion.div>
                  )}

                  {/* Semantic Proximity Mappings (Nearest Neighbors) */}
                  {((result.cards.some(c => c.method === "semantic-proximity" && c.nearest_neighbors)) ||
                    (result.oovCards && result.oovCards.some(c => c.method === "semantic-proximity" && c.nearest_neighbors))) && (
                    <motion.div
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="bg-white border border-stone-200 rounded-xl p-6 shadow-xs flex flex-col gap-4"
                    >
                      <div className="flex flex-col gap-1">
                        <span className="text-[11px] font-bold text-accent uppercase tracking-[0.08em]">
                          🧠 Embedded Proximity Mapping (OOV Resolution)
                        </span>
                        <p className="text-[13px] text-text-secondary">
                          The following out-of-vocabulary words were dynamically mapped to the nearest known concept in the embedding space:
                        </p>
                      </div>
                      <div className="flex flex-col gap-4 mt-2">
                        {[
                          ...result.cards.filter(c => c.method === "semantic-proximity" && c.nearest_neighbors),
                          ...(result.oovCards ? result.oovCards.filter(c => c.method === "semantic-proximity" && c.nearest_neighbors) : [])
                        ].map((card, idx) => (
                          <div key={idx} className="bg-stone-50 border border-stone-150 rounded-lg p-4 flex flex-col gap-3">
                            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                              <div className="flex items-center gap-2 flex-wrap">
                                <span className="font-bold text-stone-800 px-2 py-1 bg-stone-200/50 rounded font-mono text-[13px]">
                                  {card.word.toUpperCase()}
                                </span>
                                <span className="text-stone-450 text-xs font-medium">mapped to</span>
                                <span className="px-2.5 py-1 bg-accent/10 border border-accent/20 rounded-md text-accent text-[13px] font-bold flex items-center gap-1.5 shadow-2xs">
                                  <span>{card.nearest_neighbors?.[0]?.word}</span>
                                  <span className="text-base">{card.emoji}</span>
                                </span>
                              </div>
                              <div className="flex flex-col gap-1.5">
                                <span className="text-[10px] font-bold text-stone-400 uppercase tracking-wider">Similar K-Nearest Clustering:</span>
                                <div className="flex flex-wrap gap-1.5">
                                  {card.nearest_neighbors?.map((neighbor, nIdx) => (
                                    <span key={nIdx} className="px-2.5 py-0.5 bg-white border border-stone-200 rounded-md text-[11px] text-stone-700 font-mono shadow-3xs flex items-center gap-1">
                                      <span className="font-semibold">{neighbor.word}</span>
                                      <span className="text-[10px] text-stone-400 font-bold">{(neighbor.similarity * 100).toFixed(0)}%</span>
                                      <span>{neighbor.emoji}</span>
                                    </span>
                                  ))}
                                </div>
                              </div>
                            </div>
                            {/* Embedding vector comparison widget */}
                            <EmbeddingCompareWidget
                              inputWord={card.word}
                              matchedWord={card.nearest_neighbors?.[0]?.word ?? ""}
                            />
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  )}

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
                          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4 mb-4">
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
                            <div className="bg-white border border-stone-200 p-4 rounded-md shadow-xs">
                              <span className="text-[11px] text-text-muted block mb-1">Semantic Cluster</span>
                              <span className="text-[14px] font-semibold text-accent uppercase tracking-wider">
                                {result.semanticCluster ?? "NEUTRAL"}
                              </span>
                            </div>
                            <div className="bg-white border border-stone-200 p-4 rounded-md shadow-xs">
                              <span className="text-[11px] text-text-muted block mb-1">Cluster Conf.</span>
                              <span className="text-[14px] font-semibold text-text-primary font-mono">
                                {result.clusterConfidence !== undefined ? `${(result.clusterConfidence * 100).toFixed(0)}%` : "N/A"}
                              </span>
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
                                      {card.method === "ml-model"
                                        ? "Seq2Seq Model Generation"
                                        : card.method === "dictionary-heuristic"
                                        ? "Dictionary Heuristic"
                                        : card.method === "semantic-proximity"
                                        ? "Embedded Proximity Match"
                                        : card.method}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
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
