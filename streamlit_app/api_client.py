import logging
from typing import Dict, List, Optional

import httpx
import pandas as pd

from src.crossword.clue_generator import CrosswordClue, CrosswordClueResponse
from src.crossword.crossword_generator import Placement


class APIClient:
    """Client for communicating with the FastAPI backend."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)

    def __del__(self):
        """Clean up the HTTP client on destruction."""
        try:
            self.client.close()
        except Exception:
            pass

    def health_check(self) -> bool:
        """Check if the API server is running."""
        try:
            response = self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception:
            return False

    def generate_clues(
        self,
        topic_str: Optional[str] = None,
        difficulty: Optional[str] = None,
        num_clues: Optional[int] = 30,
        model: str = "claude-3-5-haiku-20241022",
    ) -> Optional[CrosswordClueResponse]:
        """Generate crossword clues via API."""
        try:
            payload = {
                "topic_str": topic_str,
                "difficulty": difficulty,
                "num_clues": num_clues,
                "model": model,
            }

            response = self.client.post(
                f"{self.base_url}/api/clues/generate", json=payload
            )
            response.raise_for_status()

            data = response.json()
            return CrosswordClueResponse(**data)

        except Exception as e:
            logging.error(f"Error generating clues: {e}")
            return None

    def generate_crossword(
        self, clues: List[CrosswordClue]
    ) -> Optional[tuple[pd.DataFrame, List[Placement]]]:
        """Generate crossword grid and placements via API."""
        try:
            # Convert CrosswordClue objects to dicts for JSON serialization
            clues_data = [{"clue": c.clue, "answer": c.answer} for c in clues]

            payload = {"clues": clues_data}

            response = self.client.post(
                f"{self.base_url}/api/crossword/generate", json=payload
            )
            response.raise_for_status()

            data = response.json()

            # Convert response back to expected formats
            grid_df = pd.DataFrame(data["grid"])

            placements = []
            for p_data in data["placements"]:
                placement = Placement(
                    word=p_data["word"],
                    row=p_data["row"],
                    col=p_data["col"],
                    direction=p_data["direction"],
                    clue=p_data["clue"],
                )
                placements.append(placement)

            return grid_df, placements

        except Exception as e:
            logging.error(f"Error generating crossword: {e}")
            return None

    def generate_chat_response(
        self,
        user_input: str,
        clue: Optional[CrosswordClue] = None,
        chat_type: str = "Get a Hint",
        historical_messages: List[Dict[str, str]] = None,
        model: str = "claude-3-5-sonnet-20241022",
    ) -> Optional[str]:
        """Generate chat response via API."""
        try:
            if historical_messages is None:
                historical_messages = []

            payload = {
                "user_input": user_input,
                "clue": {"clue": clue.clue, "answer": clue.answer} if clue else None,
                "chat_type": chat_type,
                "historical_messages": historical_messages,
                "model": model,
            }

            response = self.client.post(
                f"{self.base_url}/api/chat/generate", json=payload
            )
            response.raise_for_status()

            data = response.json()
            return data["response"]

        except Exception as e:
            logging.error(f"Error generating chat response: {e}")
            return None

    def get_available_models(self) -> List[str]:
        """Get list of available models from the API."""
        try:
            response = self.client.get(f"{self.base_url}/api/models")
            response.raise_for_status()

            data = response.json()
            return data["models"]

        except Exception as e:
            logging.error(f"Error getting available models: {e}")
            return []

    def get_difficulty_levels(self) -> List[str]:
        """Get list of difficulty levels from the API."""
        try:
            response = self.client.get(f"{self.base_url}/api/difficulty-levels")
            response.raise_for_status()

            data = response.json()
            return data["difficulty_levels"]

        except Exception as e:
            logging.error(f"Error getting difficulty levels: {e}")
            return ["Easy", "Medium", "Hard"]  # Fallback

    def get_chat_types(self) -> List[str]:
        """Get list of chat types from the API."""
        try:
            response = self.client.get(f"{self.base_url}/api/chat-types")
            response.raise_for_status()

            data = response.json()
            return data["chat_types"]

        except Exception as e:
            logging.error(f"Error getting chat types: {e}")
            return ["Get a Hint", "Deep Dive into the Answer"]  # Fallback
