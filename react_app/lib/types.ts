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


export const BLOCK_TOKEN = "⬛⬛";
export const EMPTY_CELL = "";