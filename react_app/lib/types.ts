export interface CrosswordClue {
  clue: string;
  answer: string;
}

export interface CrosswordClueResponse {
  clues: CrosswordClue[];
}

export interface Placement {
  word: string;
  row: number;
  col: number;
  direction: "across" | "down";
  clue: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface GenerateCluesRequest {
  topic_str?: string;
  difficulty?: string;
  num_clues?: number;
  model: string;
}

export interface GenerateCrosswordRequest {
  clues: CrosswordClue[];
}

export interface GenerateChatRequest {
  user_input: string;
  clue?: CrosswordClue;
  chat_type: string;
  historical_messages: ChatMessage[];
  model: string;
}

export type GridCell = string | null;
export type CrosswordGrid = GridCell[][];

export const CLAUDE_MODELS = [
  "claude-3-5-haiku-20241022",
  "claude-sonnet-4-20250514",
  "claude-opus-4-20250514",
  "claude-opus-4-1-20250805",
];

export const DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"];
export const CHAT_TYPES = ["Get a Hint", "Deep Dive into the Answer"];
export const BLOCK_TOKEN = "⬛⬛";
export const EMPTY_CELL = "";