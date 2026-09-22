"use client";

import React, { useEffect, useRef, useState } from "react";
import { RemediationTurn, TopicMastery } from "../types/quiz";

interface InteractiveRemediationQuizProps {
  topic: TopicMastery;
  onExit: () => void;
}

export default function InteractiveRemediationQuiz({
  topic,
  onExit,
}: InteractiveRemediationQuizProps) {
  const [messages, setMessages] = useState<RemediationTurn[]>([
    {
      id: "intro-1",
      sender: "socra",
      content: `Welcome to your Socratic Remediation Session on **${topic.title}**! 🎯\n\nI noticed you had some difficulty with base case boundary conditions in recursive search and insertion. Let's work through this step-by-step with interactive questions and guided reasoning.`,
      timestamp: "Just now",
    },
    {
      id: "quiz-mcq-1",
      sender: "socra",
      content: "Let's start with a foundational check. Look at this recursive tree traversal snippet. Which line will crash if `root` is `None`?",
      isQuestion: true,
      questionData: {
        type: "mcq",
        options: [
          { label: "A", text: "Line 1: if root.val == target:", isCorrect: true },
          { label: "B", text: "Line 2: return search(root.left, target)", isCorrect: false },
          { label: "C", text: "Line 3: return False", isCorrect: false },
        ],
        answered: false,
      },
      timestamp: "Just now",
    },
  ]);

  const [inputVal, setInputVal] = useState("");
  const [currentHintLevel, setCurrentHintLevel] = useState<number>(0);
  const [cognitiveState, setCognitiveState] = useState<
    "exploring" | "struggling" | "stuck" | "mastered" | "making_progress"
  >("exploring");
  const [activeMisconception, setActiveMisconception] = useState<string>("Off-by-One / Null Boundary Check");
  const [isAiTyping, setIsAiTyping] = useState(false);
  const [hintsUsed, setHintsUsed] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isAiTyping]);

  const hintLevelLabels: Record<number, { title: string; color: string; desc: string }> = {
    0: { title: "Level 0 · Socratic Probe", color: "text-cyan-400 border-cyan-500/30", desc: "Open guiding question" },
    1: { title: "Level 1 · Conceptual Pointer", color: "text-blue-400 border-blue-500/30", desc: "Core definition reminder" },
    2: { title: "Level 2 · Strategic Hint", color: "text-amber-400 border-amber-500/30", desc: "Heuristic and approach guide" },
    3: { title: "Level 3 · Decomposition", color: "text-orange-400 border-orange-500/30", desc: "Sub-problem breakdown" },
    4: { title: "Level 4 · Worked Analogy", color: "text-pink-400 border-pink-500/30", desc: "Real-world analogous pattern" },
    5: { title: "Level 5 · Bottom-Out Walkthrough", color: "text-emerald-400 border-emerald-500/30", desc: "Step-by-step resolution" },
  };

  const handleSelectQuizOption = (msgId: string, optionLabel: string, isCorrect: boolean) => {
    setMessages((prev) =>
      prev.map((m) =>
        m.id === msgId && m.questionData
          ? {
              ...m,
              questionData: {
                ...m.questionData,
                answered: true,
                selectedLabel: optionLabel,
                isCorrect,
              },
            }
          : m
      )
    );

    setIsAiTyping(true);
    setTimeout(() => {
      if (isCorrect) {
        setCognitiveState("making_progress");
        setMessages((prev) => [

          ...prev,
          {
            id: `socra-resp-${Date.now()}`,
            sender: "socra",
            content: `Spot on! 🎉 Line 1 crashes because accessing \`root.val\` when \`root is None\` triggers an immediate error before any check.\n\nNow, here is a short-answer challenge for you:\n**In 1-2 sentences, what line of code should we place before Line 1 to safely handle this boundary condition?**`,
            timestamp: "Just now",
          },
        ]);
      } else {
        setCognitiveState("struggling");
        setMessages((prev) => [
          ...prev,
          {
            id: `socra-resp-${Date.now()}`,
            sender: "socra",
            content: `Not quite. If \`root\` is \`None\`, Python cannot read \`root.val\` or \`root.left\`—it fails immediately on the property access!\n\n**Socratic Question:** Before you examine what is *inside* the node, what is the prerequisite check you must perform on the node itself?`,
            hintLevel: 1,
            timestamp: "Just now",
          },
        ]);
      }
      setIsAiTyping(false);
    }, 1000);
  };

  const handleSendMessage = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const text = inputVal.trim();
    if (!text || isAiTyping) return;

    const userTurn: RemediationTurn = {
      id: `user-${Date.now()}`,
      sender: "student",
      content: text,
      timestamp: "Just now",
    };

    setMessages((prev) => [...prev, userTurn]);
    setInputVal("");
    setIsAiTyping(true);

    const lower = text.toLowerCase();
    setTimeout(() => {
      // Socratic feedback logic
      if (
        lower.includes("if root is none") ||
        lower.includes("if not root") ||
        lower.includes("if root == none") ||
        lower.includes("check if none")
      ) {
        setCognitiveState("mastered");
        setActiveMisconception("None Detected · Concept Mastered");
        setMessages((prev) => [
          ...prev,
          {
            id: `socra-${Date.now()}`,
            sender: "socra",
            content: `🌟 **Mastery Achieved!**\n\nExactly: \`if root is None: return False\` (or return a newly constructed node for insertion).\n\nBy placing the null-check as the very first line of your recursive function, you ensure that every sub-tree traversal terminates safely without ever throwing an exception.\n\nReady to return to the practice dashboard?`,
            timestamp: "Just now",
          },
        ]);
      } else if (lower.includes("help") || lower.includes("hint") || lower.includes("idk") || lower.includes("don't know")) {
        setCognitiveState("struggling");
        const nextHint = Math.min(5, currentHintLevel + 1);
        setCurrentHintLevel(nextHint);
        setHintsUsed((h) => h + 1);
        setMessages((prev) => [
          ...prev,
          {
            id: `socra-${Date.now()}`,
            sender: "socra",
            content: `No worries, let's look at this hint (Level ${nextHint}):\n\nThink about what Python evaluates first. If a box is empty (\`None\`), trying to look inside the box will fail. You must ask: *"Is this box empty?"* before opening it. How would you write that in Python?`,
            hintLevel: nextHint,
            timestamp: "Just now",
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            id: `socra-${Date.now()}`,
            sender: "socra",
            content: `I see what you're thinking! Let's refine it: How do we test if \`root\` is empty or null before accessing its properties? Try typing the Python \`if\` statement.`,
            timestamp: "Just now",
          },
        ]);
      }
      setIsAiTyping(false);
    }, 1100);
  };

  const handleRequestHint = () => {
    if (isAiTyping) return;
    const nextLevel = Math.min(5, currentHintLevel + 1);
    setCurrentHintLevel(nextLevel);
    setHintsUsed((h) => h + 1);
    setIsAiTyping(true);

    setTimeout(() => {
      let hintText = "";
      if (nextLevel === 1) {
        hintText = "💡 **Level 1 (Conceptual Pointer):** In recursive trees, the base case must check if the current pointer itself is null before evaluating `node.val` or `node.left`.";
      } else if (nextLevel === 2) {
        hintText = "💡 **Level 2 (Strategic Hint):** Use Python's `is None` identity check at the very top of your function body.";
      } else if (nextLevel === 3) {
        hintText = "💡 **Level 3 (Decomposition):** Step 1: Write `if root is None:`. Step 2: Decide what to return (e.g. `False` for search, or `TreeNode(val)` for insert).";
      } else if (nextLevel === 4) {
        hintText = "💡 **Level 4 (Worked Analogy):** Imagine walking down a path until the road ends. Before you try taking another step, you check if the road is there. If the road is `None`, you stop!";
      } else {
        hintText = "💡 **Level 5 (Bottom-Out Walkthrough):** Here is the complete safe base case:\n```python\nif root is None:\n    return False\n```\nNotice how this prevents any AttributeError. Does this make sense?";
      }

      setMessages((prev) => [
        ...prev,
        {
          id: `hint-${Date.now()}`,
          sender: "socra",
          content: hintText,
          hintLevel: nextLevel,
          timestamp: "Just now",
        },
      ]);
      setIsAiTyping(false);
    }, 800);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 flex flex-col h-[calc(100vh-5rem)]">
      {/* Top Bar HUD */}
      <div className="glass-panel p-4 rounded-2xl mb-4 border border-slate-800 flex flex-wrap items-center justify-between gap-3 shrink-0">
        <div className="flex items-center gap-3">
          <button
            onClick={onExit}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors"
          >
            ← Back to Practice
          </button>
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <h1 className="text-sm sm:text-base font-bold text-white">
                Socra AI Socratic Remediation
              </h1>
            </div>
            <p className="text-xs text-slate-400">{topic.title}</p>
          </div>
        </div>

        {/* Diagnostic Status Indicators */}
        <div className="flex items-center gap-2">
          {/* Cognitive State */}
          <div className="px-2.5 py-1 rounded-full bg-slate-800 border border-slate-700 text-[11px] font-medium text-slate-300 flex items-center gap-1.5">
            <span>State:</span>
            <span
              className={`font-bold capitalize ${
                cognitiveState === "mastered"
                  ? "text-emerald-400"
                  : cognitiveState === "stuck"
                  ? "text-rose-400"
                  : cognitiveState === "struggling"
                  ? "text-amber-400"
                  : "text-cyan-400"
              }`}
            >
              {cognitiveState}
            </span>
          </div>

          {/* Hint Level Pill */}
          <div
            className={`px-2.5 py-1 rounded-full bg-slate-800 border text-[11px] font-medium ${
              hintLevelLabels[currentHintLevel].color
            }`}
          >
            {hintLevelLabels[currentHintLevel].title}
          </div>
        </div>
      </div>

      {/* Main Chat and Dialogue View */}
      <div className="flex-1 glass-panel rounded-2xl p-4 sm:p-6 overflow-y-auto mb-4 border border-slate-800 space-y-4">
        {/* Topic Misconception Focus Banner */}
        <div className="p-3.5 rounded-xl bg-cyan-950/40 border border-cyan-500/20 text-xs text-cyan-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-base">🎯</span>
            <span>
              <strong>Remediation Target:</strong> {activeMisconception}
            </span>
          </div>
          <span className="text-slate-400 text-[11px]">Hints Used: {hintsUsed}</span>
        </div>

        {messages.map((m) => {
          const isSocra = m.sender === "socra";
          return (
            <div
              key={m.id}
              className={`flex flex-col ${isSocra ? "items-start" : "items-end"}`}
            >
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-semibold text-slate-400">
                  {isSocra ? "🤖 Socra Socratic Tutor" : "🧑‍💻 You"}
                </span>
                {m.hintLevel !== undefined && (
                  <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-amber-300 border border-amber-500/30">
                    Hint L{m.hintLevel}
                  </span>
                )}
              </div>

              <div
                className={`max-w-[85%] sm:max-w-[75%] p-4 rounded-2xl text-sm sm:text-base leading-relaxed ${
                  isSocra
                    ? "bg-slate-900/90 border border-slate-700/60 text-slate-100 shadow-md"
                    : "bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-md shadow-cyan-900/30"
                }`}
              >
                <div className="whitespace-pre-line">{m.content}</div>

                {/* Embedded Interactive MCQ inside Dialogue */}
                {m.isQuestion && m.questionData?.type === "mcq" && (
                  <div className="mt-4 pt-3 border-t border-slate-800 space-y-2">
                    {m.questionData.options?.map((opt) => {
                      const isAnswered = m.questionData?.answered;
                      const isSelected = m.questionData?.selectedLabel === opt.label;
                      return (
                        <button
                          key={opt.label}
                          disabled={isAnswered}
                          onClick={() => handleSelectQuizOption(m.id, opt.label, opt.isCorrect)}
                          className={`w-full text-left p-3 rounded-xl border text-xs sm:text-sm font-medium transition-all cursor-pointer flex items-center justify-between ${
                            isSelected
                              ? opt.isCorrect
                                ? "bg-emerald-950/60 border-emerald-400 text-emerald-200"
                                : "bg-rose-950/60 border-rose-400 text-rose-200"
                              : "bg-slate-800/80 border-slate-700 text-slate-200 hover:bg-slate-750 hover:border-slate-600"
                          }`}
                        >
                          <div className="flex items-center gap-2.5">
                            <span className="w-5 h-5 rounded-full bg-slate-900 border border-slate-700 flex items-center justify-center text-[10px] font-bold">
                              {opt.label}
                            </span>
                            <span>{opt.text}</span>
                          </div>
                          {isSelected && (
                            <span className="text-xs font-bold">
                              {opt.isCorrect ? "✓ Correct" : "✕ Try Again"}
                            </span>
                          )}
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {isAiTyping && (
          <div className="flex items-center gap-2 text-xs text-cyan-400 py-2">
            <span className="animate-spin text-base">⚙️</span>
            <span>Socra AI is diagnosing your answer and formulating Socratic feedback...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Bottom Action bar & Input */}
      <div className="glass-panel p-3 rounded-2xl border border-slate-800 shrink-0 space-y-2.5">
        {/* Quick hint trigger bar */}
        <div className="flex items-center justify-between px-1">
          <button
            onClick={handleRequestHint}
            disabled={isAiTyping || currentHintLevel >= 5}
            className="px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 hover:bg-amber-500/20 text-xs font-semibold transition-all disabled:opacity-40 cursor-pointer flex items-center gap-1.5"
          >
            <span>💡 Request Progressive Hint (L{Math.min(5, currentHintLevel + 1)})</span>
          </button>

          <span className="text-[11px] text-slate-400 hidden sm:inline">
            Type your reasoning or answer below
          </span>
        </div>

        {/* Input Form */}
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <input
            type="text"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder="Type your answer, code, or question to Socra..."
            className="flex-1 px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 text-sm font-mono"
          />
          <button
            type="submit"
            disabled={!inputVal.trim() || isAiTyping}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold text-sm hover:opacity-95 shadow-md shadow-cyan-500/20 disabled:opacity-40 cursor-pointer transition-all"
          >
            Send ⏎
          </button>
        </form>
      </div>
    </div>
  );
}
