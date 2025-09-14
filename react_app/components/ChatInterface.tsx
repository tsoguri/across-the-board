'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
  Typography,
  Box,
  TextField,
  Button,
  CircularProgress,
  IconButton,
  Paper,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import ReactMarkdown from 'react-markdown';
import { ChatMessage, CrosswordClue, CHAT_TYPES } from '../lib/types';

interface ChatInterfaceProps {
  selectedClue: CrosswordClue | null;
  onSendMessage: (message: string, chatType: string) => Promise<string | null>;
  isLoading: boolean;
  chatType?: string;
  onClose: () => void;
}

export default function ChatInterface({ selectedClue, onSendMessage, isLoading, chatType = 'Get a Hint', onClose }: ChatInterfaceProps) {
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
    return null;
  }

  return (
    <Paper
      elevation={8}
      sx={{
        position: 'fixed',
        bottom: 20,
        right: 20,
        width: 500,
        height: 600,
        display: 'flex',
        flexDirection: 'column',
        borderRadius: 3,
        overflow: 'hidden',
        zIndex: 1300,
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(20px)',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1)',
      }}
    >
      {/* Header */}
      <Box sx={{ 
        p: 2, 
        borderBottom: 1, 
        borderColor: 'divider',
        bgcolor: chatType === 'Get a Hint' ? 'secondary.light' : 'primary.main',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <Box>
          <Typography variant="h6" sx={{ fontSize: '1rem', fontWeight: 600 }}>
            {chatType === 'Get a Hint' ? '💡 Get a Hint' : '🔍 Deep Dive'}
          </Typography>
          <Typography variant="caption" sx={{ opacity: 0.9, fontSize: '0.75rem' }}>
            {selectedClue.clue}
          </Typography>
        </Box>
        <IconButton
          onClick={onClose}
          size="small"
          sx={{ color: 'white' }}
        >
          <CloseIcon />
        </IconButton>
      </Box>

      {/* Messages Container */}
      <Box 
        sx={{ 
          flex: 1,
          overflowY: 'auto', 
          p: 2, 
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
                {message.role === 'assistant' ? (
                  <ReactMarkdown
                    components={{
                      p: ({ children }) => (
                        <Typography variant="body2" sx={{ mb: 1, '&:last-child': { mb: 0 } }}>
                          {children}
                        </Typography>
                      ),
                      strong: ({ children }) => (
                        <Typography component="span" sx={{ fontWeight: 'bold' }}>
                          {children}
                        </Typography>
                      ),
                      em: ({ children }) => (
                        <Typography component="span" sx={{ fontStyle: 'italic' }}>
                          {children}
                        </Typography>
                      ),
                      ul: ({ children }) => (
                        <Box component="ul" sx={{ pl: 2, my: 1 }}>
                          {children}
                        </Box>
                      ),
                      ol: ({ children }) => (
                        <Box component="ol" sx={{ pl: 2, my: 1 }}>
                          {children}
                        </Box>
                      ),
                      li: ({ children }) => (
                        <Typography component="li" variant="body2" sx={{ mb: 0.5 }}>
                          {children}
                        </Typography>
                      ),
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                ) : (
                  <Typography variant="body2">
                    {message.content}
                  </Typography>
                )}
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
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', gap: 1 }}>
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
            size="small"
            sx={{ px: 2 }}
          >
            Send
          </Button>
        </Box>
      </Box>
    </Paper>
  );
}