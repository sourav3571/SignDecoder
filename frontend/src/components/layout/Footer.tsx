import React from "react";
import Link from "next/link";

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-accent text-text-muted py-16 px-6">
      <div className="max-w-[1200px] mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">
          {/* Logo & Tagline */}
          <div className="col-span-1 md:col-span-1">
            <Link href="/" className="flex items-center gap-2 mb-6">
              <div className="w-8 h-8 bg-white text-accent flex items-center justify-center rounded-sm font-bold text-lg">
                S
              </div>
              <span className="font-semibold text-[17px] tracking-tight text-white">
                SignSpeak
              </span>
            </Link>
            <p className="text-[14px] leading-relaxed max-w-[200px]">
              Making the world more accessible through intelligent translation.
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 className="text-white font-medium text-[15px] mb-6">Product</h4>
            <ul className="space-y-4 text-[14px]">
              <li><Link href="/translate" className="hover:text-white transition-colors">Translator</Link></li>
              <li><Link href="/dictionary" className="hover:text-white transition-colors">Dictionary</Link></li>
              <li><Link href="/research" className="hover:text-white transition-colors">Research</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-medium text-[15px] mb-6">Resources</h4>
            <ul className="space-y-4 text-[14px]">
              <li><Link href="#" className="hover:text-white transition-colors">Documentation</Link></li>
              <li><Link href="#" className="hover:text-white transition-colors">API Reference</Link></li>
              <li><Link href="#" className="hover:text-white transition-colors">GitHub</Link></li>
            </ul>
          </div>

          <div className="text-right md:text-right">
            <p className="text-white font-medium text-[15px] mb-2">Built for accessibility</p>
            <p className="text-[13px]">B.Tech Final Year 2024</p>
          </div>
        </div>

        <div className="pt-8 border-t border-white/10 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-[12px]">
            &copy; {currentYear} SignDecoder. All rights reserved.
          </p>
          <div className="flex items-center gap-6 text-[12px]">
            <span>WCAG 2.1 AA Compliant</span>
            <Link href="#" className="hover:text-white transition-colors">Privacy Policy</Link>
            <Link href="#" className="hover:text-white transition-colors">Terms of Service</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
