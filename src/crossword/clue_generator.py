import logging
from typing import Optional

import anthropic
from pydantic import BaseModel, Field

from src.crossword.prompts import (
    CLUE_GENERATION_PROMPT,
    CLUE_GENERATION_SYSTEM_PROMPT,
    CLUE_GENERATION_TOPIC_PROMPT,
    DIFFICULTY_DESCRIPTION,
)
from src.weaviate_client import WeaviateClient

MAX_TOKENS = 8192


class CrosswordClue(BaseModel):
    """Model representing a crossword clue and its answer."""

    clue: str = Field(..., description="The crossword clue text")
    answer: str = Field(..., description="The answer to the crossword clue")


class CrosswordClueResponse(BaseModel):
    """Model representing the response from the clue generation API."""

    clues: list[CrosswordClue] = Field(
        ..., description="List of generated crossword clues"
    )


class ClueGenerator:
    def __init__(self, model: str):
        self.anthropic_client = anthropic.Anthropic()
        self.model = model

    def generate_clues(
        self,
        topic_str: Optional[str] = None,
        difficulty: Optional[str] = None,
        num_clues: Optional[int] = 30,
    ) -> CrosswordClueResponse:
        """
        Generate clues based on the provided topic, difficulty, and size.

        Args:
            topic_str (str): Comma-separated topics for the crossword.
            difficulty (str): Difficulty level of the crossword.
            size (int): Size of the crossword grid.

        Returns:
            None
        """
        logging.info(
            f"Generating clues for topics: {topic_str}, difficulty: {difficulty}, num_clues: {num_clues}"
        )
        topic_prompt_str = ""
        if topic_str:
            topics = [topic.strip() for topic in topic_str.split(",")]
            logging.info(f"Parsed topics: {topics}")
            clue_examples = self._get_clue_examples(topic_str)
            topic_prompt_str = CLUE_GENERATION_TOPIC_PROMPT.format(
                topic_str=topic_str,
                clue_examples=clue_examples,
            )
        prompt = CLUE_GENERATION_PROMPT.format(
            topics=topic_prompt_str,
            difficulty=DIFFICULTY_DESCRIPTION.get(difficulty),
            num_clues=num_clues,
        )
        clues = self._get_clues(prompt)
        return clues

    def _get_clues(self, prompt: str) -> CrosswordClueResponse:
        """
        Generate clues with Claude based on the provided prompt.

        Args:
            prompt (str): The prompt to generate clues.

        Returns:
            list[CrosswordClue]: List of generated clues.
        """
        response = self.anthropic_client.messages.create(
            model=self.model,
            max_tokens=MAX_TOKENS,
            tools=[
                {
                    "name": "generate_crossword_clues",
                    "description": CrosswordClueResponse.__doc__,
                    "input_schema": CrosswordClueResponse.model_json_schema(),
                }
            ],
            tool_choice={"type": "tool", "name": "generate_crossword_clues"},
            system=CLUE_GENERATION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        reasoning_text = ""
        tool_response = None
        for content_block in response.content:
            if (
                content_block.type == "thinking"
                or content_block.type == "redacted_thinking"
            ):
                reasoning_text += content_block.content
            if content_block.type == "text":
                reasoning_text += content_block.text
            if (
                content_block.type == "tool_use"
                and content_block.name == "generate_crossword_clues"
            ):
                tool_input = content_block.input
                try:
                    tool_response = CrosswordClueResponse(**tool_input)
                    result = []
                    answer_set = []
                    for clue in tool_response.clues:
                        if clue.answer.isalpha() and clue.answer not in answer_set:
                            result.append(
                                CrosswordClue(
                                    clue=clue.clue.strip(),
                                    answer=clue.answer.upper().strip(),
                                )
                            )
                            answer_set.append(clue.answer)
                    return CrosswordClueResponse(clues=result)
                except Exception as e:
                    print(f"Error parsing tool response: {e}")
        return tool_response

    def _get_clue_examples(self, topic_str: str):
        """
        Fetch clue examples from the Weaviate collection based on the provided topic string.

        Args:
            topic_str (str): Comma-separated topics for the crossword.

        Returns:
            list: List of clue examples.
        """
        weaviate_client = WeaviateClient()
        results = weaviate_client.query_collection(topic_str, limit=5)
        clue_examples = []
        for result in results:
            if result.properties.get("clue") and result.properties.get("answer"):
                clue_examples.append(
                    {
                        "clue": result.properties.get("clue"),
                        "answer": result.properties.get("answer"),
                    }
                )
        return clue_examples
