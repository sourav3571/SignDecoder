"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, ArrowRight } from "lucide-react";

export interface SimplificationChange {
  original_word: string;
  simplified_word: string;
  position: number;
  emoji: string;
  definition: string;
  pronunciation: string;
  example: string;
  images: {
    wikimedia: string;
    unsplash: string;
    primary: string;
  };
  links: {
    merriam_webster: string;
    oxford: string;
    google_images: string;
    wikipedia: string;
  };
  complexity_score: {
    original: number;
    simplified: number;
    reduction: number;
  };
}

export interface SimplificationDetails {
  original: string;
  simplified: string;
  changes: SimplificationChange[];
  sentence_complexity?: {
    original: number;
    simplified: number;
    reduction: number;
  };
  sentence_visuals?: {
    theme: string;
    image: string;
    google_images: string;
    wikipedia: string;
  };
}

interface SimplificationDetailsWidgetProps {
  details: SimplificationDetails;
}

export default function SimplificationDetailsWidget({ details }: SimplificationDetailsWidgetProps) {
  const defaultWord = details.changes?.[0]?.original_word || "";
  const [activeWord, setActiveWord] = useState<string>(defaultWord);
  const [prevDetails, setPrevDetails] = useState<SimplificationDetails | null>(null);

  if (details !== prevDetails) {
    setPrevDetails(details);
    setActiveWord(defaultWord);
  }

  if (!details.changes || details.changes.length === 0) {
    return null;
  }

  const activeChange = details.changes.find(c => c.original_word === activeWord);

  const escapeRegExp = (string: string) => string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

  const renderHighlightedText = (text: string, isOriginal: boolean) => {
    const sortedChanges = [...details.changes].sort((a, b) => {
      const lenA = isOriginal ? a.original_word.length : a.simplified_word.length;
      const lenB = isOriginal ? b.original_word.length : b.simplified_word.length;
      return lenB - lenA;
    });

    const searchWords = sortedChanges.map(c => isOriginal ? c.original_word : c.simplified_word);
    if (searchWords.length === 0) return <span>{text}</span>;

    const pattern = new RegExp(`(${searchWords.map(escapeRegExp).join('|')})`, 'gi');
    const parts = text.split(pattern);

    return (
      <>
        {parts.map((part, index) => {
          const matchingChange = sortedChanges.find(c => {
            const target = isOriginal ? c.original_word : c.simplified_word;
            return part.toLowerCase() === target.toLowerCase();
          });

          if (matchingChange) {
            const isActive = matchingChange.original_word === activeWord;
            return (
              <span
                key={index}
                onClick={() => setActiveWord(matchingChange.original_word)}
                className={`cursor-pointer px-1 py-0.5 rounded-sm font-semibold transition-all duration-250 decoration-dotted underline decoration-2 select-none ${isOriginal
                    ? isActive
                      ? 'bg-amber-100 text-amber-900 border-b-2 border-amber-500 shadow-3xs'
                      : 'bg-amber-50/50 hover:bg-amber-100 text-amber-800'
                    : isActive
                      ? 'bg-emerald-100 text-emerald-900 border-b-2 border-emerald-500 shadow-3xs'
                      : 'bg-emerald-50/50 hover:bg-emerald-100 text-emerald-800'
                  }`}
              >
                {part}
              </span>
            );
          }
          return <span key={index}>{part}</span>;
        })}
      </>
    );
  };

  // Helper to estimate a word's difficulty if not in changes
  const getWordDifficulty = (word: string) => {
    const clean = word.toLowerCase().replace(/[^a-z]/g, "");
    if (!clean) return 0.1;
    // Common short stop words
    const stopWords = ["the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "to", "of", "in", "on", "at", "by", "for", "with", "about", "as"];
    if (stopWords.includes(clean)) return 0.05;

    // Heuristic based on length
    if (clean.length <= 4) return 0.15;
    if (clean.length <= 7) return 0.35;
    return 0.6;
  };

  const getSentenceComplexity = () => {
    if (details.sentence_complexity) {
      return details.sentence_complexity;
    }

    // Fallback calculation using replacements and heuristics
    const getSentWords = (s: string) => s.split(/\s+/).map(w => w.replace(/[^a-zA-Z]/g, "")).filter(Boolean);
    const origWords = getSentWords(details.original);
    const simpWords = getSentWords(details.simplified);

    if (origWords.length === 0) return { original: 0.3, simplified: 0.3, reduction: 0 };

    const getDiff = (words: string[], isOriginal: boolean) => {
      let sum = 0;
      words.forEach(w => {
        const change = details.changes.find(c =>
          (isOriginal ? c.original_word : c.simplified_word).toLowerCase() === w.toLowerCase()
        );
        if (change) {
          sum += isOriginal ? change.complexity_score.original : change.complexity_score.simplified;
        } else {
          sum += getWordDifficulty(w);
        }
      });
      return sum / words.length;
    };

    const original = getDiff(origWords, true);
    const simplified = getDiff(simpWords, false);
    return {
      original: Math.round(original * 100) / 100,
      simplified: Math.round(simplified * 100) / 100,
      reduction: Math.round((original - simplified) * 100) / 100
    };
  };

  const sentenceComplexity = getSentenceComplexity();

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 15 }}
      transition={{ duration: 0.4 }}
      className="bg-white border border-stone-200 rounded-2xl shadow-xs overflow-hidden flex flex-col gap-6 p-6"
    >
      {/* Header */}
      <div className="flex items-center gap-2 pb-4 border-b border-stone-100">
        <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center text-accent">
          <Sparkles size={18} className="animate-pulse" />
        </div>
        <div>
          <h3 className="text-[16px] font-bold text-stone-900 leading-tight">Lexical & Figurative Insights</h3>
          <p className="text-[11px] text-stone-400 font-medium uppercase tracking-wider mt-0.5">Visual learning assistant active</p>
        </div>
      </div>

      {/* Sentence Comparison */}
      <div className="flex flex-col gap-4 bg-stone-50/50 border border-stone-150 p-4 rounded-xl">
        <div className="flex flex-col gap-1.5">
          <span className="text-[10px] font-bold text-stone-400 uppercase tracking-widest">Original Input</span>
          <div className="text-[15px] font-medium text-stone-700 leading-relaxed">
            &quot;{renderHighlightedText(details.original, true)}&quot;
          </div>
        </div>
        <div className="h-[1px] bg-stone-200/60" />
        <div className="flex flex-col gap-1.5">
          <span className="text-[10px] font-bold text-emerald-600 uppercase tracking-widest">Simplified Mapping</span>
          <div className="text-[16px] font-bold text-stone-900 leading-relaxed">
            &quot;{renderHighlightedText(details.simplified, false)}&quot;
          </div>
        </div>
      </div>

      {/* Selector Tabs */}
      <div className="flex flex-wrap gap-2 pb-2">
        {details.changes.map((change) => (
          <button
            key={change.original_word}
            onClick={() => setActiveWord(change.original_word)}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all ${change.original_word === activeWord
                ? "bg-stone-900 border-stone-900 text-white shadow-3xs"
                : "bg-white border-stone-200 text-stone-600 hover:bg-stone-50 hover:text-stone-950"
              }`}
          >
            {change.original_word} → {change.simplified_word} {change.emoji}
          </button>
        ))}
      </div>

      {/* Main Details Panel */}
      <AnimatePresence mode="wait">
        {activeChange ? (
          <motion.div
            key={activeChange.original_word}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.25 }}
            className="flex justify-center items-center py-2"
          >
            {/* Word Banner / Top Section Only */}
            <div className="flex items-center gap-3 bg-stone-50 border border-stone-150 p-4 rounded-xl shadow-3xs">
              <div className="px-3.5 py-2 bg-amber-50 border border-amber-200 rounded-xl">
                <span className="text-[14px] font-bold text-amber-800 font-mono">{activeChange.original_word}</span>
              </div>
              <ArrowRight size={16} className="text-stone-400" />
              <div className="px-3.5 py-2 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center gap-2">
                <span className="text-[15px] font-extrabold text-emerald-800 font-mono">{activeChange.simplified_word}</span>
                <span className="text-lg">{activeChange.emoji}</span>
              </div>
            </div>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </motion.div>
  );
}
