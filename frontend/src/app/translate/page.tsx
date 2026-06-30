"use client";

import React, { useState } from "react";
import { Play, ChevronDown, ChevronUp, X, Sparkles, HelpCircle } from "lucide-react";
import EmojiCard, { SemanticRole } from "@/components/translator/EmojiCard";
import TranslateInput from "@/components/translator/TranslateInput";
import { LoadingState, EmptyState } from "@/components/translator/States";
import EmbeddingCompareWidget from "@/components/translator/EmbeddingCompareWidget";
import SimplificationDetailsWidget from "@/components/translator/SimplificationDetailsWidget";
import { motion, AnimatePresence } from "framer-motion";
import labelToEmojiData from "@/data/label_to_emoji.json";
import { getConceptVisuals } from "@/lib/visualDictionary";

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
  const [showDiagnostics, setShowDiagnostics] = useState(false);

  // Visual Dictionary States
  const [selectedGlossWord, setSelectedGlossWord] = useState<string | null>(null);
  const [glossDetails, setGlossDetails] = useState<any | null>(null);
  const [isLoadingGlossDetails, setIsLoadingGlossDetails] = useState<boolean>(false);



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

  const handleCardClick = async (word: string) => {
    const cleanWord = word.replace(/[\[\]]/g, "").trim();
    if (!cleanWord) return;
    
    setSelectedGlossWord(cleanWord);
    setIsLoadingGlossDetails(true);
    setGlossDetails(null);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 
        (typeof window !== "undefined" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.5.1" || window.location.hostname === "127.0.0.1")
          ? "http://localhost:8000"
          : "");
      const response = await fetch(`${backendUrl}/api/v1/translate/dictionary/${encodeURIComponent(cleanWord.toLowerCase())}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch dictionary details`);
      }
      
      const data = await response.json();
      
      const visualData = await getConceptVisuals(cleanWord);
      
      setGlossDetails({
        ...data,
        image_url: visualData.imageUrl || data.image_url,
        explanation: visualData.extract || data.explanation
      });
    } catch (err) {
      console.error("Error fetching dictionary details:", err);
      
      const visualData = await getConceptVisuals(cleanWord);
      
      // Premium experience client-side fallback
      setGlossDetails({
        word: cleanWord.toUpperCase(),
        definition: `A primary visual sign concept representing '${cleanWord.toLowerCase()}'.`,
        sign_handshape: "Closed-5 or flat hand shape",
        sign_location: "Neutral workspace in front of the chest",
        sign_movement: "Varies depending on grammar context",
        explanation: visualData.extract || `To sign '${cleanWord.toLowerCase()}', position your hand in the central signing space. Gently move it outwards or tap representing the core meaning.`,
        mnemonic_tip: `Associate the physical gesture with the definition of '${cleanWord.toLowerCase()}'.`,
        image_url: visualData.imageUrl || `https://images.unsplash.com/featured/800x600/?${encodeURIComponent(cleanWord.toLowerCase())}`,
        video_url: `https://www.youtube.com/results?search_query=how+to+sign+${encodeURIComponent(cleanWord.toLowerCase())}+in+sign+language`,
        emoji: "❓"
      });
    } finally {
      setIsLoadingGlossDetails(false);
    }
  };

  return (
    <div className="pt-16 min-h-screen bg-stone-50">
      <div className="max-w-[1280px] mx-auto h-[calc(100vh-64px)] flex flex-col md:flex-row">
        <div className="w-full md:w-[38%] p-6 md:p-10 overflow-y-auto border-r border-stone-200 bg-white">
          <TranslateInput onTranslate={handleTranslate} isLoading={isLoading} />
        </div>

        <div className="w-full md:w-[62%] flex flex-col lg:flex-row overflow-hidden bg-stone-50/40 border-l border-stone-200">
          {/* Main Results Scrollable Area */}
          <div className="flex-1 p-6 md:p-10 overflow-y-auto h-full flex flex-col gap-10">
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

                  {/* Lexical Simplification Details Widget */}
                  {result.simplification_details && (
                    <SimplificationDetailsWidget details={result.simplification_details} />
                  )}

                  {result.rawMlPrediction && (
                    <motion.div
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="bg-white border border-stone-200 rounded-xl p-6 shadow-xs flex flex-col gap-4"
                    >
                      <div className="flex flex-col gap-1">
                        <span className="text-[11px] font-bold text-text-muted uppercase tracking-[0.08em]">
                          🔮 Gloss Model (emoji_ml)
                        </span>
                        <p className="text-[13px] text-text-secondary">
                          Input sentence mapped to output ISL gloss label sequence. Click tokens for dictionary lookup.
                        </p>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-stone-100 pt-4">
                        <div className="flex flex-col gap-1.5">
                          <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider">
                            Model Input (Simplified Sentence)
                          </span>
                          <div className="p-3 bg-stone-50 border border-stone-100 rounded-lg text-[13px] font-medium text-stone-800">
                            {result.reconstructed}
                          </div>
                        </div>

                        <div className="flex flex-col gap-1.5">
                          <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider">
                            Model Output (Gloss Sequence)
                          </span>
                          <div className="flex flex-wrap gap-1.5 p-2 bg-stone-50 border border-stone-100 rounded-lg font-mono text-[13px] text-accent font-semibold items-center min-h-[46px]">
                            {result.rawMlPrediction.split(" ").map((token, idx) => {
                              const cleanToken = token.replace(/[\[\]]/g, "").trim();
                              const isSelected = selectedGlossWord?.toUpperCase() === cleanToken.toUpperCase();
                              return (
                                <span
                                  key={idx}
                                  onClick={() => handleCardClick(cleanToken)}
                                  className={`px-2.5 py-1 rounded-md text-[13px] font-semibold border transition-all duration-200 cursor-pointer shadow-3xs hover:scale-[1.03] active:scale-[0.98] ${
                                    isSelected
                                      ? "bg-accent text-white border-accent shadow-md shadow-accent/20"
                                      : "bg-white border-stone-200 text-stone-800 hover:border-accent/40 hover:text-accent"
                                  }`}
                                >
                                  {token}
                                </span>
                              );
                            })}
                          </div>
                        </div>
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
                          Mapped Sign Gloss Sequence (Click cards for dictionary lookup)
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
                            onClick={() => handleCardClick(card.word)}
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

          {/* Deep-dive Visual Dictionary Side Panel */}
          <AnimatePresence>
            {selectedGlossWord && (
              <motion.div
                initial={{ opacity: 0, x: 50, width: 0 }}
                animate={{ opacity: 1, x: 0, width: "100%", maxWidth: "420px" }}
                exit={{ opacity: 0, x: 50, width: 0 }}
                transition={{ type: "spring", damping: 25, stiffness: 200 }}
                className="w-full lg:w-[420px] bg-white border-l border-stone-200 h-full flex flex-col overflow-hidden shadow-2xl relative z-10"
              >
                {/* Header */}
                <div className="p-5 border-b border-stone-150 flex items-center justify-between bg-stone-50/50">
                  <div className="flex flex-col gap-0.5">
                    <div className="flex items-center gap-1.5">
                      <span className="text-[11px] font-bold text-accent uppercase tracking-wider flex items-center gap-1">
                        <Sparkles size={10} className="fill-current" /> AI Visual Dictionary
                      </span>
                      <span className="px-1.5 py-0.5 bg-accent/10 border border-accent/25 text-accent text-[8px] font-bold rounded-sm uppercase tracking-[0.05em]">
                        Premium
                      </span>
                    </div>
                    <h3 className="text-xl font-extrabold text-stone-900 tracking-tight flex items-center gap-2">
                      {selectedGlossWord.toUpperCase()}
                      {glossDetails?.emoji && <span className="text-xl">{glossDetails.emoji}</span>}
                    </h3>
                  </div>
                  <button
                    onClick={() => { setSelectedGlossWord(null); setGlossDetails(null); }}
                    className="p-1.5 rounded-full hover:bg-stone-250 text-stone-400 hover:text-stone-700 transition-colors cursor-pointer"
                  >
                    <X size={18} />
                  </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-5 flex flex-col gap-6">
                  {isLoadingGlossDetails ? (
                    <div className="flex-1 flex flex-col gap-6 py-6 animate-pulse">
                      {/* Image Placeholder */}
                      <div className="w-full h-48 bg-stone-100 rounded-lg shadow-inner flex items-center justify-center">
                        <span className="text-stone-300 text-xs font-semibold uppercase tracking-wider flex items-center gap-2">
                          <Sparkles className="animate-spin" size={12} /> Fetching visuals...
                        </span>
                      </div>
                      
                      {/* Details Placeholder */}
                      <div className="flex flex-col gap-3">
                        <div className="h-4 bg-stone-100 rounded w-1/3"></div>
                        <div className="h-3 bg-stone-100 rounded w-full"></div>
                        <div className="h-3 bg-stone-100 rounded w-5/6"></div>
                        <div className="h-3 bg-stone-100 rounded w-4/5"></div>
                      </div>
                    </div>
                  ) : glossDetails ? (
                    <div className="flex flex-col gap-6">
                      {/* Photographic Image */}
                      {glossDetails.image_url && (
                        <div className="group relative w-full h-48 bg-stone-50 overflow-hidden rounded-lg shadow-sm border border-stone-200/50">
                          <img
                            src={glossDetails.image_url}
                            alt={glossDetails.word}
                            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                          />
                          <div className="absolute top-2 left-2 bg-black/60 backdrop-blur-xs text-white text-[10px] font-bold px-2 py-0.5 rounded-sm shadow-xs flex items-center gap-1 uppercase tracking-wider">
                            📸 Photographic Concept
                          </div>
                        </div>
                      )}

                      {/* Explanation */}
                      <div className="flex flex-col gap-2">
                        <span className="text-[10px] font-bold text-stone-400 uppercase tracking-wider flex items-center gap-1">
                          ✨ Concept & Signing Guide
                        </span>
                        <p className="text-sm text-stone-750 font-medium leading-relaxed bg-stone-50/50 border border-stone-100 p-4 rounded-md shadow-3xs">
                          {glossDetails.explanation}
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div className="flex-1 flex flex-col items-center justify-center text-center p-6 text-stone-400">
                      <HelpCircle size={36} className="text-stone-300 mb-2" />
                      <p className="text-sm font-medium">Select a gloss card to view detailed dictionary insights.</p>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
