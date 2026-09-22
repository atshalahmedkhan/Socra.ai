import re

from app.schemas.remediation import (
    DiagnosticAssessment,
    HintLevel,
    MisconceptionCategory,
    StudentCognitiveState,
)

FRUSTRATION_PATTERNS = [
    r"\bi('?m| am)?\s*(confused|lost|stuck|clueless)\b",
    r"\bi\s*(don'?t|do not)\s*(know|get it|understand|have any idea)\b",
    r"\b(no idea|give up|can'?t figure|help me|idk)\b",
    r"^\s*(\?+|help|hint|what\??|why\??)\s*$",
]

BOUNDARY_PATTERNS = [
    r"\b(off[- ]by[- ]one|index out of bounds|<=?\s*vs\s*<|boundary|out of range|indexerror|base case)\b",
    r"\b(array index|list index|n\s*\+\s*1|n\s*-\s*1|len\s*-\s*1|len\s*vs\s*len\s*-\s*1)\b",
    r"\b(empty (list|array|tree|string)|null pointer|none check)\b",
]

INVERSION_PATTERNS = [
    r"\b(reversed|backwards|inverted|flipped|wrong order|ascending vs descending)\b",
    r"\b(greater instead of less|less instead of greater|false when true)\b",
    r"\b(preorder vs postorder|inorder vs preorder)\b",
]

SYNTAX_TYPE_PATTERNS = [
    r"\b(typeerror|syntaxerror|nameerror|attributeerror|cannot convert|expected int)\b",
    r"\b(str vs int|undefined|null is not an object|none type|cannot call method)\b",
]

PROGRESS_PATTERNS = [
    r"\b(because|so if we|therefore|my thinking is|we should first|then we check|base case is)\b",
    r"\b(first step|i think|could it be|is it because|pattern)\b",
]

MASTERY_PATTERNS = [
    r"\b(i get it now|that makes sense|solved|got it|makes total sense|now i understand)\b",
    r"\b(correct base case|the time complexity is o\(.+\)|we should return)\b",
]


