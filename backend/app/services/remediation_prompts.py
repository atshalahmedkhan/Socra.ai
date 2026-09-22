from app.schemas.model import ChatMessage
from app.schemas.remediation import DiagnosticAssessment, HintLevel


class RemediationPromptBuilder:
    """Builds structured Socratic prompts for Gemma model inference with embedded scaffolding guidance."""

    SOCRATIC_BASE_SYSTEM_PROMPT = """You are Socra, an intelligent Socratic tutor.
Your core teaching philosophy is active discovery: you guide the student toward understanding
through targeted questions, hints, and feedback instead of directly giving away solutions.

Guidelines:
1. Always maintain a supportive, encouraging, and intellectually rigorous tone.
2. Ask one clear question or provide one focused hint at a time. Do not overwhelm the student with long lectures.
3. If the student has a misconception, do not say 'wrong' directly;
   instead ask a question that exposes the contradiction or tests an edge case.
4. Strictly follow the assigned scaffolding level and constraints.
"""

    def build_messages(
        self,
        learning_objective: str | None,
        target_hint_level: HintLevel,
        diagnostic: DiagnosticAssessment,
        scaffolding_instructions: str,
        dialogue_history: list[ChatMessage],
    ) -> list[ChatMessage]:
        system_sections = [self.SOCRATIC_BASE_SYSTEM_PROMPT]

        if learning_objective:
            system_sections.append(f"CURRENT LEARNING OBJECTIVE:\n{learning_objective}")

        system_sections.append(f"REMEDIATION GUIDANCE:\n{scaffolding_instructions}")

        full_system_content = "\n\n".join(system_sections)

        messages: list[ChatMessage] = [
            ChatMessage(role="system", content=full_system_content)
        ]

        # Append previous messages, normalizing roles if needed
        for msg in dialogue_history:
            role = msg.role
            if role == "student":
                role = "user"
            elif role == "assistant":
                role = "assistant"
            elif role == "system":
                continue  # Base system prompt already added above
            messages.append(ChatMessage(role=role, content=msg.content))

        return messages
