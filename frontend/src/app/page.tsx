import React from "react";
import Link from "next/link";
import { ArrowRight, Brain, Zap, Sparkles, Database, FileText, Globe } from "lucide-react";
import EmojiCard from "@/components/translator/EmojiCard";
import { cn } from "@/lib/utils";

export default function LandingPage() {
  return (
    <div className="flex flex-col">
      {}
      <section className="relative min-h-[90vh] flex flex-col items-center justify-center pt-32 pb-20 px-6 bg-background overflow-hidden">
        <div className="max-w-[1200px] mx-auto flex flex-col items-center text-center">
          {}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-white border border-border rounded-full shadow-xs mb-10 transition-transform hover:scale-105">
            <span className="text-[13px] font-medium text-text-secondary flex items-center gap-2">
              🏆 <span className="hidden sm:inline">B.Tech NLP based project</span>
              <span className="sm:hidden">FYP 2026</span>
            </span>
          </div>

          {}
          <h1 className="font-serif text-[48px] md:text-[64px] leading-[1.1] text-text-primary max-w-[700px] mb-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            Understanding Sign Language, Made Simple.
          </h1>

          {}
          <p className="text-[17px] md:text-[18px] text-text-secondary leading-[1.7] max-w-[520px] mb-12 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-100">
            SignDecoder converts English text into sign language emoji sequences using advanced NLP — making communication accessible for everyone.
          </p>

          {}
          <div className="flex flex-col sm:flex-row items-center gap-4 mb-10 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-200">
            <Link
              href="/translate"
              className="w-full sm:w-auto px-8 py-3.5 bg-accent text-white rounded-sm font-medium text-[15px] hover:bg-accent-hover transition-all flex items-center justify-center gap-2"
            >
              Start Translating
              <ArrowRight size={16} />
            </Link>
            <Link
              href="#how-it-works"
              className="w-full sm:w-auto px-8 py-3.5 bg-transparent border border-border-strong text-text-secondary rounded-sm font-medium text-[15px] hover:bg-surface-elevated transition-all text-center"
            >
              See How It Works
            </Link>
          </div>

          <p className="text-[13px] text-text-muted mb-24 animate-in fade-in duration-1000 delay-300">
            Free to use &middot; No account required
          </p>

          {}
          <div className="relative w-full max-w-[720px] animate-in fade-in zoom-in-95 duration-1000 delay-500">
            <div className="flex items-center justify-center flex-wrap gap-4 p-8 bg-white/50 border border-border rounded-lg shadow-lg backdrop-blur-sm">
              <EmojiCard index={0} emoji="⬅️" word="Yesterday" role="TIME" />
              <EmojiCard index={1} emoji="🏠" word="Home" role="LOCATION" />
              <EmojiCard index={2} emoji="👤" word="Sourav" role="SUBJECT" />
              <EmojiCard index={3} emoji="🥣" word="Breakfast" role="OBJECT" />
              <EmojiCard index={4} emoji="🍽️" word="Eat" role="VERB" />
            </div>
            <p className="mt-6 text-[13px] text-text-muted italic">
              Example: "Sourav was eating breakfast at home yesterday"
            </p>
          </div>
        </div>
      </section>

      {}
      <section className="py-12 border-t border-b border-border bg-background">
        <div className="max-w-[1200px] mx-auto px-6">
          <div className="flex flex-wrap items-center justify-center gap-x-12 gap-y-8 opacity-50 grayscale transition-all hover:grayscale-0 hover:opacity-100">
            <span className="text-[12px] font-bold text-text-muted uppercase tracking-widest w-full text-center mb-4 md:w-auto md:mb-0">
              Built with
            </span>
            <span className="text-[14px] font-bold text-text-primary font-mono tracking-tighter">spaCy</span>
            <span className="text-[14px] font-bold text-text-primary tracking-tight">HuggingFace</span>
            <span className="text-[14px] font-bold text-text-primary uppercase">PHOENIX Dataset</span>
            <span className="text-[14px] font-bold text-text-primary flex items-center gap-1">
              <span className="text-blue-600">IEEE</span> Research Aligned
            </span>
          </div>
        </div>
      </section>

      {}
      <section className="py-24 bg-surface-elevated">
        <div className="max-w-[1200px] mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureCard 
              icon={<Brain className="text-accent" size={24} />}
              title="Deep NLP Understanding"
              description="Uses spaCy and custom neural models to extract precise semantic meaning from complex English sentences."
            />
            <FeatureCard 
              icon={<Zap className="text-accent" size={24} />}
              title="Sign Language Grammar"
              description="Automatically reorders words following ASL/ISL grammar rules, moving time to the front and verbs to the end."
            />
            <FeatureCard 
              icon={<Sparkles className="text-accent" size={24} />}
              title="Visual Emoji Output"
              description="Translates gloss sequences into clear, animated emoji cards that represent concepts visually for easy understanding."
            />
          </div>
        </div>
      </section>

      {}
      <section id="how-it-works" className="py-32 bg-white">
        <div className="max-w-[720px] mx-auto px-6">
          <div className="text-center mb-20">
            <span className="text-[11px] font-bold text-text-muted uppercase tracking-[0.08em]">
              HOW IT WORKS
            </span>
            <h2 className="font-serif text-[36px] mt-4">
              Six steps from text to understanding
            </h2>
          </div>

          <div className="flex flex-col">
            <Step number={1} title="You type a sentence" description="Enter any English sentence. Our system handles normalization and cleaning automatically." />
            <Step number={2} title="We clean and normalize" description="Punctuation is removed, and words are reduced to their base forms (lemmas) for easier mapping." />
            <Step number={3} title="NLP extracts meaning" description="We identify subjects, verbs, objects, time indicators, and locations using dependency parsing." />
            <Step number={4} title="Grammar reorders" description="Sentences are restructured from English SVO (Subject-Verb-Object) to Sign Language grammar." />
            <Step number={5} title="Words mapped to emoji" description="Each sign concept is mapped to its most accurate visual representation from our dictionary." />
            <Step number={6} title="Animations play sequentially" description="Watch as the sequence unfolds, playing each sign animation in the correct linguistic order." />
          </div>
        </div>
      </section>

      {}
      <section className="py-24 bg-white border-t border-border">
        <div className="max-w-[1000px] mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
            <div className="grid grid-cols-2 gap-8">
              <Stat value="0.68" label="BLEU Score" />
              <Stat value="87%" label="Emoji Accuracy" />
              <Stat value="1000+" label="Words Covered" />
              <Stat value="ASL/ISL" label="Languages" />
            </div>
            <div className="relative">
              <div className="absolute -top-4 -left-4 text-accent/10">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M14.017 21L14.017 18C14.017 16.8954 14.9124 16 16.017 16H19.017C19.5693 16 20.017 15.5523 20.017 15V9C20.017 8.44772 19.5693 8 19.017 8H16.017C14.9124 8 14.017 7.10457 14.017 6V3L14.017 2H11.017V21H14.017ZM5.017 21L5.017 18C5.017 16.8954 5.91243 16 7.017 16H10.017C10.5693 16 11.017 15.5523 11.017 15V9C11.017 8.44772 10.5693 8 10.017 8H7.017C5.91243 8 5.017 7.10457 5.017 6V3L5.017 2H2.017V21H5.017Z" />
                </svg>
              </div>
              <blockquote className="text-[20px] font-serif leading-relaxed text-text-primary relative z-10">
                "SignDecoder demonstrates that rule-based and neural hybrid approaches can significantly improve accessibility by bridging the gap between spoken language and visual communication."
              </blockquote>
              <cite className="block mt-6 text-[14px] font-medium text-text-secondary not-italic">
                &mdash; Research Abstract, 2026 
              </cite>
            </div>
          </div>
        </div>
      </section>

      {}
      <section className="py-24 bg-accent text-white text-center px-6">
        <h2 className="font-serif text-[42px] mb-8">Ready to start communicating?</h2>
        <Link
          href="/translate"
          className="inline-flex items-center gap-2 px-10 py-4 bg-white text-accent rounded-sm font-medium text-[16px] hover:bg-surface-elevated transition-all shadow-lg"
        >
          Open Translator
          <ArrowRight size={18} />
        </Link>
      </section>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="bg-white p-8 rounded-md border border-border shadow-sm hover:shadow-md transition-all duration-300">
      <div className="mb-6">{icon}</div>
      <h3 className="text-[17px] font-semibold mb-4">{title}</h3>
      <p className="text-[15px] text-text-secondary leading-relaxed">{description}</p>
    </div>
  );
}

function Step({ number, title, description }: { number: number, title: string, description: string }) {
  return (
    <div className="flex gap-8 group">
      <div className="flex flex-col items-center">
        <div className="w-10 h-10 rounded-full border border-border flex items-center justify-center font-mono text-[14px] text-text-muted group-hover:border-accent group-hover:text-accent transition-colors">
          {number}
        </div>
        {number < 6 && <div className="w-[1px] h-full bg-border my-2" />}
      </div>
      <div className="pb-12 pt-1">
        <h3 className="text-[17px] font-semibold mb-2 group-hover:text-accent transition-colors">{title}</h3>
        <p className="text-[15px] text-text-secondary leading-relaxed">{description}</p>
      </div>
    </div>
  );
}

function Stat({ value, label }: { value: string, label: string }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-[32px] font-serif text-accent">{value}</span>
      <span className="text-[11px] font-bold text-text-muted uppercase tracking-wider">{label}</span>
    </div>
  );
}
