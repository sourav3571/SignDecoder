"use client";

import React, { useEffect, useState, useRef } from "react";
import { motion } from "framer-motion";
import Lottie, { LottieRefCurrentProps } from "lottie-react";
import { cn } from "@/lib/utils";

export type SemanticRole = "SUBJECT" | "VERB" | "OBJECT" | "TIME" | "LOCATION" | "NEGATION";

interface EmojiCardProps {
  emoji: string;
  word: string;
  role: SemanticRole;
  confidence?: number;
  lottieSrc?: string;
  index: number;
  isActive?: boolean;
  onAnimationComplete?: () => void;
  showEmoji?: boolean;
}

const ROLE_COLORS: Record<SemanticRole, string> = {
  SUBJECT: "bg-role-subject",
  VERB: "bg-role-verb",
  OBJECT: "bg-role-object",
  TIME: "bg-role-time",
  LOCATION: "bg-role-location",
  NEGATION: "bg-role-negation",
};

export default function EmojiCard({
  emoji,
  word,
  role,
  lottieSrc,
  index,
  isActive = false,
  onAnimationComplete,
  showEmoji = true,
}: EmojiCardProps) {
  const [animationData, setAnimationData] = useState<Record<string, unknown> | null>(null);
  const lottieRef = useRef<LottieRefCurrentProps>(null);

  useEffect(() => {
    if (lottieSrc) {
      fetch(lottieSrc)
        .then((res) => res.json())
        .then((data) => setAnimationData(data))
        .catch(() => setAnimationData(null));
    }
  }, [lottieSrc]);

  useEffect(() => {
    if (isActive) {
      if (animationData && lottieRef.current) {
        lottieRef.current.goToAndPlay(0);
      } else {
        const timer = setTimeout(() => {
          if (onAnimationComplete) {
            onAnimationComplete();
          }
        }, 1200); 
        return () => clearTimeout(timer);
      }
    }
  }, [isActive, animationData, onAnimationComplete]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ 
        duration: 0.3, 
        delay: index * 0.1,
        ease: "easeOut"
      }}
      className={cn(
        "group relative flex flex-col items-center justify-between w-[120px] p-5 bg-white border border-border rounded-md shadow-sm transition-all duration-200 hover:shadow-md hover:-translate-y-0.5",
        isActive && "border-accent ring-1 ring-accent/10 shadow-lg"
      )}
      aria-label={`${word} (${role})`}
    >
      {}
      <div className={cn("absolute top-4 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full", ROLE_COLORS[role])} />

      {}
      <div className="my-3 flex items-center justify-center h-[60px] w-full">
        {animationData ? (
          <Lottie
            lottieRef={lottieRef}
            animationData={animationData}
            loop={false}
            autoplay={false}
            onComplete={onAnimationComplete}
            style={{ width: "100%", height: "100%" }}
          />
        ) : showEmoji ? (
          <div className="flex flex-row flex-nowrap items-center justify-center gap-1.5 max-w-full">
            {(emoji || "").split(/\s+/).filter(Boolean).map((em, idx) => {
              const count = (emoji || "").split(/\s+/).filter(Boolean).length;
              const sizeClass = count >= 3 ? "text-[22px]" : count === 2 ? "text-[30px]" : "text-[42px]";
              return (
                <span key={idx} className={sizeClass} role="img">
                  {em}
                </span>
              );
            })}
          </div>
        ) : (
          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-stone-50 border border-stone-200/50 text-stone-700 font-semibold text-[15px] select-none shadow-xs">
            {word[0]?.toUpperCase() || "S"}
          </div>
        )}
      </div>

      {}
      <div className="text-center mt-2">
        <span className="block text-[14px] font-medium text-text-primary leading-tight">
          {word}
        </span>
        <span className="block text-[10px] font-bold text-text-muted uppercase tracking-widest mt-1">
          {role}
        </span>
      </div>

      {}
      {isActive && (
        <motion.div 
          layoutId="active-indicator"
          className="absolute -bottom-[1px] left-0 right-0 h-0.5 bg-accent rounded-full"
        />
      )}
    </motion.div>
  );
}
