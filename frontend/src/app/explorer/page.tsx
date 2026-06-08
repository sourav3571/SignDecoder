"use client";

import React, { useState, useEffect } from "react";
import { Search, Compass, Cpu, Info, HelpCircle, Activity, Sparkles, RefreshCw, BarChart2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface Neighbor {
  word: string;
  similarity: number;
  emojis: string[];
}

interface ExplorerData {
  query: string;
  vector_slice: number[];
  neighbors: Neighbor[];
}

const PRESET_CONCEPTS = [
  { term: "sad", label: "😢 Sadness", category: "Emotions" },
  { term: "disappointed", label: "🥺 Disappointment", category: "Emotions" },
  { term: "happy", label: "😊 Happiness", category: "Emotions" },
  { term: "breakfast", label: "🍳 Breakfast", category: "Actions/Objects" },
  { term: "school", label: "🏫 School", category: "Locations" },
  { term: "weather", label: "🌧️ Weather", category: "Contexts" },
  { term: "doctor", label: "🩺 Doctor", category: "Objects" },
  { term: "yesterday", label: "📅 Yesterday", category: "Time" },
];

export default function VectorExplorerPage() {
  const [query, setQuery] = useState("disappointed");
  const [inputVal, setInputVal] = useState("disappointed");
  const [data, setData] = useState<ExplorerData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Custom Similarity Calculator States
  const [wordA, setWordA] = useState("sad");
  const [wordB, setWordB] = useState("unhappy");
  const [calculatedSimilarity, setCalculatedSimilarity] = useState<number | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);

  const fetchExplorerData = async (word: string) => {
    if (!word.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/embeddings/explore", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: word.trim() }),
      });
      const resData = await response.json();
      if (!response.ok) {
        throw new Error(resData.detail || "Failed to fetch vector space data.");
      }
      setData(resData);
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "Error querying semantic vector space");
    } finally {
      setIsLoading(false);
    }
  };

  const calculatePairSimilarity = async () => {
    if (!wordA.trim() || !wordB.trim()) return;
    setIsCalculating(true);
    try {
      // Query embedding explorer data for both and compute cosine similarity of their vector slices
      const resA = await fetch("/api/embeddings/explore", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: wordA.trim() }),
      });
      const resB = await fetch("/api/embeddings/explore", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: wordB.trim() }),
      });
      
      if (resA.ok && resB.ok) {
        const dataA = await resA.json();
        const dataB = await resB.json();
        
        // Calculate similarity using vector_slice (normalized in backend projection net)
        const vecA = dataA.vector_slice;
        const vecB = dataB.vector_slice;
        
        let dotProduct = 0;
        let normA = 0;
        let normB = 0;
        for (let i = 0; i < Math.min(vecA.length, vecB.length); i++) {
          dotProduct += vecA[i] * vecB[i];
          normA += vecA[i] * vecA[i];
          normB += vecB[i] * vecB[i];
        }
        
        const similarity = dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
        setCalculatedSimilarity(Math.max(-1, Math.min(1, similarity)));
      } else {
        throw new Error("One or both words could not be found in vocabulary index.");
      }
    } catch (err) {
      console.error(err);
      alert(err instanceof Error ? err.message : "Error calculating similarity");
    } finally {
      setIsCalculating(false);
    }
  };

  useEffect(() => {
    fetchExplorerData(query);
  }, [query]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputVal.trim()) {
      setQuery(inputVal.trim());
    }
  };

  // Map value to color representing positive/negative dimension weight
  const getDimensionColor = (val: number) => {
    const absVal = Math.min(Math.abs(val) * 3, 1); // scale representation
    if (val >= 0) {
      return `rgba(59, 130, 246, ${absVal})`; // Tailwind blue
    } else {
      return `rgba(245, 158, 11, ${absVal})`; // Tailwind amber
    }
  };

  return (
    <div className="pt-28 pb-24 min-h-screen bg-stone-50/40 text-stone-850">
      <div className="max-w-[1200px] mx-auto px-6">
        
        {/* Header */}
        <header className="mb-12 border-b border-stone-200 pb-8">
          <div className="flex items-center gap-2 mb-3">
            <span className="px-2.5 py-0.5 bg-accent/10 text-accent text-[11px] font-bold rounded-full uppercase tracking-wider">
              Neural Semantic Space
            </span>
            <span className="px-2.5 py-0.5 bg-stone-200 text-stone-700 text-[11px] font-medium rounded-full">
              InfoNCE Loss Aligned
            </span>
          </div>
          <h1 className="text-4xl font-extrabold text-stone-900 tracking-tight mb-4">
            Vector Space Explorer
          </h1>
          <p className="text-stone-600 max-w-2xl leading-relaxed text-sm md:text-[15px]">
            Meaning in SignSpeak is defined geometrically by proximity in a shared vector space, 
            rather than rigid, rule-based mappings. Query any English word or phrase to visualize 
            its projected embedding and inspect its nearest semantic neighbors.
          </p>
        </header>

        {/* Content Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Left Panel: Query & Presets */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            <div className="bg-white border border-stone-200 rounded-xl p-6 shadow-xs">
              <h2 className="text-sm font-bold text-stone-850 uppercase tracking-wider mb-4 flex items-center gap-2">
                <Search size={16} className="text-accent" />
                Query Vector Space
              </h2>
              
              <form onSubmit={handleSearchSubmit} className="flex gap-2 mb-4">
                <input
                  type="text"
                  value={inputVal}
                  onChange={(e) => setInputVal(e.target.value)}
                  placeholder="Enter word or phrase..."
                  className="flex-1 px-4 py-2.5 bg-stone-50 border border-stone-250 rounded-lg text-sm focus:outline-hidden focus:border-accent text-stone-800"
                />
                <button
                  type="submit"
                  disabled={isLoading}
                  className="px-4 bg-accent hover:bg-accent-hover text-white text-sm font-semibold rounded-lg shadow-3xs hover:shadow-2xs transition-all flex items-center justify-center"
                >
                  {isLoading ? <RefreshCw size={15} className="animate-spin" /> : "Query"}
                </button>
              </form>

              {error && (
                <div className="text-xs text-red-600 bg-red-50 border border-red-100 p-3 rounded-lg mb-4">
                  {error}
                </div>
              )}

              {/* Anchors / Presets */}
              <div className="border-t border-stone-150 pt-4">
                <span className="text-[11px] font-bold text-stone-500 uppercase tracking-wider block mb-3">
                  Preset Concept Anchors
                </span>
                <div className="flex flex-wrap gap-2">
                  {PRESET_CONCEPTS.map((concept) => (
                    <button
                      key={concept.term}
                      onClick={() => {
                        setQuery(concept.term);
                        setInputVal(concept.term);
                      }}
                      className={`px-3 py-1.5 text-xs rounded-md border transition-all ${
                        query.toLowerCase() === concept.term.toLowerCase()
                          ? "bg-accent/10 border-accent text-accent font-semibold"
                          : "bg-white hover:bg-stone-50 border-stone-200 text-stone-700"
                      }`}
                    >
                      {concept.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Diagnostic Theory card */}
            <div className="bg-stone-900 text-stone-100 rounded-xl p-6 shadow-xs">
              <h3 className="text-xs font-bold text-accent uppercase tracking-wider mb-3 flex items-center gap-2">
                <Cpu size={15} />
                Embedding Mechanics
              </h3>
              <ul className="text-xs text-stone-300 space-y-3 leading-relaxed">
                <li>
                  <strong className="text-stone-100">1. SentenceTransformer Encoder:</strong> Generates a dense 384-dimensional semantic embedding via <code className="bg-stone-800 px-1 py-0.5 rounded text-amber-300">all-MiniLM-L6-v2</code>.
                </li>
                <li>
                  <strong className="text-stone-100">2. Linear Projection:</strong> Projects the standard representation into a customized, sign-aligned semantic subspace where cosine proximity denotes equivalence.
                </li>
                <li>
                  <strong className="text-stone-100">3. Dynamic k-NN Retrieval:</strong> Retrieves the closest lexical neighbors dynamically from the pre-trained dictionary, bypasses static rules entirely.
                </li>
              </ul>
            </div>
          </div>

          {/* Right Panel: Visualization Visualizer */}
          <div className="lg:col-span-8 flex flex-col gap-6">
            
            {/* Visual Barcode Fingerprint */}
            <div className="bg-white border border-stone-200 rounded-xl p-6 md:p-8 shadow-xs">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
                <div>
                  <span className="text-[11px] font-bold text-stone-400 uppercase tracking-wider block mb-1">
                    Embedding Visual Fingerprint
                  </span>
                  <h2 className="text-lg font-bold text-stone-900">
                    Projected Vector Slice (First 48 Dimensions)
                  </h2>
                </div>
                <div className="flex gap-4 text-xs font-semibold">
                  <span className="flex items-center gap-1.5 text-blue-600">
                    <span className="w-3 h-3 rounded-xs bg-blue-500 block" /> Positive
                  </span>
                  <span className="flex items-center gap-1.5 text-amber-600">
                    <span className="w-3 h-3 rounded-xs bg-amber-500 block" /> Negative
                  </span>
                </div>
              </div>

              {data ? (
                <div className="flex flex-col gap-6">
                  {/* Grid Representation */}
                  <div className="grid grid-cols-8 sm:grid-cols-12 gap-1.5 bg-stone-50 p-4 border border-stone-150 rounded-lg">
                    {data.vector_slice.map((val, idx) => (
                      <div
                        key={idx}
                        style={{ backgroundColor: getDimensionColor(val) }}
                        className="aspect-square rounded-sm border border-stone-200 hover:scale-[1.15] hover:border-stone-800 transition-all cursor-crosshair flex items-center justify-center group relative"
                      >
                        <span className="text-[9px] font-bold opacity-0 group-hover:opacity-100 text-stone-900 pointer-events-none select-none">
                          {idx}
                        </span>
                        
                        {/* Tooltip */}
                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 bg-stone-950 text-white text-[10px] py-1 px-2.5 rounded-sm whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none shadow-md transition-opacity z-10 flex flex-col gap-0.5">
                          <span className="font-bold text-accent">Dimension {idx}</span>
                          <span className="font-mono">{val.toFixed(6)}</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Summary Metric Strip */}
                  <div className="grid grid-cols-3 gap-4 border-t border-stone-150 pt-4 text-center">
                    <div>
                      <span className="text-[10px] text-stone-400 font-semibold uppercase tracking-wider block mb-1">Mean Magnitude</span>
                      <span className="text-sm font-bold text-stone-850">
                        {(data.vector_slice.reduce((acc, curr) => acc + Math.abs(curr), 0) / data.vector_slice.length).toFixed(4)}
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] text-stone-400 font-semibold uppercase tracking-wider block mb-1">Peak Dimension</span>
                      <span className="text-sm font-bold text-stone-850">
                        {data.vector_slice.reduce((maxIdx, curr, idx, arr) => Math.abs(curr) > Math.abs(arr[maxIdx]) ? idx : maxIdx, 0)}
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] text-stone-400 font-semibold uppercase tracking-wider block mb-1">L2 Norm (Slice)</span>
                      <span className="text-sm font-bold text-stone-850">
                        {Math.sqrt(data.vector_slice.reduce((acc, curr) => acc + curr * curr, 0)).toFixed(4)}
                      </span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="h-32 flex items-center justify-center text-stone-400 italic text-sm">
                  Loading vector fingerprint...
                </div>
              )}
            </div>

            {/* Nearest Neighbors Map */}
            <div className="bg-white border border-stone-200 rounded-xl p-6 md:p-8 shadow-xs">
              <span className="text-[11px] font-bold text-stone-400 uppercase tracking-wider block mb-1">
                Cosine Similarity Index
              </span>
              <h2 className="text-lg font-bold text-stone-900 mb-6 flex items-center gap-2">
                <Compass size={18} className="text-accent" />
                Nearest Vocabulary Neighbors in Projected Space
              </h2>

              {data ? (
                <div className="flex flex-col gap-4">
                  <div className="divide-y divide-stone-100 border border-stone-200 rounded-lg overflow-hidden">
                    {data.neighbors.map((neighbor, idx) => (
                      <div
                        key={idx}
                        className={`flex items-center justify-between p-4 transition-colors ${
                          idx === 0 ? "bg-accent/5" : "bg-white hover:bg-stone-50"
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <span className="w-5 h-5 bg-stone-100 text-stone-600 rounded-full flex items-center justify-center text-[10px] font-bold font-mono">
                            {idx + 1}
                          </span>
                          <div>
                            <span className="font-bold text-stone-850 text-sm md:text-base capitalize">
                              {neighbor.word}
                            </span>
                            <span className="ml-3 text-lg">
                              {neighbor.emojis.join(" ")}
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center gap-4 w-40 justify-end">
                          <div className="w-24 bg-stone-150 h-2 rounded-full overflow-hidden hidden sm:block">
                            <div
                              style={{ width: `${(neighbor.similarity * 100).toFixed(0)}%` }}
                              className="bg-accent h-full rounded-full"
                            />
                          </div>
                          <span className="text-xs font-mono font-bold text-accent min-w-[45px] text-right">
                            {(neighbor.similarity * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="h-32 flex items-center justify-center text-stone-400 italic text-sm">
                  Loading similarity neighbors...
                </div>
              )}
            </div>

            {/* Word Similarity Pair Calculator */}
            <div className="bg-white border border-stone-200 rounded-xl p-6 md:p-8 shadow-xs">
              <span className="text-[11px] font-bold text-stone-400 uppercase tracking-wider block mb-1">
                Cosine Similarity Comparator
              </span>
              <h2 className="text-lg font-bold text-stone-900 mb-6 flex items-center gap-2">
                <Activity size={18} className="text-accent" />
                Semantic Cosine Angle Calculator
              </h2>

              <div className="flex flex-col sm:flex-row gap-4 items-center mb-6">
                <div className="flex-1 w-full flex flex-col gap-1">
                  <label className="text-[10px] font-bold text-stone-500 uppercase">Word A</label>
                  <input
                    type="text"
                    value={wordA}
                    onChange={(e) => setWordA(e.target.value)}
                    className="w-full px-3 py-2 bg-stone-50 border border-stone-250 rounded-lg text-sm text-stone-800"
                  />
                </div>
                <div className="text-stone-400 text-sm font-bold pt-4">vs</div>
                <div className="flex-1 w-full flex flex-col gap-1">
                  <label className="text-[10px] font-bold text-stone-500 uppercase">Word B</label>
                  <input
                    type="text"
                    value={wordB}
                    onChange={(e) => setWordB(e.target.value)}
                    className="w-full px-3 py-2 bg-stone-50 border border-stone-250 rounded-lg text-sm text-stone-800"
                  />
                </div>
                <button
                  onClick={calculatePairSimilarity}
                  disabled={isCalculating}
                  className="sm:self-end px-5 py-2 bg-stone-900 hover:bg-stone-850 text-white text-sm font-semibold rounded-lg shadow-3xs"
                >
                  {isCalculating ? "Computing..." : "Compare"}
                </button>
              </div>

              {calculatedSimilarity !== null && (
                <div className="bg-stone-50 border border-stone-200 p-4 rounded-lg flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">⚡</span>
                    <div>
                      <span className="text-[10px] text-stone-400 block font-semibold uppercase">Proximity Score</span>
                      <span className="text-sm font-bold text-stone-800">
                        Cosine distance between "{wordA}" and "{wordB}" in the projected space
                      </span>
                    </div>
                  </div>
                  <span className="text-xl font-extrabold font-mono text-accent">
                    {(calculatedSimilarity * 100).toFixed(2)}%
                  </span>
                </div>
              )}
            </div>

          </div>

        </div>

      </div>
    </div>
  );
}
