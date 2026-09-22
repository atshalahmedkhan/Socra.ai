"use client";

import React, { useState } from "react";
import DiagnosticQuiz from "../components/DiagnosticQuiz";
import InteractiveRemediationQuiz from "../components/InteractiveRemediationQuiz";
import LandingHero from "../components/LandingHero";
import PracticeDashboard from "../components/PracticeDashboard";
import { AppStage, TopicMastery } from "../types/quiz";

const DEFAULT_TOPICS: TopicMastery[] = [
  {
    id: "recursion_base_cases",
    title: "Recursion Base Cases & Boundary Off-by-One",
    description: "Handling null references, empty structures, and pointer re-assignment in recursive trees.",
    score: 35,
    totalQuestions: 2,
    correctQuestions: 0,
    isWeakPoint: true,
    misconceptionAlert:
      "Critical Weak Point: Attempting to access node properties before verifying null reference, causing crash on missing keys.",
    recommendedFocus: "Socratic breakdown on base-case guards & pointer linking.",
  },
  {
    id: "tree_traversal",
    title: "Binary Tree Traversal Properties",
    description: "Understanding Inorder vs Preorder vs Postorder recursive flow on binary structures.",
    score: 100,
    totalQuestions: 1,
    correctQuestions: 1,
    isWeakPoint: false,
    recommendedFocus: "Reviewing DFS traversal call stacks.",
  },
];

export default function Home() {
  const [stage, setStage] = useState<AppStage>("landing");
  const [topics, setTopics] = useState<TopicMastery[]>(DEFAULT_TOPICS);
  const [activeTopic, setActiveTopic] = useState<TopicMastery>(DEFAULT_TOPICS[0]);

  const handleQuizComplete = (results: TopicMastery[]) => {
    setTopics(results);
    setStage("practice");
  };

  const handleStartRemediation = (topic: TopicMastery) => {
    setActiveTopic(topic);
    setStage("remediation");
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#090d16] text-slate-100 selection:bg-cyan-500 selection:text-black">
      {/* Navigation Header */}
      <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div
            onClick={() => setStage("landing")}
            className="flex items-center gap-2.5 cursor-pointer group"
          >
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center font-black text-white shadow-md shadow-cyan-500/30 group-hover:scale-105 transition-transform">
              Σ
            </div>
            <span className="text-xl font-extrabold tracking-tight text-white group-hover:text-cyan-400 transition-colors">
              Socra<span className="text-cyan-400">.ai</span>
            </span>
          </div>

          <nav className="flex items-center gap-2 sm:gap-4 text-xs sm:text-sm font-medium">
            <button
              onClick={() => setStage("landing")}
              className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                stage === "landing"
                  ? "text-cyan-400 bg-cyan-950/40 border border-cyan-500/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setStage("quiz")}
              className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                stage === "quiz"
                  ? "text-cyan-400 bg-cyan-950/40 border border-cyan-500/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Diagnostic Quiz
            </button>
            <button
              onClick={() => setStage("practice")}
              className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer flex items-center gap-1.5 ${
                stage === "practice" || stage === "remediation"
                  ? "text-rose-400 bg-rose-950/40 border border-rose-500/30 font-bold"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
              Practice & Weak Points
            </button>
          </nav>
        </div>
      </header>

      {/* Main Dynamic Stage View */}
      <main className="flex-1 flex flex-col justify-center">
        {stage === "landing" && (
          <LandingHero
            onStartQuiz={() => setStage("quiz")}
            onGoToPractice={() => setStage("practice")}
          />
        )}

        {stage === "quiz" && (
          <DiagnosticQuiz
            onComplete={handleQuizComplete}
            onCancel={() => setStage("landing")}
          />
        )}

        {stage === "practice" && (
          <PracticeDashboard
            topics={topics}
            onStartRemediation={handleStartRemediation}
            onRetakeQuiz={() => setStage("quiz")}
          />
        )}

        {stage === "remediation" && (
          <InteractiveRemediationQuiz
            topic={activeTopic}
            onExit={() => setStage("practice")}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500">
        Socra Socratic AI Tutoring Platform · Fine-Tuned Gemma Model Scaffold
      </footer>
    </div>
  );
}
