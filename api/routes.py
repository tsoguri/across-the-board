from fastapi import APIRouter

from api.controllers import (
    generate_chat_response,
    generate_clues,
    generate_crossword,
    get_available_models,
    get_chat_types,
    get_difficulty_levels,
    health_check,
)
from api.models import (
    ChatResponse,
    GenerateCrosswordResponse,
)
from src.crossword.clue_generator import CrosswordClueResponse

router = APIRouter()

router.get("/health")(health_check)
router.post("/api/clues/generate", response_model=CrosswordClueResponse)(generate_clues)
router.post("/api/crossword/generate", response_model=GenerateCrosswordResponse)(
    generate_crossword
)
router.post("/api/chat/generate", response_model=ChatResponse)(generate_chat_response)
router.get("/api/models")(get_available_models)
router.get("/api/difficulty-levels")(get_difficulty_levels)
router.get("/api/chat-types")(get_chat_types)
