"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_LINKS = [
  { name: "How it Works", href: "/#how-it-works" },
  { name: "Dictionary", href: "/dictionary" },
  { name: "Research", href: "/research" },
];

export default function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <nav
      className={cn(
        "fixed top-0 left-0 right-0 z-50 transition-all duration-300",
        isScrolled || isMobileMenuOpen
          ? "bg-surface/80 backdrop-blur-md border-b border-border py-3"
          : "bg-transparent py-5"
      )}
    >
      <div className="max-w-[1200px] mx-auto px-6 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 bg-accent text-white flex items-center justify-center rounded-sm font-bold text-lg transition-transform group-hover:scale-105">
            S
          </div>
          <span className="font-semibold text-[17px] tracking-tight text-text-primary">
            SignSpeak
          </span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-8">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.name}
              href={link.href}
              className={cn(
                "text-[15px] font-medium transition-colors hover:text-text-primary",
                pathname === link.href ? "text-text-primary" : "text-text-secondary"
              )}
            >
              {link.name}
            </Link>
          ))}
        </div>

        {/* Desktop Actions */}
        <div className="hidden md:flex items-center gap-4">
          <button className="text-[13px] font-medium text-text-secondary hover:text-text-primary px-4 py-2 transition-colors">
            Sign In
          </button>
          <Link
            href="/translate"
            className="bg-accent text-white text-[13px] font-medium px-5 py-2.5 rounded-sm hover:bg-accent-hover transition-all flex items-center gap-2"
          >
            Try Free
            <ArrowRight size={14} />
          </Link>
        </div>

        {/* Mobile Menu Toggle */}
        <button
          className="md:hidden text-text-primary"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        >
          {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
            className="absolute top-full left-0 right-0 bg-surface border-b border-border md:hidden overflow-hidden"
          >
            <div className="px-6 py-8 flex flex-col gap-6">
              {NAV_LINKS.map((link) => (
                <Link
                  key={link.name}
                  href={link.href}
                  className="text-lg font-medium text-text-primary"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {link.name}
                </Link>
              ))}
              <hr className="border-border" />
              <div className="flex flex-col gap-4">
                <button className="text-lg font-medium text-text-secondary text-left">
                  Sign In
                </button>
                <Link
                  href="/translate"
                  className="bg-accent text-white text-center py-3 rounded-sm font-medium"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Try Free
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
