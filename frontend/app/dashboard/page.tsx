"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Navbar from "@/components/Navbar";
import TopicCard from "@/components/TopicCard";

const mockWeakPoints = [
  {
    topic: "Binary Search Trees",
    description: "Struggled with balancing operations and identifying when rotation is needed",
    difficulty: "high" as const,
  },
  {
    topic: "Recursion Depth",
    description: "Had difficulty tracing recursive calls and predicting stack depth",
    difficulty: "medium" as const,
  },
  {
    topic: "Big-O Analysis",
    description: "Minor confusion on nested loop time complexity calculations",
    difficulty: "low" as const,
  },
];

export default function Dashboard() {
  const [customTopic, setCustomTopic] = useState("");
  const router = useRouter();

  const handleCustomTopicSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (customTopic.trim()) {
      router.push(`/practice/${encodeURIComponent(customTopic.trim())}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="mx-auto max-w-6xl px-6 py-12">
        <div className="mb-8">
          <h1 className="mb-2 text-3xl font-bold text-gray-900">
            Good afternoon, Tejas
          </h1>
          <p className="text-gray-600">CSE 250: Data Structures</p>
        </div>

        <section className="mb-12">
          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              Your Weak Points from Today's Session
            </h2>
            <span className="text-sm text-gray-600">
              {mockWeakPoints.length} areas identified
            </span>
          </div>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {mockWeakPoints.map((point) => (
              <TopicCard
                key={point.topic}
                topic={point.topic}
                description={point.description}
                difficulty={point.difficulty}
              />
            ))}
          </div>
        </section>

        <section className="rounded-lg border border-gray-200 bg-white p-8">
          <h2 className="mb-4 text-xl font-semibold text-gray-900">
            Start a Custom Topic
          </h2>
          <p className="mb-6 text-sm text-gray-600">
            Want to practice something specific? Type any topic and Socra will guide you through it.
          </p>
          <form onSubmit={handleCustomTopicSubmit} className="flex gap-3">
            <input
              type="text"
              value={customTopic}
              onChange={(e) => setCustomTopic(e.target.value)}
              placeholder="e.g., Hash tables, Dynamic programming, Graph traversal..."
              className="flex-1 rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 placeholder-gray-500 outline-none focus:border-[#4d9c8f] focus:ring-2 focus:ring-[#4d9c8f]/20"
            />
            <button
              type="submit"
              className="rounded-lg bg-[#4d9c8f] px-6 py-3 font-medium text-white transition-colors hover:bg-[#3d8c7f]"
            >
              Start Practice →
            </button>
          </form>
        </section>

        <section className="mt-12 rounded-lg border border-gray-200 bg-white p-6">
          <div className="mb-3 text-xs font-semibold uppercase tracking-wide text-[#4d9c8f]">
            Socra Learning Philosophy
          </div>
          <p className="text-sm leading-relaxed text-gray-700">
            Socra never supplies the final answer. It asks focused questions, checks your reasoning, 
            and gives progressive support only when needed. This practice space is self-directed 
            and low-stakes—take your time and think through each step.
          </p>
        </section>
      </main>
    </div>
  );
}
