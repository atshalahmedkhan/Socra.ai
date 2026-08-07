import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyResult:
    accepted: bool
    rejection_code: str | None = None
    reason: str | None = None


def validate_response(content: str, student_text: str, max_chars: int = 6000) -> PolicyResult:
    if not content.strip():
        return PolicyResult(False, "EMPTY", "Response is empty")
    if len(content) > max_chars:
        return PolicyResult(False, "TOO_LONG", "Response exceeds policy length")
    asks_complete = bool(
        re.search(r"\b(complete|full|entire)\b.*\b(code|solution|answer)\b", student_text, re.IGNORECASE)
    )
    code_lines = sum(
        1 for line in content.splitlines() if line.strip().startswith(("def ", "class ", "function ", "```"))
    )
    if asks_complete and (code_lines >= 2 or "```" in content):
        return PolicyResult(False, "FULL_SOLUTION", "Response appears to provide a complete solution")
    return PolicyResult(True)
