interface ChatBubbleProps {
  message: string;
  isAI: boolean;
}

export default function ChatBubble({ message, isAI }: ChatBubbleProps) {
  return (
    <div className={`flex ${isAI ? "justify-start" : "justify-end"} mb-4`}>
      <div
        className={`max-w-[70%] rounded-2xl px-5 py-3 ${
          isAI
            ? "border border-gray-200 bg-white text-gray-900"
            : "bg-[#4d9c8f] text-white"
        }`}
      >
        {isAI && (
          <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-[#4d9c8f]">
            Socra
          </div>
        )}
        <p className="text-sm leading-relaxed">{message}</p>
      </div>
    </div>
  );
}
