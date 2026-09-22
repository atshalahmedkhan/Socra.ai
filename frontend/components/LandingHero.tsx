"use client";

import React from "react";

interface LandingHeroProps {
  onStartQuiz: () => void;
  onGoToPractice: () => void;
}

export default function LandingHero({ onStartQuiz, onGoToPractice }: LandingHeroProps) {
  return (
    <div className="relative flex flex-col items-center justify-center text-center px-4 py-16 md:py-24 max-w-5xl mx-auto">
      {/* Background glow orb */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-cyan-500/15 rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="absolute top-1/3 left-1/3 w-80 h-80 bg-purple-500/15 rounded-full blur-3xl pointer-events-none -z-10" />

      {/* Pill Badge */}
      <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass-panel border border-cyan-500/30 text-xs font-semibold text-cyan-400 mb-6 shadow-inner tracking-wide uppercase">
        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
        Socratic AI Tutoring & Remediation Engine
      </div>

      {/* Main Headline */}
      <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight mb-6">
        Master Computer Science via{" "}
        <span className="text-gradient">Active Discovery</span>
      </h1>

      {/* Subtitle */}
      <p className="text-lg sm:text-xl text-slate-300 max-w-2xl mx-auto mb-10 leading-relaxed font-normal">
        Socra does not give away the code. It diagnoses your exact misconception and guides you step-by-step with progressive Socratic hints until you truly master the concept.
      </p>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row items-center gap-4 mb-16 w-full sm:w-auto">
        <button
          onClick={onStartQuiz}
          className="w-full sm:w-auto px-8 py-4 rounded-xl bg-gradient-to-r from-cyan-500 via-indigo-500 to-purple-600 text-white font-semibold shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 cursor-pointer text-base flex items-center justify-center gap-2"
        >
          <span>🚀 Start 3-Question Diagnostic Quiz</span>
        </button>

        <button
          onClick={onGoToPractice}
          className="w-full sm:w-auto px-7 py-4 rounded-xl glass-panel text-slate-200 font-medium hover:bg-slate-800/80 hover:text-white border border-slate-700 transition-all duration-200 cursor-pointer text-base"
        >
          View Practice & Weak Points
        </button>
      </div>

      {/* Feature cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full text-left">
        <div className="p-6 rounded-2xl glass-panel border border-slate-800 hover:border-cyan-500/40 transition-all duration-300">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-xl mb-4">
            🔍
          </div>
          <h2 className="text-lg font-bold text-white mb-2">Diagnostic Assessment</h2>
          <p className="text-sm text-slate-400 leading-relaxed">
            Attempt CS challenges. Socra analyzes your reasoning to flag edge-case confusion, inversion, or boundary traps.
          </p>
        </div>

        <div className="p-6 rounded-2xl glass-panel border border-slate-800 hover:border-rose-500/40 transition-all duration-300">
          <div className="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-xl mb-4">
            🚨
          </div>
          <h2 className="text-lg font-bold text-white mb-2">Red Weak-Point Detection</h2>
          <p className="text-sm text-slate-400 leading-relaxed">
            Weak areas are immediately highlighted in red on your practice dashboard so you never waste time studying what you already know.
          </p>
        </div>

        <div className="p-6 rounded-2xl glass-panel border border-slate-800 hover:border-purple-500/40 transition-all duration-300">
          <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-xl mb-4">
            🪜
          </div>
          <h2 className="text-lg font-bold text-white mb-2">5-Level Adaptive Remediation</h2>
          <p className="text-sm text-slate-400 leading-relaxed">
            Engage in interactive Socratic dialog. Socra adapts hint levels from gentle probes to decomposition and guided analogies.
          </p>
        </div>
      </div>
    </div>
  );
}
