import Link from "next/link";

interface TopicCardProps {
  topic: string;
  description: string;
  difficulty: "high" | "medium" | "low";
}

export default function TopicCard({ topic, description, difficulty }: TopicCardProps) {
  const difficultyColors = {
    high: "bg-red-500",
    medium: "bg-yellow-500",
    low: "bg-green-500",
  };

  const difficultyLabels = {
    high: "Needs practice",
    medium: "Review suggested",
    low: "Minor gap",
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 transition-shadow hover:shadow-md">
      <div className="mb-3 flex items-start justify-between">
        <h3 className="text-lg font-semibold text-gray-900">{topic}</h3>
        <div className="flex items-center gap-2">
          <div className={`h-2 w-2 rounded-full ${difficultyColors[difficulty]}`}></div>
          <span className="text-xs text-gray-500">{difficultyLabels[difficulty]}</span>
        </div>
      </div>
      <p className="mb-4 text-sm text-gray-600">{description}</p>
      <Link 
        href={`/practice/${encodeURIComponent(topic)}`}
        className="inline-flex items-center rounded-lg bg-[#4d9c8f] px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-[#3d8c7f]"
      >
        Practice This →
      </Link>
    </div>
  );
}
