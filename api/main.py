from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.chat.chat_service import ChatService
from src.crossword.clue_generator import (
    ClueGenerator,
    CrosswordClue,
    CrosswordClueResponse,
)
from src.crossword.crossword_generator import CrosswordGenerator
from streamlit_app.constants import CLAUDE_MODELS

app = FastAPI(
    title="Across the Board API",
    description="API for crossword generation and chat services",
    version="1.0.0",
)

# Add CORS middleware to allow Streamlit to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],  # Streamlit default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
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


# Global service instances (in production, consider dependency injection)
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


# Endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/clues/generate", response_model=CrosswordClueResponse)
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


@app.post("/api/crossword/generate", response_model=GenerateCrosswordResponse)
async def generate_crossword(request: GenerateCrosswordRequest):
    try:
        if not request.clues:
            raise HTTPException(status_code=400, detail="No clues provided")

        crossword_generator = CrosswordGenerator(clues=request.clues)
        grid_df, placements = crossword_generator.generate()

        # Convert DataFrame to list of lists
        grid = grid_df.values.tolist()

        # Convert Placement objects to dicts
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


@app.post("/api/chat/generate", response_model=ChatResponse)
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


@app.get("/api/models")
async def get_available_models():
    return {"models": CLAUDE_MODELS}


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
