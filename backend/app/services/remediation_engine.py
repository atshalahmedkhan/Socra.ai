from app.schemas.remediation import (
    DiagnosticAssessment,
    HintLevel,
    MisconceptionCategory,
    StudentCognitiveState,
)


class RemediationEngine:
    """Manages adaptive scaffolding, hint level progression, and pedagogical strategy."""

    HINT_LEVEL_DESCRIPTIONS = {
        HintLevel.SOCRATIC_PROBE: (
            "Level 0 (Socratic Probe): Ask a single, thought-provoking guiding question. "
            "Do NOT give away the answer or any strategic hints."
        ),
        HintLevel.CONCEPTUAL_POINTER: (
            "Level 1 (Conceptual Pointer): Remind the student of the key concept, definition, "
            "or invariant they need to consider, without explaining how to solve it."
        ),
        HintLevel.STRATEGIC_HINT: (
            "Level 2 (Strategic Hint): Suggest a strategic approach or heuristic "
            "(e.g. 'try tracing with a small input', 'think about what state needs to be maintained across calls')."
        ),

        HintLevel.DECOMPOSITION_BREAKDOWN: (
            "Level 3 (Decomposition): Break down the problem into 2-3 smaller, bite-sized micro-steps. "
            "Ask the student to solve only the first micro-step."
        ),
        HintLevel.WORKED_ANALOGY: (
            "Level 4 (Worked Analogy / Reflection): Present a simplified analogous example or visual metaphor, "
            "and ask the student to apply the pattern to their original problem."
        ),
        HintLevel.BOTTOM_OUT_WALKTHROUGH: (
            "Level 5 (Bottom-out Walkthrough): Walk through the solution step-by-step with clear explanations, "
            "then ask a verification question to confirm the student understands the underlying reasoning."
        ),
    }

    def determine_next_hint_level(
        self,
        current_hint_level: HintLevel,
        diagnostic: DiagnosticAssessment,
        explicit_hint_requested: bool = False,
    ) -> HintLevel:
        """Determines the appropriate hint level for the current turn."""
        if explicit_hint_requested:
            # Explicit request increments hint level by 1, up to level 5
            return HintLevel(min(5, int(current_hint_level) + 1))

        # Automatic adaptive scaffolding based on cognitive diagnosis
        if diagnostic.cognitive_state == StudentCognitiveState.MASTERED:
            return HintLevel.SOCRATIC_PROBE

        if diagnostic.cognitive_state == StudentCognitiveState.STUCK:
            # If stuck, jump or escalate by at least 1 or 2 levels
            return HintLevel(min(5, max(int(current_hint_level) + 1, int(diagnostic.suggested_hint_level))))

        if diagnostic.cognitive_state == StudentCognitiveState.STRUGGLING:
            # Escalate if struggle is persistent
            return HintLevel(min(5, max(int(current_hint_level), int(diagnostic.suggested_hint_level))))

        # If making progress or exploring, maintain level 0 or current level
        if diagnostic.cognitive_state == StudentCognitiveState.MAKING_PROGRESS:
            return HintLevel.SOCRATIC_PROBE

        return current_hint_level

    def get_scaffolding_instructions(
        self,
        target_hint_level: HintLevel,
        misconception: MisconceptionCategory,
        pedagogical_focus: str,
    ) -> str:
        """Generates clear instructions for the model based on target hint level and misconception."""
        desc = self.HINT_LEVEL_DESCRIPTIONS.get(target_hint_level, "")
        instructions = [
            f"TARGET SCAFFOLDING LEVEL: {desc}",
            f"DIAGNOSED MISCONCEPTION: {misconception.value}",
            f"PEDAGOGICAL INSTRUCTION: {pedagogical_focus}",
        ]

        if target_hint_level < HintLevel.BOTTOM_OUT_WALKTHROUGH:
            instructions.append(
                "CRITICAL CONSTRAINT: Do NOT reveal the full code or the final answer. "
                "Keep your response concise (1-3 sentences or a short question) so the student must think and respond."
            )
        else:
            instructions.append(
                "SCAFFOLDING CONSTRAINT: Clearly explain the steps, but conclude with a comprehension check question."
            )

        return "\n".join(instructions)
