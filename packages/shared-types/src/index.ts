// Shared contract types between the Socra frontend (frontend/) and backend
// (backend/). Keep these in sync with the backend Pydantic schemas.

export type AppEnv = "development" | "staging" | "production";

/** Roles a tutoring turn can originate from. */
export type ChatRole = "student" | "tutor" | "system";

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
