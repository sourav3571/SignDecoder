"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, ArrowRight, BookOpen, Volume2, Image as ImageIcon, ExternalLink, Globe } from "lucide-react";

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
}

interface SimplificationDetailsWidgetProps {
  details: SimplificationDetails;
}

export default function SimplificationDetailsWidget({ details }: SimplificationDetailsWidgetProps) {
  const [activeWord, setActiveWord] = useState<string>("");
  const [prevDetails, setPrevDetails] = useState<SimplificationDetails | null>(null);

  if (details !== prevDetails) {
    setPrevDetails(details);
    if (details.changes && details.changes.length > 0) {
      setActiveWord(details.changes[0].original_word);
    } else {
      setActiveWord("");
    }
  }

  if (!details.changes || details.changes.length === 0) {
    return null;
  }

  const activeChange = details.changes.find(c => c.original_word === activeWord) || details.changes[0];

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
                className={`cursor-pointer px-1 py-0.5 rounded-sm font-semibold transition-all duration-250 decoration-dotted underline decoration-2 select-none ${
                  isOriginal
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

      {/* Selector Tabs (if multiple changes exist) */}
      {details.changes.length > 1 && (
        <div className="flex flex-wrap gap-2 pb-2">
          {details.changes.map((change) => (
            <button
              key={change.original_word}
              onClick={() => setActiveWord(change.original_word)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all ${
                change.original_word === activeWord
                  ? "bg-stone-900 border-stone-900 text-white shadow-3xs"
                  : "bg-white border-stone-200 text-stone-600 hover:bg-stone-50 hover:text-stone-950"
              }`}
            >
              {change.original_word} → {change.simplified_word}
            </button>
          ))}
        </div>
      )}

      {/* Main Details Panel */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeChange.original_word}
          initial={{ opacity: 0, x: 10 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -10 }}
          transition={{ duration: 0.25 }}
          className="grid grid-cols-1 md:grid-cols-12 gap-6"
        >
          {/* Left Side: Explanations and Complexity */}
          <div className="md:col-span-7 flex flex-col gap-5">
            {/* Word Banner */}
            <div className="flex items-center gap-3">
              <div className="px-3.5 py-2 bg-amber-50 border border-amber-200 rounded-xl">
                <span className="text-[14px] font-bold text-amber-800 font-mono">{activeChange.original_word}</span>
              </div>
              <ArrowRight size={16} className="text-stone-400" />
              <div className="px-3.5 py-2 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center gap-2">
                <span className="text-[15px] font-extrabold text-emerald-800 font-mono">{activeChange.simplified_word}</span>
                <span className="text-lg">{activeChange.emoji}</span>
              </div>
            </div>

            {/* Complexity Indicator */}
            <div className="bg-stone-50 border border-stone-150 rounded-xl p-4 flex flex-col gap-3">
              <span className="text-[10px] font-bold text-stone-400 uppercase tracking-wider block">Complexity Score Reduction</span>
              
              <div className="flex flex-col gap-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-stone-600 font-medium">Original difficulty:</span>
                  <span className="font-bold text-amber-700">{Math.round(activeChange.complexity_score.original * 100)}%</span>
                </div>
                <div className="w-full h-2 bg-stone-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-amber-500 rounded-full transition-all duration-500"
                    style={{ width: `${activeChange.complexity_score.original * 100}%` }}
                  />
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-stone-600 font-medium">Simplified difficulty:</span>
                  <span className="font-bold text-emerald-700">{Math.round(activeChange.complexity_score.simplified * 100)}%</span>
                </div>
                <div className="w-full h-2 bg-stone-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                    style={{ width: `${activeChange.complexity_score.simplified * 100}%` }}
                  />
                </div>
              </div>

              {activeChange.complexity_score.reduction > 0 && (
                <div className="mt-1 text-[11px] font-bold text-emerald-600 flex items-center gap-1">
                  <span>✓ Complexity reduced by {Math.round(activeChange.complexity_score.reduction * 100)}%! Better mapping context.</span>
                </div>
              )}
            </div>

            {/* Dictionary Definitions */}
            <div className="flex flex-col gap-3">
              <div className="flex items-center gap-1.5 text-stone-800">
                <BookOpen size={16} className="text-stone-400" />
                <span className="text-xs font-bold uppercase tracking-wider">Dictionary Lookup</span>
              </div>
              <div className="flex flex-col gap-2">
                {activeChange.pronunciation && (
                  <div className="flex items-center gap-2 text-stone-550 text-xs font-mono">
                    <Volume2 size={13} className="text-stone-400" />
                    <span>Pronunciation:</span>
                    <span className="font-semibold text-stone-700">{activeChange.pronunciation}</span>
                  </div>
                )}
                <div className="text-[14px] text-stone-800 leading-relaxed font-medium bg-stone-50/50 p-3 rounded-lg border border-stone-100">
                  <span className="font-bold text-stone-500 text-xs block mb-1">Meaning:</span>
                  {activeChange.definition}
                </div>
                {activeChange.example && (
                  <div className="text-[13px] text-stone-600 italic bg-stone-50/50 p-3 rounded-lg border border-stone-100">
                    <span className="font-bold text-stone-500 text-xs block mb-1 not-italic">Usage Example:</span>
                    &quot;{activeChange.example}&quot;
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Side: Unsplash Image & Quick Resources */}
          <div className="md:col-span-5 flex flex-col gap-4">
            {/* Visual Representation Container */}
            <div className="flex flex-col gap-1.5">
              <div className="flex items-center gap-1.5 text-stone-800">
                <ImageIcon size={16} className="text-stone-400" />
                <span className="text-xs font-bold uppercase tracking-wider">Visual Association</span>
              </div>
              <div className="relative aspect-video w-full overflow-hidden rounded-xl border border-stone-200 bg-stone-150 shadow-3xs group">
                <img
                  src={activeChange.images.primary}
                  alt={activeChange.simplified_word}
                  className="object-cover w-full h-full transition-transform duration-500 group-hover:scale-105"
                  onError={(e) => {
                    // Fallback to plain color block if image fails to load
                    (e.target as HTMLElement).style.display = 'none';
                  }}
                />
                <div className="absolute bottom-2 right-2 px-2 py-1 bg-stone-900/80 backdrop-blur-xs rounded-md text-[9px] font-bold text-white tracking-wider uppercase">
                  Associated concept
                </div>
              </div>
            </div>

            {/* Quick External Dictionaries Links */}
            <div className="flex flex-col gap-2">
              <span className="text-[10px] font-bold text-stone-400 uppercase tracking-wider">Verify Meanings</span>
              <div className="grid grid-cols-2 gap-2">
                <a
                  href={activeChange.links.merriam_webster}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 px-3 py-2 bg-stone-50 hover:bg-stone-100 border border-stone-200 rounded-lg text-xs font-semibold text-stone-700 hover:text-stone-950 transition-colors shadow-3xs"
                >
                  <BookOpen size={13} className="text-stone-400" />
                  <span>Merriam-Webster</span>
                  <ExternalLink size={10} className="ml-auto text-stone-400" />
                </a>
                <a
                  href={activeChange.links.oxford}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 px-3 py-2 bg-stone-50 hover:bg-stone-100 border border-stone-200 rounded-lg text-xs font-semibold text-stone-700 hover:text-stone-950 transition-colors shadow-3xs"
                >
                  <BookOpen size={13} className="text-stone-400" />
                  <span>Oxford Learn</span>
                  <ExternalLink size={10} className="ml-auto text-stone-400" />
                </a>
                <a
                  href={activeChange.links.wikipedia}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 px-3 py-2 bg-stone-50 hover:bg-stone-100 border border-stone-200 rounded-lg text-xs font-semibold text-stone-700 hover:text-stone-950 transition-colors shadow-3xs"
                >
                  <Globe size={13} className="text-stone-400" />
                  <span>Wikipedia</span>
                  <ExternalLink size={10} className="ml-auto text-stone-400" />
                </a>
                <a
                  href={activeChange.links.google_images}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 px-3 py-2 bg-stone-50 hover:bg-stone-100 border border-stone-200 rounded-lg text-xs font-semibold text-stone-700 hover:text-stone-950 transition-colors shadow-3xs"
                >
                  <ImageIcon size={13} className="text-stone-400" />
                  <span>Google Images</span>
                  <ExternalLink size={10} className="ml-auto text-stone-400" />
                </a>
              </div>
            </div>
          </div>
        </motion.div>
      </AnimatePresence>
    </motion.div>
  );
}
