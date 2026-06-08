"""
Shared AI availability check used by every service module.

Centralises the placeholder-detection logic so that adding `sk-ant-...` (or any
other documentation-style placeholder) to .env never causes a live 500 error.
"""
from app.core.config import settings

# Values that look "set" but are documentation placeholders
_KNOWN_PLACEHOLDERS = {
    "placeholder",
    "sk-ant-placeholder",
    "sk-ant-...",
    "your-anthropic-key",
    "your_anthropic_key",
    "<your-key>",
    "CHANGE_ME",
}


def ai_available() -> bool:
    """
    Return True only when ANTHROPIC_API_KEY looks like a real key.

    Rules:
    - Must be non-empty
    - Must not be one of the known documentation placeholders
    - Must not end with "..." (ellipsis sentinel used in .env examples)
    - Must be at least 20 chars (real Anthropic keys are ~108 chars)
    """
    key = (settings.ANTHROPIC_API_KEY or "").strip()
    if not key:
        return False
    if key in _KNOWN_PLACEHOLDERS:
        return False
    if key.endswith("..."):
        return False
    if len(key) < 20:
        return False
    return True