class DiagnosticEngine:
    """Evaluates student responses and dialog history to diagnose misconceptions and student struggle."""

    def diagnose(
        self,
        student_text: str,
        learning_objective: str | None = None,
        attempts: int = 0,
        current_hint_level: HintLevel = HintLevel.SOCRATIC_PROBE,
        consecutive_errors: int = 0,
    ) -> DiagnosticAssessment:
        clean_text = student_text.strip().lower()
        signals: list[str] = []

        # 1. Frustration / Stuck detection
        is_frustrated = any(re.search(p, clean_text) for p in FRUSTRATION_PATTERNS)
        if is_frustrated:
            signals.append("Expressed confusion or uncertainty")

        # 2. Boundary / Off-by-one detection
        has_boundary_issue = any(re.search(p, clean_text) for p in BOUNDARY_PATTERNS)
        if has_boundary_issue:
            signals.append("Boundary or edge-case reasoning detected")

        # 3. Logical Inversion detection
        has_inversion_issue = any(re.search(p, clean_text) for p in INVERSION_PATTERNS)
        if has_inversion_issue:
            signals.append("Condition or order inversion detected")

        # 4. Syntax / Type error detection
        has_syntax_issue = any(re.search(p, clean_text) for p in SYNTAX_TYPE_PATTERNS)
        if has_syntax_issue:
            signals.append("Type or syntax hurdle detected")

        # 5. Length & Substance check
        is_short = len(clean_text.split()) < 4
        if is_short and not is_frustrated:
            signals.append("Brief response with minimal reasoning")

        # 6. Progress / Reasoning signals
        shows_reasoning = any(re.search(p, clean_text) for p in PROGRESS_PATTERNS)
        shows_mastery = any(re.search(p, clean_text) for p in MASTERY_PATTERNS)

        # Categorize Misconception
        if is_frustrated:
            misconception = MisconceptionCategory.FRUSTRATION_OR_STUCK
        elif has_boundary_issue:
            misconception = MisconceptionCategory.OFF_BY_ONE_OR_BOUNDARY
        elif has_inversion_issue:
            misconception = MisconceptionCategory.LOGICAL_INVERSION
        elif has_syntax_issue:
            misconception = MisconceptionCategory.SYNTAX_OR_TYPE
        elif consecutive_errors >= 2:
            misconception = MisconceptionCategory.CONCEPTUAL_CONFUSION
        elif is_short:
            misconception = MisconceptionCategory.INCOMPLETE_REASONING
        else:
            misconception = MisconceptionCategory.NONE_DETECTED

        # Calculate struggle score (0.0 to 1.0)
        struggle = 0.0
        if is_frustrated:
            if re.search(r"\b(stuck|give up|no idea|clueless|cannot figure|can'?t figure)\b", clean_text):
                struggle += 0.75
            else:
                struggle += 0.5
        if is_short:
            struggle += 0.2
        if consecutive_errors > 0:
            struggle += min(0.4, consecutive_errors * 0.15)
        if attempts >= 3:
            struggle += 0.2
        if shows_reasoning:
            struggle = max(0.0, struggle - 0.25)
        if shows_mastery:
            struggle = 0.0


        struggle_score = round(min(1.0, max(0.0, struggle)), 2)

        # Determine Cognitive State
        if shows_mastery and struggle_score < 0.2:
            cognitive_state = StudentCognitiveState.MASTERED
        elif struggle_score >= 0.7 or (is_frustrated and consecutive_errors >= 2):
            cognitive_state = StudentCognitiveState.STUCK
        elif struggle_score >= 0.4:
            cognitive_state = StudentCognitiveState.STRUGGLING
        elif shows_reasoning:
            cognitive_state = StudentCognitiveState.MAKING_PROGRESS
        else:
            cognitive_state = StudentCognitiveState.EXPLORING

        # Suggest Hint Level
        suggested_hint_level = current_hint_level
        if cognitive_state == StudentCognitiveState.STUCK:
            suggested_hint_level = HintLevel(min(5, int(current_hint_level) + 2))
        elif cognitive_state == StudentCognitiveState.STRUGGLING:
            suggested_hint_level = HintLevel(min(5, int(current_hint_level) + 1))
        elif cognitive_state == StudentCognitiveState.MASTERED:
            suggested_hint_level = HintLevel.SOCRATIC_PROBE

        # Pedagogical focus description
        pedagogical_focus = self._determine_focus(misconception, cognitive_state, learning_objective)

        return DiagnosticAssessment(
            cognitive_state=cognitive_state,
            misconception=misconception,
            struggle_score=struggle_score,
            confidence=0.85 if misconception != MisconceptionCategory.NONE_DETECTED else 0.7,
            key_signals=signals,
            suggested_hint_level=suggested_hint_level,
            pedagogical_focus=pedagogical_focus,
        )

    def _determine_focus(
        self,
        misconception: MisconceptionCategory,
        state: StudentCognitiveState,
        learning_objective: str | None,
    ) -> str:
        objective_prefix = f"Regarding '{learning_objective}': " if learning_objective else ""
        if misconception == MisconceptionCategory.FRUSTRATION_OR_STUCK:
            return (
                f"{objective_prefix}Acknowledge difficulty, provide encouragement, "
                "and break the immediate question down into a simpler micro-step."
            )
        if misconception == MisconceptionCategory.OFF_BY_ONE_OR_BOUNDARY:
            return (
                f"{objective_prefix}Guide student to trace edge values "
                "(e.g. empty collection, 0, or length-1) step-by-step."
            )
        if misconception == MisconceptionCategory.LOGICAL_INVERSION:
            return (
                f"{objective_prefix}Prompt student to verify condition direction "
                "by dry-running a single concrete example."
            )
        if misconception == MisconceptionCategory.SYNTAX_OR_TYPE:
            return (
                f"{objective_prefix}Clarify the expected data type or interface "
                "before reasoning about the algorithm."
            )
        if misconception == MisconceptionCategory.CONCEPTUAL_CONFUSION:
            return (
                f"{objective_prefix}Provide a conceptual pointer or analogy "
                "to anchor the underlying principle before details."
            )
        if misconception == MisconceptionCategory.INCOMPLETE_REASONING:
            return (
                f"{objective_prefix}Prompt the student to explain their step-by-step thinking "
                "or fill in the missing rationale."
            )
        if state == StudentCognitiveState.MASTERED:
            return (
                f"{objective_prefix}Affirm correct understanding and challenge student "
                "to consider complexity or generalizations."
            )
        return f"{objective_prefix}Ask a focused guiding question to encourage active reasoning."

