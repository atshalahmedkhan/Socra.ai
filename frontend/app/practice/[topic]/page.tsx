"use client";

import { useState, use } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import Navbar from "@/components/Navbar";
import ChatBubble from "@/components/ChatBubble";
import QuizCard from "@/components/QuizCard";

const mockConversations: Record<string, { message: string; isAI: boolean }[]> = {
  "Binary Search Trees": [
    { message: "I'd like to understand BST insertion better.", isAI: false },
    {
      message: "Great! Let's start with the fundamentals. What property must every node in a BST satisfy relative to its children?",
      isAI: true,
    },
    { message: "The left child must be smaller and right child larger?", isAI: false },
    {
      message: "You're on the right track! Can you be more precise about what 'smaller' and 'larger' means in this context? What exactly are we comparing?",
      isAI: true,
    },
  ],
  "Recursion Depth": [
    { message: "I'm having trouble understanding recursion depth.", isAI: false },
    {
      message: "Let's explore this together. When we make a recursive call, what happens to the current function?",
      isAI: true,
    },
    { message: "It waits until the recursive call returns?", isAI: false },
    {
      message: "Exactly! And where does the information about this 'waiting' function get stored? Think about what data structure the system uses.",
      isAI: true,
    },
  ],
};

const mockQuizData: Record<string, { question: string; options: string[] }> = {
  "Binary Search Trees": {
    question: "In a balanced BST with n nodes, what is the worst-case time complexity for searching for a specific value?",
    options: [
      "O(n) — we might need to check every node",
      "O(log n) — we eliminate half the nodes at each level",
      "O(n log n) — we need to sort first then search",
      "O(1) — direct access to any node",
    ],
  },
  "Recursion Depth": {
    question: "What determines the maximum depth of recursion before a stack overflow occurs?",
    options: [
      "The number of parameters in the recursive function",
      "The available stack memory and size of each stack frame",
      "The CPU processing speed",
      "The total amount of RAM in the system",
    ],
  },
};

export default function Practice({ params }: { params: Promise<{ topic: string }> }) {
  const resolvedParams = use(params);
  const searchParams = useSearchParams();
  const mode = searchParams.get("mode") || "chat";
  const topic = decodeURIComponent(resolvedParams.topic);

  const [messages, setMessages] = useState(
    mockConversations[topic] || [
      {
        message: `Let's explore ${topic} together. What specific aspect would you like to understand better?`,
        isAI: true,
      },
    ]
  );
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    const nextMessages = [...messages, { message: userMessage, isAI: false }];
    setMessages(nextMessages);
    setInputValue("");
    setIsLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, messages: nextMessages }),
      });
      const data = await res.json();

      if (!res.ok) {
        setMessages((prev) => [
          ...prev,
          {
            message:
              data.error ||
              "Socra couldn't respond. Check that GEMINI_API_KEY is set in frontend/.env.local and restart the dev server.",
            isAI: true,
          },
        ]);
        return;
      }

      setMessages((prev) => [
        ...prev,
        { message: data.reply as string, isAI: true },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          message: "Network error talking to Socra. Is the Next.js server running?",
          isAI: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-gray-50">
      <Navbar />
      
      <div className="flex flex-1">
        {/* Sidebar */}
        <aside className="w-64 border-r border-gray-200 bg-white p-6">
          <div className="mb-6">
            <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
              Current Topic
            </div>
            <h3 className="text-lg font-semibold text-gray-900">{topic}</h3>
          </div>
          
          <Link
            href="/dashboard"
            className="text-sm text-[#4d9c8f] transition-colors hover:text-[#3d8c7f]"
          >
            ← Switch Topic
          </Link>

          <div className="mt-8">
            <div className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-500">
              Format
            </div>
            <div className="space-y-2">
              <Link
                href={`/practice/${encodeURIComponent(topic)}`}
                className={`block rounded-lg px-3 py-2 text-sm transition-colors ${
                  mode === "chat"
                    ? "bg-[#4d9c8f] text-white"
                    : "text-gray-700 hover:bg-gray-100"
                }`}
              >
                Chat
              </Link>
              <Link
                href={`/practice/${encodeURIComponent(topic)}?mode=quiz`}
                className={`block rounded-lg px-3 py-2 text-sm transition-colors ${
                  mode === "quiz"
                    ? "bg-[#4d9c8f] text-white"
                    : "text-gray-700 hover:bg-gray-100"
                }`}
              >
                Quiz
              </Link>
              <button
                className="w-full rounded-lg px-3 py-2 text-left text-sm text-gray-400 transition-colors hover:bg-gray-100"
                disabled
              >
                Flashcards
              </button>
            </div>
          </div>

          <div className="mt-8 rounded-lg border border-gray-200 bg-gray-50 p-4">
            <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-[#4d9c8f]">
              Reminder
            </div>
            <p className="text-xs leading-relaxed text-gray-600">
              Socra asks questions and checks your reasoning. It won't give you the final answer—that's your job!
            </p>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 bg-white">
          {mode === "quiz" ? (
            <div className="px-8 py-12">
              <QuizCard
                question={mockQuizData[topic]?.question || "What would you like to explore about this topic?"}
                options={mockQuizData[topic]?.options || [
                  "Option A",
                  "Option B",
                  "Option C",
                  "Option D",
                ]}
                questionNumber={1}
                totalQuestions={5}
              />
            </div>
          ) : (
            <div className="flex h-full flex-col">
              {/* Chat Messages */}
              <div className="flex-1 overflow-y-auto bg-gray-50 px-8 py-8">
                <div className="mx-auto max-w-3xl">
                  {messages.map((msg, index) => (
                    <ChatBubble key={index} message={msg.message} isAI={msg.isAI} />
                  ))}
                  {isLoading && (
                    <ChatBubble message="Socra is thinking…" isAI={true} />
                  )}
                </div>
              </div>

              {/* Input Area */}
              <div className="border-t border-gray-200 bg-white px-8 py-6">
                <form onSubmit={handleSendMessage} className="mx-auto max-w-3xl">
                  <div className="flex gap-3">
                    <input
                      type="text"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      placeholder="Type your response or question..."
                      disabled={isLoading}
                      className="flex-1 rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 placeholder-gray-500 outline-none focus:border-[#4d9c8f] focus:ring-2 focus:ring-[#4d9c8f]/20 disabled:opacity-60"
                    />
                    <button
                      type="submit"
                      disabled={isLoading}
                      className="rounded-lg bg-[#4d9c8f] px-6 py-3 font-medium text-white transition-colors hover:bg-[#3d8c7f] disabled:opacity-60"
                    >
                      {isLoading ? "…" : "Send"}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
