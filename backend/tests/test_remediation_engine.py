
from app.schemas.model import ChatMessage
from app.schemas.remediation import (
    DiagnosticAssessment,
    HintLevel,
    MisconceptionCategory,
    StudentCognitiveState,
)
from app.services.diagnostic_engine import DiagnosticEngine
from app.services.remediation_engine import RemediationEngine
from app.services.remediation_prompts import RemediationPromptBuilder


def test_diagnostic_engine_detects_frustration():
    engine = DiagnosticEngine()
    result = engine.diagnose("I am completely stuck and have no idea what to do")
    assert result.misconception == MisconceptionCategory.FRUSTRATION_OR_STUCK
    assert result.cognitive_state == StudentCognitiveState.STUCK
    assert result.struggle_score >= 0.5


def test_diagnostic_engine_detects_boundary_error():
    engine = DiagnosticEngine()
    result = engine.diagnose("I think we need to loop until n instead of len - 1, but get index out of bounds")
    assert result.misconception == MisconceptionCategory.OFF_BY_ONE_OR_BOUNDARY
    assert "Boundary" in result.key_signals[0] or "edge-case" in result.key_signals[0]


def test_diagnostic_engine_detects_inversion():
    engine = DiagnosticEngine()
    result = engine.diagnose("The output is sorted backwards in descending order instead of ascending")
    assert result.misconception == MisconceptionCategory.LOGICAL_INVERSION


def test_diagnostic_engine_detects_mastery():
    engine = DiagnosticEngine()
    result = engine.diagnose(
        "I get it now! The base case is when node is None so we return 0. Time complexity is O(N)."
    )
    assert result.cognitive_state == StudentCognitiveState.MASTERED
    assert result.struggle_score == 0.0



def test_remediation_engine_hint_progression():
    engine = RemediationEngine()

    # Normal Socratic probe
    diag_normal = DiagnosticAssessment(
        cognitive_state=StudentCognitiveState.MAKING_PROGRESS,
        misconception=MisconceptionCategory.NONE_DETECTED,
    )
    level = engine.determine_next_hint_level(HintLevel.SOCRATIC_PROBE, diag_normal)
    assert level == HintLevel.SOCRATIC_PROBE

    # Student stuck -> escalates
    diag_stuck = DiagnosticAssessment(
        cognitive_state=StudentCognitiveState.STUCK,
        misconception=MisconceptionCategory.FRUSTRATION_OR_STUCK,
        suggested_hint_level=HintLevel.STRATEGIC_HINT,
    )
    level_escalated = engine.determine_next_hint_level(HintLevel.CONCEPTUAL_POINTER, diag_stuck)
    assert level_escalated >= HintLevel.STRATEGIC_HINT

    # Explicit hint requested -> increments by 1
    level_explicit = engine.determine_next_hint_level(
        HintLevel.STRATEGIC_HINT,
        diag_normal,
        explicit_hint_requested=True,
    )
    assert level_explicit == HintLevel.DECOMPOSITION_BREAKDOWN

    # Level capped at 5
    level_max = engine.determine_next_hint_level(
        HintLevel.BOTTOM_OUT_WALKTHROUGH,
        diag_normal,
        explicit_hint_requested=True,
    )
    assert level_max == HintLevel.BOTTOM_OUT_WALKTHROUGH


def test_remediation_prompt_builder_structure():
    builder = RemediationPromptBuilder()
    diag = DiagnosticAssessment(
        cognitive_state=StudentCognitiveState.STRUGGLING,
        misconception=MisconceptionCategory.OFF_BY_ONE_OR_BOUNDARY,
        pedagogical_focus="Focus on the empty array base case.",
    )
    messages = builder.build_messages(
        learning_objective="Binary Search Implementation",
        target_hint_level=HintLevel.STRATEGIC_HINT,
        diagnostic=diag,
        scaffolding_instructions="Suggest checking low <= high vs low < high",
        dialogue_history=[
            ChatMessage(role="student", content="Why does my loop never terminate?"),
        ],
    )

    assert len(messages) >= 2
    assert messages[0].role == "system"
    assert "Binary Search Implementation" in messages[0].content
    assert "Suggest checking low <= high" in messages[0].content
    assert messages[1].role == "user"
    assert "Why does my loop never terminate?" in messages[1].content
