import anthropic

from app.constants import CHAT_TYPE
from src.chat.prompts import HINT_SYSTEM_PROMPT, RESEARCH_SYSTEM_PROMPT
from src.crossword.clue_generator import CrosswordClue

MAX_TOKENS = 8192


class ChatService:
    def __init__(self, model: str):
        self.anthropic_client = anthropic.Anthropic()
        self.model = model

    def generate_research_response(
        self,
        user_input: str,
        historical_messages: list[dict] = [],
    ) -> str:
        messages = historical_messages + [{"role": "user", "content": user_input}]
        response = self.anthropic_client.messages.create(
            model=self.model,
            max_tokens=MAX_TOKENS,
            system=RESEARCH_SYSTEM_PROMPT,
            messages=messages,
        )
        return response.content[0].text

    def generate_response(
        self,
        user_input: str,
        clue: CrosswordClue,
        type: str,
        historical_messages: list[dict] = [],
    ):
        messages = historical_messages + [{"role": "user", "content": user_input}]
        if type == CHAT_TYPE[1]:
            prompt = RESEARCH_SYSTEM_PROMPT
        else:
            prompt = HINT_SYSTEM_PROMPT
        response = self.anthropic_client.messages.create(
            model=self.model,
            max_tokens=MAX_TOKENS,
            system=prompt.format(clue=clue),
            messages=messages,
        )
        return response.content[0].text
