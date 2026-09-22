"use client";

import React, { useState } from "react";
import { QuizQuestion, TopicMastery } from "../types/quiz";

const SAMPLE_QUESTIONS: QuizQuestion[] = [
  {
    id: "q1",
    topicId: "recursion_base_cases",
    topicTitle: "Recursion Base Cases & Boundary Conditions",
    question: "In a recursive binary search tree search function `search(node, target)`, what is the essential base case to prevent a NullPointerException/AttributeError when searching for a missing value?",
    codeSnippet: `def search_bst(node, target):
    # What must be checked FIRST here?
    if node.val == target:
        return True
    elif target < node.val:
        return search_bst(node.left, target)
    else:
        return search_bst(node.right, target)`,
    type: "mcq",
    options: [
      {
        label: "A",
        text: "if node.left is None and node.right is None: return False",
        isCorrect: false,
        feedback: "Incorrect: If node is None, accessing node.left raises an AttributeError before checking!",
      },
      {
        label: "B",
        text: "if node is None: return False",
        isCorrect: true,
        feedback: "Correct! Checking if node is None handles both an empty tree and reaching past a leaf.",
      },
      {
        label: "C",
        text: "if node.val is None: return False",
        isCorrect: false,
        feedback: "Incorrect: If node itself is None, evaluating node.val will immediately crash.",
      },
      {
        label: "D",
        text: "if target == 0: return False",
        isCorrect: false,
        feedback: "Incorrect: Target 0 is a valid key value and not a termination condition.",
      },
    ],
    explanation: "Recursive tree traversal must always guard against null node references as its fundamental base case before inspecting node attributes.",
  },
  {
    id: "q2",
    topicId: "tree_traversal",
    topicTitle: "Binary Tree Traversal Strategies",
    question: "Given a valid Binary Search Tree, which recursive traversal strategy guarantees that elements are visited in strictly ascending numerical order?",
    type: "mcq",
    options: [
      {
        label: "A",
        text: "Preorder Traversal (Root → Left → Right)",
        isCorrect: false,
        feedback: "Preorder visits root first, which does not output sorted order.",
      },
      {
        label: "B",
        text: "Inorder Traversal (Left → Root → Right)",
        isCorrect: true,
        feedback: "Correct! Inorder on a BST visits all smaller left elements, then root, then larger right elements.",
      },
      {
        label: "C",
        text: "Postorder Traversal (Left → Right → Root)",
        isCorrect: false,
        feedback: "Postorder visits children before parents, used typically for node deletion.",
      },
      {
        label: "D",
        text: "Breadth-First / Level Order Traversal",
        isCorrect: false,
        feedback: "Level-order traverses tier-by-tier and is not monotonic.",
      },
    ],
    explanation: "Inorder traversal naturally sorts a BST because Left Subtree < Root < Right Subtree.",
  },
  {
    id: "q3",
    topicId: "recursion_base_cases",
    topicTitle: "Recursion Base Cases & Boundary Conditions",
    question: "In recursive BST insertion `insert(root, val)`, what should be returned when the recursion reaches `root is None`?",
    codeSnippet: `def insert(root, val):
    if root is None:
        # What should be returned here?
        return ________
    if val < root.val:
        root.left = insert(root.left, val)
    else:
        root.right = insert(root.right, val)
    return root`,
    type: "short_answer",
    correctKeywords: ["treenode", "node", "new node", "treenode(val)", "node(val)"],
    explanation: "When hitting a None pointer, create and return a newly constructed Node(val) so the parent can hook its pointer to it.",
  },
];

interface DiagnosticQuizProps {
  onComplete: (topics: TopicMastery[]) => void;
  onCancel: () => void;
}

