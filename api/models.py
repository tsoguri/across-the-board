from typing import List, Optional

from pydantic import BaseModel

from api.constants import get_cached_claude_models
from src.crossword.clue_generator import CrosswordClue


class GenerateCluesRequest(BaseModel):
    topic_str: Optional[str] = None
    difficulty: Optional[str] = None
    num_clues: Optional[int] = 30
    model: str = get_cached_claude_models()[0]


class GenerateCrosswordRequest(BaseModel):
    clues: List[CrosswordClue]


class GenerateCrosswordResponse(BaseModel):
    grid: List[List[str]]
    placements: List[dict]  # Will contain Placement data as dicts


class ChatRequest(BaseModel):
    user_input: str
    clue: Optional[CrosswordClue] = None
    chat_type: str
    historical_messages: List[dict] = []
    model: str = get_cached_claude_models()[0]


class ChatResponse(BaseModel):
    response: str
