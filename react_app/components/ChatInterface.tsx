'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
  Typography,
  Box,
  TextField,
  Button,
  CircularProgress,
} from '@mui/material';
import { ChatMessage, CrosswordClue, CHAT_TYPES } from '../lib/types';

interface ChatInterfaceProps {
  selectedClue: CrosswordClue | null;
  onSendMessage: (message: string, chatType: string) => Promise<string | null>;
  isLoading: boolean;
  chatType?: string;
}

export default function ChatInterface({ selectedClue, onSendMessage, isLoading, chatType = 'Get a Hint' }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Send opening message when clue or chat type changes
  useEffect(() => {
    if (selectedClue && chatType) {
      setMessages([]);
      handleOpeningMessage();
    }
  }, [selectedClue, chatType]);

  const handleOpeningMessage = async () => {
    if (!selectedClue) return;

    const opener = chatType === CHAT_TYPES[0]
      ? "Give me an initial direction how to think about the clue. Ask me what I know / think I know about this clue already."
      : "Provide me a brief intellectual, academic overview of this topic. Ask me if there's anything specific I want to know about this topic.";

    const response = await onSendMessage(opener, chatType);
    if (response) {
      setMessages([{ role: 'assistant', content: response }]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || !selectedClue || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    
    // Add user message to chat
    const newMessages = [...messages, { role: 'user' as const, content: userMessage }];
    setMessages(newMessages);

    // Get AI response
    const response = await onSendMessage(userMessage, chatType);
    if (response) {
      setMessages(prev => [...prev, { role: 'assistant', content: response }]);
    } else {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Failed to generate response. Please try again.' }]);
    }
  };


  if (!selectedClue) {
    return (
      <Box sx={{ p: 3, textAlign: 'center', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          Select a clue to start a conversation.
        </Typography>
      </Box>
    );
  }

  const label = chatType === "Get a Hint" ? "some help for" : "to learn more about";

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 1 }}>
          Selected clue you would like {label}:
        </Typography>
        <Typography variant="body1" sx={{ fontWeight: 600 }}>
          {selectedClue.clue}
        </Typography>
      </Box>

      {/* Messages Container */}
      <Box 
        sx={{ 
          flex: 1,
          overflowY: 'auto', 
          p: 3, 
          bgcolor: 'grey.50',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Box sx={{ flex: 1 }}>
          {messages.map((message, index) => (
            <Box
              key={index}
              sx={{
                mb: 2,
                textAlign: message.role === 'user' ? 'right' : 'left'
              }}
            >
              <Box
                sx={{
                  display: 'inline-block',
                  p: 2,
                  borderRadius: 2,
                  maxWidth: '85%',
                  bgcolor: message.role === 'user' ? 'primary.main' : 'background.paper',
                  color: message.role === 'user' ? 'primary.contrastText' : 'text.primary',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                }}
              >
                <Typography variant="body2">
                  {message.content}
                </Typography>
              </Box>
            </Box>
          ))}
          {isLoading && (
            <Box textAlign="left" mb={2}>
              <Box
                sx={{
                  display: 'inline-block',
                  p: 2,
                  borderRadius: 2,
                  bgcolor: 'grey.200',
                  color: 'text.secondary',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={16} />
                  <Typography variant="body2">Generating response...</Typography>
                </Box>
              </Box>
            </Box>
          )}
        </Box>
        <div ref={messagesEndRef} />
      </Box>

      {/* Chat Input */}
      <Box sx={{ p: 3, borderTop: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', gap: 2 }}>
          <TextField
            fullWidth
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask me anything!"
            disabled={isLoading}
            size="small"
          />
          <Button
            type="submit"
            variant="contained"
            disabled={isLoading || !inputValue.trim()}
            sx={{ px: 3 }}
          >
            Send
          </Button>
        </Box>
      </Box>
    </Box>
  );
}