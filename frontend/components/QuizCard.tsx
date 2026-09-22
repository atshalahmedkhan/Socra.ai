"use client";

import { useState } from "react";

interface QuizCardProps {
  question: string;
  options: string[];
  questionNumber: number;
  totalQuestions: number;
}

export default function QuizCard({
  question,
  options,
  questionNumber,
  totalQuestions,
}: QuizCardProps) {
  const [selectedOption, setSelectedOption] = useState<number | null>(null);

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-6">
        <div className="mb-2 text-sm font-medium text-gray-600">
          Question {questionNumber} of {totalQuestions}
        </div>
        <div className="h-2 w-full rounded-full bg-gray-200">
          <div
            className="h-2 rounded-full bg-[#4d9c8f] transition-all"
            style={{ width: `${(questionNumber / totalQuestions) * 100}%` }}
          ></div>
        </div>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-8">
        <h2 className="mb-6 text-xl font-semibold text-gray-900">{question}</h2>
        <div className="space-y-3">
          {options.map((option, index) => (
            <button
              key={index}
              onClick={() => setSelectedOption(index)}
              className={`w-full rounded-lg border-2 p-4 text-left transition-all ${
                selectedOption === index
                  ? "border-[#4d9c8f] bg-[#4d9c8f]/5"
                  : "border-gray-200 hover:border-gray-300"
              }`}
            >
              <span className="font-medium text-gray-900">{option}</span>
            </button>
          ))}
        </div>
        <button className="mt-6 w-full rounded-lg bg-[#4d9c8f] px-6 py-3 font-medium text-white transition-colors hover:bg-[#3d8c7f] disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={selectedOption === null}
        >
          Check Answer
        </button>
      </div>
    </div>
  );
}
