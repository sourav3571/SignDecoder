"use client";

import React, { useState } from "react";
import { Search, Filter, X } from "lucide-react";
import DictionaryCard from "@/components/dictionary/DictionaryCard";
import { cn } from "@/lib/utils";

const CATEGORIES = [
  "All Words",
  "Actions / Verbs",
  "People",
  "Places",
  "Food & Drink",
  "Emotions",
  "Time",
  "Objects",
  "Nature"
];

const DICTIONARY_DATA = [
  { word: "Eat", emoji: "🍽️", category: "Actions / Verbs", example: "I like to eat apples." },
  { word: "Home", emoji: "🏠", category: "Places", example: "I am going home." },
  { word: "Yesterday", emoji: "⬅️", category: "Time", example: "It rained yesterday." },
  { word: "Breakfast", emoji: "🥣", category: "Food & Drink", example: "I had eggs for breakfast." },
  { word: "Sourav", emoji: "👤", category: "People", example: "Sourav is my friend." },
  { word: "Happy", emoji: "😊", category: "Emotions", example: "She looks very happy." },
  { word: "School", emoji: "🏫", category: "Places", example: "The school is closed today." },
  { word: "Drink", emoji: "🧃", category: "Actions / Verbs", example: "Would you like a drink?" },
  { word: "Today", emoji: "📅", category: "Time", example: "Today is a sunny day." },
  { word: "Friend", emoji: "🤝", category: "People", example: "He is my best friend." },
  { word: "Sad", emoji: "😢", category: "Emotions", example: "Why are you feeling sad?" },
  { word: "Water", emoji: "💧", category: "Nature", example: "Please give me some water." },
];

export default function DictionaryPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState("All Words");

  const filteredData = DICTIONARY_DATA.filter((item) => {
    const matchesSearch = item.word.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = activeCategory === "All Words" || item.category === activeCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="pt-32 pb-24 min-h-screen bg-background">
      <div className="max-w-[1200px] mx-auto px-6">
        {/* Header */}
        <div className="flex flex-col items-center text-center mb-16">
          <span className="text-[11px] font-bold text-text-muted uppercase tracking-[0.08em] mb-4">
            DICTIONARY
          </span>
          <h1 className="font-serif text-[42px] mb-8">
            Explore the Visual Language
          </h1>
          
          <div className="relative w-full max-w-[560px] group">
            <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-text-muted group-focus-within:text-accent transition-colors" size={20} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search for a word or category..."
              className="w-full h-14 pl-14 pr-12 bg-white border border-border rounded-md shadow-sm outline-none focus:border-accent focus:ring-1 focus:ring-accent/10 transition-all text-[16px]"
            />
            {searchQuery && (
              <button 
                onClick={() => setSearchQuery("")}
                className="absolute right-5 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary transition-colors"
              >
                <X size={18} />
              </button>
            )}
          </div>
        </div>

        <div className="flex flex-col lg:flex-row gap-12">
          {/* Filter Sidebar */}
          <aside className="w-full lg:w-64 shrink-0">
            <div className="sticky top-32">
              <div className="flex items-center gap-2 mb-6">
                <Filter size={16} className="text-text-muted" />
                <span className="text-[13px] font-bold text-text-muted uppercase tracking-wider">
                  Categories
                </span>
              </div>
              
              <nav className="flex lg:flex-col flex-wrap gap-1">
                {CATEGORIES.map((category) => (
                  <button
                    key={category}
                    onClick={() => setActiveCategory(category)}
                    className={cn(
                      "text-left px-4 py-2.5 rounded-sm text-[15px] transition-all",
                      activeCategory === category
                        ? "bg-accent text-white font-medium"
                        : "text-text-secondary hover:bg-surface-elevated hover:text-text-primary"
                    )}
                  >
                    {category}
                  </button>
                ))}
              </nav>
            </div>
          </aside>

          {/* Grid */}
          <main className="flex-grow">
            <div className="flex items-center justify-between mb-8">
              <span className="text-[13px] text-text-muted">
                Showing {filteredData.length} results
              </span>
            </div>
            
            {filteredData.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
                {filteredData.map((item, index) => (
                  <DictionaryCard key={index} {...item} />
                ))}
              </div>
            ) : (
              <div className="py-20 text-center bg-white border border-dashed border-border rounded-lg">
                <p className="text-text-secondary mb-2">No results found for "{searchQuery}"</p>
                <button 
                  onClick={() => {setSearchQuery(""); setActiveCategory("All Words");}}
                  className="text-accent text-[14px] font-medium hover:underline"
                >
                  Clear all filters
                </button>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}
