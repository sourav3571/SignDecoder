import React from "react";
import { ArrowRight, FileText, ExternalLink } from "lucide-react";

export default function ResearchPage() {
  return (
    <div className="pt-32 pb-32 bg-white">
      <article className="max-w-[720px] mx-auto px-6">
        {}
        <header className="mb-16 border-b border-border pb-16">
          <span className="text-[11px] font-bold text-text-muted uppercase tracking-[0.1em] mb-6 block">
            RESEARCH PAPER &middot; 2024
          </span>
          <h1 className="font-serif text-[42px] md:text-[54px] leading-[1.1] text-text-primary mb-8">
            SignSpeak: A Rule-Based and Neural Hybrid Approach to English-to-Sign Language Translation
          </h1>
          
          <div className="flex flex-wrap gap-x-8 gap-y-4 text-[15px] text-text-secondary">
            <div>
              <span className="block font-semibold text-text-primary">Sourav Kumar</span>
              <span>B.Tech CSE, 2026</span>
            </div>
            <div>
              <span className="block font-semibold text-text-primary">Supervised by</span>
              <span>Dept. of CS</span>
            </div>
          </div>
        </header>

        {}
        <section className="mb-16">
          <h2 className="text-[13px] font-bold text-text-muted uppercase tracking-[0.1em] mb-6">
            Abstract
          </h2>
          <p className="text-[17px] leading-[1.8] text-text-primary italic bg-surface-elevated p-8 rounded-sm border-l-4 border-accent">
            Communication barriers for deaf and mute individuals remain a significant challenge in modern society. Current translation systems often struggle with the unique grammatical structures of sign languages. SignSpeak proposes a hybrid methodology that combines Natural Language Processing (NLP) for semantic extraction with a rule-based engine for grammatical reordering. By mapping text to sequential visual emoji representations, we provide an intuitive and accessible bridge for non-signers to communicate with the deaf community.
          </p>
        </section>

        {}
        <section className="mb-16">
          <h2 className="text-[13px] font-bold text-text-muted uppercase tracking-[0.1em] mb-6">
            Methodology
          </h2>
          <p className="text-[16px] leading-[1.8] text-text-secondary mb-10">
            The SignSpeak pipeline follows a strictly defined four-stage process to ensure linguistic accuracy and visual clarity.
          </p>
          
          {}
          <div className="bg-surface-elevated border border-border p-8 rounded-md mb-10">
            <div className="flex flex-col gap-6">
              <div className="flex items-center gap-6">
                <div className="w-12 h-12 bg-accent text-white flex items-center justify-center rounded-sm font-bold shrink-0">1</div>
                <div>
                  <h4 className="font-semibold text-text-primary">Input Normalization</h4>
                  <p className="text-[13px] text-text-secondary">Text cleaning, punctuation removal, and lowercasing.</p>
                </div>
              </div>
              <div className="ml-6 border-l-2 border-border h-6" />
              <div className="flex items-center gap-6">
                <div className="w-12 h-12 bg-white border-2 border-accent text-accent flex items-center justify-center rounded-sm font-bold shrink-0">2</div>
                <div>
                  <h4 className="font-semibold text-text-primary">Semantic Parsing</h4>
                  <p className="text-[13px] text-text-secondary">Dependency parsing using spaCy to extract S-V-O components.</p>
                </div>
              </div>
              <div className="ml-6 border-l-2 border-border h-6" />
              <div className="flex items-center gap-6">
                <div className="w-12 h-12 bg-white border-2 border-accent text-accent flex items-center justify-center rounded-sm font-bold shrink-0">3</div>
                <div>
                  <h4 className="font-semibold text-text-primary">Grammatical Mapping</h4>
                  <p className="text-[13px] text-text-secondary">Reordering logic applied to convert English to Sign grammar (e.g. T-L-S-O-V).</p>
                </div>
              </div>
              <div className="ml-6 border-l-2 border-border h-6" />
              <div className="flex items-center gap-6">
                <div className="w-12 h-12 bg-accent text-white flex items-center justify-center rounded-sm font-bold shrink-0">4</div>
                <div>
                  <h4 className="font-semibold text-text-primary">Visual Rendering</h4>
                  <p className="text-[13px] text-text-secondary">Mapping glosses to high-fidelity Lottie animations and emojis.</p>
                </div>
              </div>
            </div>
            <p className="mt-8 text-center text-[12px] text-text-muted italic">
              Figure 1: The SignSpeak architectural pipeline.
            </p>
          </div>
        </section>

        {}
        <section className="mb-16">
          <h2 className="text-[13px] font-bold text-text-muted uppercase tracking-[0.1em] mb-6">
            Dataset & Training
          </h2>
          <p className="text-[16px] leading-[1.8] text-text-secondary mb-6">
            Our mapping engine is trained on the PHOENIX-2014T dataset, combined with a custom-curated dictionary of 1,000+ high-frequency Indian Sign Language (ISL) and American Sign Language (ASL) glosses.
          </p>
          <ul className="list-disc list-inside space-y-3 text-[16px] text-text-secondary ml-4">
            <li>PHOENIX-2014T (Weather domain)</li>
            <li>ASL Lexicon Project (Boston University)</li>
            <li>Custom ISL Corpus for everyday conversation</li>
          </ul>
        </section>

        {}
        <section className="mb-16">
          <h2 className="text-[13px] font-bold text-text-muted uppercase tracking-[0.1em] mb-6">
            Evaluation Results
          </h2>
          <div className="overflow-hidden border border-border rounded-md shadow-sm mb-10">
            <table className="w-full text-left text-[14px]">
              <thead className="bg-surface-elevated border-b border-border">
                <tr>
                  <th className="px-6 py-4 font-semibold text-text-primary">Metric</th>
                  <th className="px-6 py-4 font-semibold text-text-primary">Score</th>
                  <th className="px-6 py-4 font-semibold text-text-primary">Benchmark</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                <tr>
                  <td className="px-6 py-4 text-text-secondary">BLEU-4</td>
                  <td className="px-6 py-4 font-mono text-accent">0.682</td>
                  <td className="px-6 py-4 text-[12px] text-text-muted">High Precision</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-text-secondary">Emoji Accuracy</td>
                  <td className="px-6 py-4 font-mono text-accent">87.4%</td>
                  <td className="px-6 py-4 text-[12px] text-text-muted">Top-1 Accuracy</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-text-secondary">Latency (Avg)</td>
                  <td className="px-6 py-4 font-mono text-accent">142ms</td>
                  <td className="px-6 py-4 text-[12px] text-text-muted">Real-time Ready</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {}
        <section className="border-t border-border pt-16">
          <h2 className="text-[13px] font-bold text-text-muted uppercase tracking-[0.1em] mb-8">
            Selected References
          </h2>
          <div className="space-y-8 text-[14px] text-text-secondary">
            <p className="leading-relaxed">
              [1] Camgoz, N. C., et al. (2018). "Neural Sign Language Translation." IEEE Conference on Computer Vision and Pattern Recognition.
            </p>
            <p className="leading-relaxed">
              [2] Bragg, D., et al. (2019). "Sign Language Recognition, Generation, and Translation: An Interdisciplinary Perspective." ASSETS '19.
            </p>
          </div>
          
          <div className="mt-16 flex items-center justify-between p-6 bg-accent text-white rounded-md">
            <div className="flex items-center gap-4">
              <FileText size={24} />
              <div>
                <span className="block font-medium">Full Research PDF</span>
                <span className="text-[12px] opacity-80">14.2 MB &middot; English</span>
              </div>
            </div>
            <button className="px-4 py-2 bg-white text-accent rounded-sm text-[13px] font-bold hover:bg-surface-elevated transition-colors flex items-center gap-2">
              Download
              <ExternalLink size={14} />
            </button>
          </div>
        </section>
      </article>
    </div>
  );
}
