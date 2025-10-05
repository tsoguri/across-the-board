from fastapi import HTTPException

from api.constants import CHAT_TYPE, DIFFICULTY_LEVEL, get_cached_claude_models
from api.models import (
    ChatRequest,
    ChatResponse,
    GenerateCluesRequest,
    GenerateCrosswordRequest,
    GenerateCrosswordResponse,
)
from src.chat.chat_service import ChatService
from src.crossword.clue_generator import ClueGenerator
from src.crossword.crossword_generator import CrosswordGenerator

_chat_services = {}
_clue_generators = {}


def get_chat_service(model: str) -> ChatService:
    if model not in _chat_services:
        _chat_services[model] = ChatService(model=model)
    return _chat_services[model]


def get_clue_generator(model: str) -> ClueGenerator:
    if model not in _clue_generators:
        _clue_generators[model] = ClueGenerator(model=model)
    return _clue_generators[model]


async def health_check():
    return {"status": "healthy"}


async def generate_clues(request: GenerateCluesRequest):
    try:
        clue_generator = get_clue_generator(request.model)
        result = clue_generator.generate_clues(
            topic_str=request.topic_str,
            difficulty=request.difficulty,
            num_clues=request.num_clues,
        )
        if not result:
            raise HTTPException(status_code=500, detail="Failed to generate clues")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating clues: {str(e)}")


async def generate_crossword(request: GenerateCrosswordRequest):
    try:
        if not request.clues:
            raise HTTPException(status_code=400, detail="No clues provided")

        crossword_generator = CrosswordGenerator(clues=request.clues)
        grid_df, placements = crossword_generator.generate()
        grid = grid_df.values.tolist()
        placements_dict = []
        for p in placements:
            placements_dict.append(
                {
                    "word": p.word,
                    "row": p.row,
                    "col": p.col,
                    "direction": p.direction,
                    "clue": p.clue,
                }
            )

        return GenerateCrosswordResponse(grid=grid, placements=placements_dict)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating crossword: {str(e)}"
        )


async def generate_chat_response(request: ChatRequest):
    try:
        chat_service = get_chat_service(request.model)

        if request.clue:
            response = chat_service.generate_response(
                user_input=request.user_input,
                clue=request.clue,
                type=request.chat_type,
                historical_messages=request.historical_messages,
            )
        else:
            response = chat_service.generate_research_response(
                user_input=request.user_input,
                historical_messages=request.historical_messages,
            )

        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating chat response: {str(e)}"
        )


async def get_available_models():
    return {"models": get_cached_claude_models()}


async def get_difficulty_levels():
    return {"difficulty_levels": DIFFICULTY_LEVEL}


async def get_chat_types():
    return {"chat_types": CHAT_TYPE}