export default function DiagnosticQuiz({ onComplete, onCancel }: DiagnosticQuizProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [shortAnswers, setShortAnswers] = useState<Record<string, string>>({});
  const [isSubmitted, setIsSubmitted] = useState(false);

  const currentQ = SAMPLE_QUESTIONS[currentIndex];

  const handleSelectOption = (qId: string, optionLabel: string) => {
    setSelectedAnswers((prev) => ({ ...prev, [qId]: optionLabel }));
  };

  const handleShortAnswerChange = (qId: string, val: string) => {
    setShortAnswers((prev) => ({ ...prev, [qId]: val }));
  };

  const calculateMastery = (): TopicMastery[] => {
    // Question 1: MCQ base cases
    const q1Ans = selectedAnswers["q1"];
    const q1Correct = q1Ans === "B";

    // Question 2: MCQ traversal
    const q2Ans = selectedAnswers["q2"];
    const q2Correct = q2Ans === "B";

    // Question 3: Short answer base cases
    const q3Ans = (shortAnswers["q3"] || "").toLowerCase();
    const q3Correct =
      q3Ans.includes("treenode") ||
      q3Ans.includes("node(val)") ||
      q3Ans.includes("new node") ||
      q3Ans.includes("treenode(val)");

    const baseCaseScore = ((q1Correct ? 1 : 0) + (q3Correct ? 1 : 0)) / 2 * 100;
    const traversalScore = q2Correct ? 100 : 0;

    const topics: TopicMastery[] = [
      {
        id: "recursion_base_cases",
        title: "Recursion Base Cases & Boundary Off-by-One",
        description: "Handling null references, empty structures, and pointer re-assignment in recursive trees.",
        score: baseCaseScore,
        totalQuestions: 2,
        correctQuestions: (q1Correct ? 1 : 0) + (q3Correct ? 1 : 0),
        isWeakPoint: baseCaseScore < 70,
        misconceptionAlert:
          baseCaseScore < 70
            ? "Misconception: Attempting to access node properties before verifying null reference, or missing return values on base condition."
            : undefined,
        recommendedFocus: "Socratic breakdown on base-case guards & pointer linking.",
      },
      {
        id: "tree_traversal",
        title: "Binary Tree Traversal Properties",
        description: "Understanding Inorder vs Preorder vs Postorder recursive flow on binary structures.",
        score: traversalScore,
        totalQuestions: 1,
        correctQuestions: q2Correct ? 1 : 0,
        isWeakPoint: traversalScore < 70,
        misconceptionAlert:
          traversalScore < 70
            ? "Misconception: Confusion between visit order and structural recursion order."
            : undefined,
        recommendedFocus: "Reviewing DFS traversal call stacks.",
      },
    ];

    return topics;
  };

  const handleFinishQuiz = () => {
    setIsSubmitted(true);
    const topics = calculateMastery();
    setTimeout(() => {
      onComplete(topics);
    }, 1200);
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      {/* Header bar */}
      <div className="flex items-center justify-between mb-8 pb-4 border-b border-slate-800">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
            CS Diagnostic Assessment
          </span>
          <h1 className="text-2xl font-bold text-white">
            Topic: Tree Recursion & Boundary Logic
          </h1>
        </div>
        <button
          onClick={onCancel}
          className="text-sm text-slate-400 hover:text-slate-200 transition-colors"
        >
          ✕ Exit Quiz
        </button>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-xs text-slate-400 mb-2">
          <span>Question {currentIndex + 1} of {SAMPLE_QUESTIONS.length}</span>
          <span>{Math.round(((currentIndex + 1) / SAMPLE_QUESTIONS.length) * 100)}% Completed</span>
        </div>
        <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-cyan-500 to-purple-500 transition-all duration-300"
            style={{ width: `${((currentIndex + 1) / SAMPLE_QUESTIONS.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Question Card */}
      <div className="glass-panel p-6 sm:p-8 rounded-2xl mb-6 shadow-xl border border-slate-800">
        <div className="inline-block px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-xs font-medium text-slate-300 mb-4">
          {currentQ.topicTitle}
        </div>

        <h2 className="text-lg sm:text-xl font-semibold text-white mb-4 leading-relaxed">
          {currentQ.question}
        </h2>

        {currentQ.codeSnippet && (
          <pre className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-sm font-mono text-cyan-300 mb-6 overflow-x-auto">
            <code>{currentQ.codeSnippet}</code>
          </pre>
        )}

        {/* MCQ Options */}
        {currentQ.type === "mcq" && currentQ.options && (
          <div className="space-y-3">
            {currentQ.options.map((opt) => {
              const isSelected = selectedAnswers[currentQ.id] === opt.label;
              return (
                <button
                  key={opt.label}
                  onClick={() => handleSelectOption(currentQ.id, opt.label)}
                  className={`w-full text-left p-4 rounded-xl border transition-all duration-200 flex items-start gap-3 cursor-pointer ${
                    isSelected
                      ? "bg-cyan-950/40 border-cyan-400 text-white shadow-md shadow-cyan-950/50"
                      : "bg-slate-900/50 border-slate-800 text-slate-300 hover:bg-slate-850 hover:border-slate-700"
                  }`}
                >
                  <span
                    className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0 mt-0.5 ${
                      isSelected
                        ? "bg-cyan-500 text-black"
                        : "bg-slate-800 text-slate-400 border border-slate-700"
                    }`}
                  >
                    {opt.label}
                  </span>
                  <span className="text-sm sm:text-base leading-relaxed">{opt.text}</span>
                </button>
              );
            })}
          </div>
        )}

        {/* Short Answer Input */}
        {currentQ.type === "short_answer" && (
          <div className="space-y-3">
            <input
              type="text"
              placeholder="e.g., TreeNode(val) or Node(val)"
              value={shortAnswers[currentQ.id] || ""}
              onChange={(e) => handleShortAnswerChange(currentQ.id, e.target.value)}
              className="w-full p-4 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition-all font-mono text-sm"
            />
            <p className="text-xs text-slate-400">
              Tip: Type the code or description of what the base case returns to connect the tree.
            </p>
          </div>
        )}
      </div>

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setCurrentIndex((p) => Math.max(0, p - 1))}
          disabled={currentIndex === 0}
          className="px-5 py-2.5 rounded-xl glass-panel text-slate-300 text-sm font-medium disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800 transition-all"
        >
          ← Previous
        </button>

        {currentIndex < SAMPLE_QUESTIONS.length - 1 ? (
          <button
            onClick={() => setCurrentIndex((p) => Math.min(SAMPLE_QUESTIONS.length - 1, p + 1))}
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-purple-600 text-white text-sm font-semibold hover:opacity-95 shadow-md shadow-cyan-500/20 transition-all"
          >
            Next Question →
          </button>
        ) : (
          <button
            onClick={handleFinishQuiz}
            disabled={isSubmitted}
            className="px-8 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-white text-sm font-bold hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-emerald-500/25 transition-all flex items-center gap-2"
          >
            {isSubmitted ? "Analyzing Diagnostic Results..." : "Submit & See Weak Points 📊"}
          </button>
        )}
      </div>
    </div>
  );
}
