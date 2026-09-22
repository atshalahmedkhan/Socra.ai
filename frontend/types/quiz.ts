export type QuizQuestionType = "mcq" | "short_answer";

export interface QuizQuestion {
  id: string;
  topicId: string;
  topicTitle: string;
  question: string;
  codeSnippet?: string;
  type: QuizQuestionType;
  options?: { label: string; text: string; isCorrect: boolean; feedback: string }[];
  correctKeywords?: string[];
  explanation: string;
}

export interface TopicMastery {
  id: string;
  title: string;
  description: string;
  score: number; // 0 to 100
  totalQuestions: number;
  correctQuestions: number;
  isWeakPoint: boolean;
  misconceptionAlert?: string;
  recommendedFocus: string;
}

export interface RemediationTurn {
  id: string;
  sender: "student" | "socra" | "system";
  content: string;
  hintLevel?: number;
  isQuestion?: boolean;
  questionData?: {
    type: "mcq" | "short_answer";
    options?: { label: string; text: string; isCorrect: boolean }[];
    answered?: boolean;
    selectedLabel?: string;
    isCorrect?: boolean;
  };
  timestamp: string;
}

export type AppStage = "landing" | "quiz" | "practice" | "remediation";
