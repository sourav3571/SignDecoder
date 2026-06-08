"use client";

import React, { useEffect, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface EmbedData {
  word1: string;
  word2: string;
  cosine_similarity: number;
  projected_similarity: number | null;
  vec1: number[];
  vec2: number[];
  proj_vec1: number[];
  proj_vec2: number[];
  dims: number;
}

interface Props {
  inputWord: string;
  matchedWord: string;
}

/** Tiny bar representing a single embedding dimension value in [-1, 1] */
function DimBar({ value, color }: { value: number; color: string }) {
  const pct = Math.abs(value) * 100; // bar length 0-100%
  const isNeg = value < 0;
  return (
    <div className="flex items-center h-[5px] w-full">
      {/* negative side */}
      <div className="flex-1 flex justify-end">
        {isNeg && (
          <div
            style={{ width: `${pct}%`, backgroundColor: color, opacity: 0.55 }}
            className="h-[4px] rounded-l-full"
          />
        )}
      </div>
      {/* centre axis */}
      <div className="w-px h-[7px] bg-stone-300 flex-shrink-0" />
      {/* positive side */}
      <div className="flex-1">
        {!isNeg && (
          <div
            style={{ width: `${pct}%`, backgroundColor: color }}
            className="h-[4px] rounded-r-full"
          />
        )}
      </div>
    </div>
  );
}

/** Stacked bar chart for one embedding vector */
function VectorChart({
  vec,
  color,
  label,
  emoji,
}: {
  vec: number[];
  color: string;
  label: string;
  emoji?: string;
}) {
  return (
    <div className="flex flex-col gap-0.5 flex-1 min-w-0">
      <div className="flex items-center gap-1.5 mb-1">
        {emoji && <span className="text-base leading-none">{emoji}</span>}
        <span
          className="text-[10px] font-bold uppercase tracking-wider truncate"
          style={{ color }}
        >
          {label}
        </span>
      </div>
      <div className="flex flex-col gap-[2px]">
        {vec.map((v, i) => (
          <DimBar key={i} value={v} color={color} />
        ))}
      </div>
    </div>
  );
}

/** Similarity meter arc */
function SimilarityMeter({ value }: { value: number }) {
  const pct = Math.max(0, Math.min(1, (value + 1) / 2)); // map [-1,1] → [0,1]
  const color =
    value >= 0.85
      ? "#22c55e"
      : value >= 0.6
      ? "#f59e0b"
      : value >= 0.35
      ? "#f97316"
      : "#ef4444";

  return (
    <div className="flex flex-col items-center gap-1 px-3">
      {/* Circular gauge */}
      <div className="relative w-14 h-14">
        <svg viewBox="0 0 56 56" className="w-full h-full -rotate-90">
          {/* Track */}
          <circle
            cx="28"
            cy="28"
            r="22"
            fill="none"
            stroke="#e7e5e4"
            strokeWidth="5"
          />
          {/* Fill */}
          <circle
            cx="28"
            cy="28"
            r="22"
            fill="none"
            stroke={color}
            strokeWidth="5"
            strokeLinecap="round"
            strokeDasharray={`${pct * 138.23} 138.23`}
            className="transition-all duration-700"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span
            className="text-[11px] font-black"
            style={{ color }}
          >
            {(value * 100).toFixed(0)}%
          </span>
        </div>
      </div>
      <span className="text-[9px] font-semibold text-stone-400 uppercase tracking-widest text-center leading-tight">
        Cosine
        <br />
        Sim
      </span>
    </div>
  );
}

export default function EmbeddingCompareWidget({ inputWord, matchedWord }: Props) {
  const [data, setData] = useState<EmbedData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);

  const fetch_ = useCallback(async () => {
    if (!inputWord || !matchedWord) return;
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(
        `/api/v1/embeddings/compare?word1=${encodeURIComponent(inputWord)}&word2=${encodeURIComponent(matchedWord)}`
      );
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      setData(await r.json());
    } catch (e: any) {
      setError(e.message ?? "Failed");
    } finally {
      setLoading(false);
    }
  }, [inputWord, matchedWord]);

  useEffect(() => {
    if (expanded && !data && !loading) fetch_();
  }, [expanded, data, loading, fetch_]);

  const sim = data?.projected_similarity ?? data?.cosine_similarity ?? null;
  const vec1 = data?.proj_vec1?.length ? data.proj_vec1 : data?.vec1 ?? [];
  const vec2 = data?.proj_vec2?.length ? data.proj_vec2 : data?.vec2 ?? [];

  return (
    <div className="mt-3 w-full">
      {/* Expand toggle */}
      <button
        onClick={() => setExpanded((p) => !p)}
        className="flex items-center gap-2 text-[10px] font-bold text-stone-400 hover:text-accent uppercase tracking-widest transition-colors group"
      >
        <span
          className={`transition-transform duration-200 ${expanded ? "rotate-90" : ""}`}
        >
          ▶
        </span>
        <span className="group-hover:text-accent transition-colors">
          {expanded ? "Hide" : "Show"} Embedding Vector Comparison
        </span>
        {sim !== null && !expanded && (
          <span
            className="px-1.5 py-0.5 rounded text-[9px] font-bold"
            style={{
              backgroundColor:
                sim >= 0.85
                  ? "#dcfce7"
                  : sim >= 0.35
                  ? "#fef3c7"
                  : "#fee2e2",
              color:
                sim >= 0.85
                  ? "#16a34a"
                  : sim >= 0.35
                  ? "#d97706"
                  : "#dc2626",
            }}
          >
            {(sim * 100).toFixed(0)}% match
          </span>
        )}
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="mt-3 bg-stone-50 border border-stone-200 rounded-xl p-4 shadow-xs">
              {loading && (
                <div className="flex items-center gap-2 text-[12px] text-stone-400 py-4 justify-center">
                  <span className="animate-spin text-base">⚙</span>
                  Loading embeddings…
                </div>
              )}

              {error && (
                <p className="text-[11px] text-red-500 py-2 text-center">
                  ⚠ {error}
                </p>
              )}

              {data && !loading && (
                <div className="flex flex-col gap-3">
                  {/* Header label */}
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold text-stone-400 uppercase tracking-widest">
                      {data.proj_vec1?.length
                        ? "Semantic Projection Space"
                        : "Raw Embedding Space"}{" "}
                      · {data.dims} dims shown
                    </span>
                    {data.projected_similarity !== null && (
                      <span className="text-[9px] bg-violet-50 text-violet-600 border border-violet-200 px-1.5 py-0.5 rounded font-semibold">
                        Projected
                      </span>
                    )}
                  </div>

                  {/* Vector charts + similarity */}
                  <div className="flex gap-3 items-stretch min-w-0">
                    <VectorChart
                      vec={vec1}
                      color="#6366f1"
                      label={inputWord.toUpperCase()}
                      emoji="📥"
                    />

                    <SimilarityMeter value={sim ?? 0} />

                    <VectorChart
                      vec={vec2}
                      color="#10b981"
                      label={matchedWord.toUpperCase()}
                      emoji="🎯"
                    />
                  </div>

                  {/* Legend */}
                  <div className="flex items-center gap-4 pt-1 border-t border-stone-100">
                    <div className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-[#6366f1] inline-block" />
                      <span className="text-[9px] text-stone-500 font-medium">Input word</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-[#10b981] inline-block" />
                      <span className="text-[9px] text-stone-500 font-medium">Predicted match</span>
                    </div>
                    <div className="flex items-center gap-1 ml-auto">
                      <span className="text-[9px] text-stone-400">
                        Each row = 1 embedding dimension · bar width = magnitude
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
