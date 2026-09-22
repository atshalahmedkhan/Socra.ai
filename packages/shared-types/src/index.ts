// Shared contract types between the Socra frontend (frontend/) and backend
// (backend/). Keep these in sync with the backend Pydantic schemas.

export type AppEnv = "development" | "staging" | "production";

/** Roles a tutoring turn can originate from. */
export type ChatRole = "student" | "assistant" | "system" | "tutor";

export type MisconceptionCategory =
  | "none_detected"
  | "conceptual_confusion"
  | "off_by_one_or_boundary"
  | "logical_inversion"
  | "incomplete_reasoning"
  | "syntax_or_type"
  | "frustration_or_stuck";

export type StudentCognitiveState =
  | "exploring"
  | "making_progress"
  | "struggling"
  | "stuck"
  | "mastered";

export enum HintLevel {
  SOCRATIC_PROBE = 0,
  CONCEPTUAL_POINTER = 1,
  STRATEGIC_HINT = 2,
  DECOMPOSITION_BREAKDOWN = 3,
  WORKED_ANALOGY = 4,
  BOTTOM_OUT_WALKTHROUGH = 5,
}

export type SessionStatus = "active" | "completed" | "abandoned" | "error";

export interface DiagnosticAssessment {
  cognitive_state: StudentCognitiveState;
  misconception: MisconceptionCategory;
  struggle_score: number;
  confidence: number;
  key_signals: string[];
  suggested_hint_level: HintLevel;
  pedagogical_focus: string;
}

export interface SessionMessage {
  id: string;
  session_id: string;
  author_user_id?: string | null;
  role: ChatRole;
  content: string;
  sequence_number: number;
  hint_level?: HintLevel | null;
  created_at: string;
}

export interface TutoringSession {
  id: string;
  classroom_id: string;
  student_id: string;
  learning_objective?: string | null;
  status: SessionStatus;
  hints_used: number;
  attempts: number;
  started_at: string;
  ended_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateTutoringSessionRequest {
  classroom_id: string;
  learning_objective: string;
}

export interface TutoringTurnRequest {
  content: string;
}

export interface TutoringTurnResponse {
  session_id: string;
  student_message: SessionMessage;
  assistant_message: SessionMessage;
  diagnostic: DiagnosticAssessment;
  current_hint_level: HintLevel;
  attempts: number;
  hints_used: number;
  status: SessionStatus;
}

export interface RequestHintResponse {
  session_id: string;
  assistant_message: SessionMessage;
  hint_level: HintLevel;
  hints_used: number;
  status: SessionStatus;
}

export interface SessionSummaryResponse {
  session_id: string;
  classroom_id: string;
  learning_objective?: string | null;
  status: SessionStatus;
  total_turns: number;
  attempts: number;
  hints_used: number;
  max_hint_level_reached: HintLevel;
  identified_misconceptions: MisconceptionCategory[];
  started_at: string;
  ended_at?: string | null;
}

export interface ChatMessage {
  role: ChatRole;
  content: string;
}

/** Request body for a Socratic tutoring turn. */
export interface TutorRequest {
  courseId: string;
  messages: ChatMessage[];
}

/** Response for a Socratic tutoring turn. */
export interface TutorResponse {
  message: ChatMessage;
  modelVersion: string;
}

export interface HealthStatus {
  status: "ok";
  service: string;
  version: string;
}

