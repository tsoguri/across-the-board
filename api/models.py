from typing import List, Optional

from pydantic import BaseModel

from src.crossword.clue_generator import CrosswordClue
from streamlit_app.constants import CLAUDE_MODELS


class GenerateCluesRequest(BaseModel):
    topic_str: Optional[str] = None
    difficulty: Optional[str] = None
    num_clues: Optional[int] = 30
    model: str = CLAUDE_MODELS[0]


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
    model: str = CLAUDE_MODELS[1]


class ChatResponse(BaseModel):
    response: str
