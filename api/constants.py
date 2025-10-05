from typing import List

import anthropic


def get_claude_models() -> List[str]:
    """Fetch available Claude models from Anthropic API."""
    try:
        client = anthropic.Anthropic()
        models = client.models.list().data
        model_ids = [model.id for model in models]

        # Sort models to prioritize Haiku (cheaper) as default
        haiku_models = [m for m in model_ids if "haiku" in m.lower()]
        other_models = [m for m in model_ids if "haiku" not in m.lower()]

        # Return Haiku models first for cheaper defaults
        return haiku_models + other_models
    except Exception:
        # Fallback to hardcoded models if API call fails
        return [
            "claude-3-5-haiku-20241022",
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
            "claude-opus-4-1-20250805",
        ]


# Cache models to avoid repeated API calls
_CLAUDE_MODELS = None


def get_cached_claude_models() -> List[str]:
    """Get cached Claude models or fetch them if not cached."""
    global _CLAUDE_MODELS
    if _CLAUDE_MODELS is None:
        _CLAUDE_MODELS = get_claude_models()
    return _CLAUDE_MODELS


# Static constants
DIFFICULTY_LEVEL = ["Easy", "Medium", "Hard"]
CHAT_TYPE = ["Get a Hint", "Deep Dive into the Answer"]
