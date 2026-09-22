"use client";

import React from "react";
import { TopicMastery } from "../types/quiz";

interface PracticeDashboardProps {
  topics: TopicMastery[];
  onStartRemediation: (topic: TopicMastery) => void;
  onRetakeQuiz: () => void;
}

export default function PracticeDashboard({
  topics,
  onStartRemediation,
  onRetakeQuiz,
}: PracticeDashboardProps) {
  const weakPoints = topics.filter((t) => t.isWeakPoint);
  const masteredTopics = topics.filter((t) => !t.isWeakPoint);

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 pb-6 border-b border-slate-800">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800 text-xs font-semibold text-cyan-400 mb-2">
            🎯 Diagnostic Assessment Results
          </div>
          <h1 className="text-3xl font-extrabold text-white">
            Your CS Knowledge & Practice Matrix
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Review your diagnosed strong points and critical weak areas below. Click on any topic in red to launch AI Socratic remediation.
          </p>
        </div>

        <button
          onClick={onRetakeQuiz}
          className="px-4 py-2.5 rounded-xl glass-panel text-xs sm:text-sm font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition-all shrink-0 self-start sm:self-center"
        >
          🔄 Retake Diagnostic Quiz
        </button>
      </div>

      {/* Weak Points Section (IN RED) */}
      <div className="mb-10">
        <div className="flex items-center gap-3 mb-4">
          <span className="flex h-3 w-3 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500" />
          </span>
          <h2 className="text-xl font-bold text-rose-400 tracking-wide uppercase text-sm">
            Critical Weak Points Identified (Action Required)
          </h2>
        </div>

        {weakPoints.length > 0 ? (
          <div className="space-y-4">
            {weakPoints.map((topic) => (
              <div
                key={topic.id}
                onClick={() => onStartRemediation(topic)}
                className="glass-panel-danger p-6 rounded-2xl border cursor-pointer hover:scale-[1.01] transition-all duration-300 group relative overflow-hidden"
              >
                {/* Background red glow accent */}
                <div className="absolute top-0 right-0 w-48 h-48 bg-rose-500/10 rounded-full blur-2xl pointer-events-none" />

                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="space-y-2 max-w-2xl">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="px-3 py-1 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 text-xs font-bold uppercase tracking-wider">
                        🚨 Weak Point · Needs Remediation
                      </span>
                      <span className="text-xs text-rose-400 font-mono">
                        Score: {topic.score}% ({topic.correctQuestions}/{topic.totalQuestions} correct)
                      </span>
                    </div>

                    <h3 className="text-xl font-bold text-white group-hover:text-rose-200 transition-colors">
                      {topic.title}
                    </h3>

                    <p className="text-sm text-slate-300">
                      {topic.description}
                    </p>

                    {topic.misconceptionAlert && (
                      <div className="p-3.5 rounded-xl bg-rose-950/60 border border-rose-500/30 text-xs text-rose-200 mt-3 flex items-start gap-2.5">
                        <span className="text-base shrink-0">⚠️</span>
                        <span>
                          <strong className="text-rose-100">AI Diagnostic finding:</strong>{" "}
                          {topic.misconceptionAlert}
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="shrink-0 flex flex-col items-start md:items-end justify-center pt-2 md:pt-0">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onStartRemediation(topic);
                      }}
                      className="w-full md:w-auto px-6 py-3 rounded-xl bg-gradient-to-r from-rose-600 via-pink-600 to-purple-600 text-white font-bold text-sm shadow-lg shadow-rose-600/30 hover:shadow-rose-600/50 hover:scale-105 active:scale-95 transition-all flex items-center justify-center gap-2"
                    >
                      <span>🤖 Ask AI for Interactive Socratic Quiz</span>
                      <span>→</span>
                    </button>
                    <span className="text-[11px] text-rose-300/80 mt-1.5 hidden md:block">
                      Includes MCQ + Guided Socratic Dialogue
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-6 rounded-2xl glass-panel-success border text-emerald-300 text-sm">
            🎉 Great job! No critical weak points detected in this evaluation.
          </div>
        )}
      </div>

      {/* Mastered Topics Section (IN GREEN) */}
      <div>
        <h2 className="text-xl font-bold text-emerald-400 tracking-wide uppercase text-sm mb-4 flex items-center gap-2">
          <span>✅</span> Proficient & Mastered Topics
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {masteredTopics.map((topic) => (
            <div
              key={topic.id}
              className="glass-panel-success p-5 rounded-2xl border border-emerald-500/30"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-bold">
                  ✓ Mastered (100%)
                </span>
                <span className="text-xs text-emerald-400 font-mono">
                  {topic.correctQuestions}/{topic.totalQuestions} Passed
                </span>
              </div>
              <h3 className="text-base font-bold text-white mb-1">{topic.title}</h3>
              <p className="text-xs text-slate-300">{topic.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
