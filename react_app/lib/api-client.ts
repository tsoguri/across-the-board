import axios, { AxiosResponse } from 'axios';
import {
  CrosswordClueResponse,
  GenerateCluesRequest,
  GenerateCrosswordRequest,
  GenerateChatRequest,
  Placement,
  CrosswordGrid,
} from './types';

export class APIClient {
  private client;

  constructor(baseUrl = "http://localhost:8000") {
    this.client = axios.create({
      baseURL: baseUrl,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.client.get('/health');
      return response.status === 200;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }

  async generateClues({
    topic_str,
    difficulty,
    num_clues = 30,
    model = "claude-3-5-haiku-20241022"
  }: GenerateCluesRequest): Promise<CrosswordClueResponse | null> {
    try {
      const response: AxiosResponse<CrosswordClueResponse> = await this.client.post(
        '/api/clues/generate',
        {
          topic_str,
          difficulty,
          num_clues,
          model,
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error generating clues:', error);
      return null;
    }
  }

  async generateCrossword({ clues }: GenerateCrosswordRequest): Promise<{
    grid: CrosswordGrid;
    placements: Placement[];
  } | null> {
    try {
      const cluesData = clues.map(c => ({ clue: c.clue, answer: c.answer }));
      
      const response = await this.client.post('/api/crossword/generate', {
        clues: cluesData
      });

      return {
        grid: response.data.grid,
        placements: response.data.placements.map((p: any) => ({
          word: p.word,
          row: p.row,
          col: p.col,
          direction: p.direction,
          clue: p.clue,
        }))
      };
    } catch (error) {
      console.error('Error generating crossword:', error);
      return null;
    }
  }

  async generateChatResponse({
    user_input,
    clue,
    chat_type = "Get a Hint",
    historical_messages = [],
    model = "claude-3-5-sonnet-20241022"
  }: GenerateChatRequest): Promise<string | null> {
    try {
      const response = await this.client.post('/api/chat/generate', {
        user_input,
        clue: clue ? { clue: clue.clue, answer: clue.answer } : null,
        chat_type,
        historical_messages,
        model,
      });
      
      return response.data.response;
    } catch (error) {
      console.error('Error generating chat response:', error);
      return null;
    }
  }

  async getAvailableModels(): Promise<string[]> {
    try {
      const response = await this.client.get('/api/models');
      return response.data.models;
    } catch (error) {
      console.error('Error getting available models:', error);
      return [];
    }
  }

  async getDifficultyLevels(): Promise<string[]> {
    try {
      const response = await this.client.get('/api/difficulty-levels');
      return response.data.difficulty_levels;
    } catch (error) {
      console.error('Error getting difficulty levels:', error);
      return ['Easy', 'Medium', 'Hard']; // Fallback
    }
  }

  async getChatTypes(): Promise<string[]> {
    try {
      const response = await this.client.get('/api/chat-types');
      return response.data.chat_types;
    } catch (error) {
      console.error('Error getting chat types:', error);
      return ['Get a Hint', 'Deep Dive into the Answer']; // Fallback
    }
  }
}