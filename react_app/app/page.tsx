'use client';

import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Alert, 
  CircularProgress, 
  Box, 
  FormControlLabel,
  Checkbox,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import CrosswordForm from '../components/CrosswordForm';
import CrosswordGrid from '../components/CrosswordGrid';
import CrosswordClues from '../components/CrosswordClues';
import ChatInterface from '../components/ChatInterface';
import { APIClient } from '../lib/api-client';
import {
  CrosswordGrid as GridType,
  Placement,
  CrosswordClue,
  CLAUDE_MODELS,
  EMPTY_CELL,
} from '../lib/types';

export default function Home() {
  const [apiClient] = useState(() => new APIClient());
  const [isApiHealthy, setIsApiHealthy] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isChatLoading, setIsChatLoading] = useState(false);
  
  // Crossword state
  const [grid, setGrid] = useState<GridType | null>(null);
  const [userGrid, setUserGrid] = useState<GridType | null>(null);
  const [placements, setPlacements] = useState<Placement[]>([]);
  
  // UI state
  const [currentPage, setCurrentPage] = useState<'form' | 'crossword'>('form');
  const [showAnswers, setShowAnswers] = useState(false);
  const [selectedClue, setSelectedClue] = useState<CrosswordClue | null>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [chatType, setChatType] = useState<string>('');

  // Check API health on mount
  useEffect(() => {
    const checkHealth = async () => {
      const healthy = await apiClient.healthCheck();
      setIsApiHealthy(healthy);
    };
    checkHealth();
  }, [apiClient]);

  const handleFormSubmit = async (formData: {
    topics: string;
    difficulty: string;
    clueModel: string;
    numClues: number;
  }) => {
    setIsLoading(true);
    try {
      // Reset previous state
      setGrid(null);
      setPlacements([]);
      setUserGrid(null);
      setSelectedClue(null);
      setShowAnswers(false);

      // Generate clues
      const clueResponse = await apiClient.generateClues({
        topic_str: formData.topics,
        difficulty: formData.difficulty,
        num_clues: formData.numClues,
        model: formData.clueModel,
      });

      if (clueResponse && clueResponse.clues) {
        // Generate crossword
        const crosswordResult = await apiClient.generateCrossword({
          clues: clueResponse.clues,
        });

        if (crosswordResult) {
          setGrid(crosswordResult.grid);
          setPlacements(crosswordResult.placements.sort((a, b) => 
            a.row === b.row ? a.col - b.col : a.row - b.row
          ));
          
          // Initialize user grid
          const newUserGrid = crosswordResult.grid.map(row =>
            row.map(cell => (cell === null || cell === EMPTY_CELL) ? null : '')
          );
          setUserGrid(newUserGrid);
          
          // Navigate to crossword page
          setCurrentPage('crossword');
        }
      }
    } catch (error) {
      console.error('Error generating crossword:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCellChange = (row: number, col: number, value: string) => {
    if (!userGrid) return;
    
    const newUserGrid = userGrid.map((r, rowIndex) =>
      r.map((c, colIndex) => {
        if (rowIndex === row && colIndex === col) {
          return value.toUpperCase();
        }
        return c;
      })
    );
    setUserGrid(newUserGrid);
  };

  const handleClueSelect = (placement: Placement, chatType: string) => {
    setSelectedClue({
      clue: placement.clue,
      answer: placement.word,
    });
    setChatType(chatType);
    setChatOpen(true);
  };

  const handleSendMessage = async (message: string, chatType: string): Promise<string | null> => {
    if (!selectedClue) return null;
    
    setIsChatLoading(true);
    try {
      const response = await apiClient.generateChatResponse({
        user_input: message,
        clue: selectedClue,
        chat_type: chatType,
        historical_messages: [], // For simplicity, not tracking history in this component
        model: CLAUDE_MODELS[1], // Use Sonnet for chat
      });
      return response;
    } catch (error) {
      console.error('Error sending chat message:', error);
      return null;
    } finally {
      setIsChatLoading(false);
    }
  };

  if (isApiHealthy === false) {
    return (
      <Container maxWidth="sm" sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Alert severity="error" sx={{ textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>
            ❌ API Server Not Running
          </Typography>
          <Typography variant="body2" gutterBottom>
            Please start the API server with:
          </Typography>
          <Box component="code" sx={{ 
            backgroundColor: 'rgba(211, 47, 47, 0.1)', 
            padding: 1, 
            borderRadius: 1, 
            display: 'block', 
            mt: 1,
            fontFamily: 'monospace'
          }}>
            python scripts/run_api.py
          </Box>
        </Alert>
      </Container>
    );
  }

  if (isApiHealthy === null) {
    return (
      <Container maxWidth="sm" sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Box textAlign="center">
          <CircularProgress sx={{ mb: 2 }} />
          <Typography variant="body1">Checking API connection...</Typography>
        </Box>
      </Container>
    );
  }

  // Form Page
  if (currentPage === 'form') {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          display: 'flex',
          alignItems: 'center',
          py: 4,
        }}
      >
        <Container maxWidth="md">
          <Box textAlign="center" mb={6}>
            <Typography 
              variant="h1" 
              component="h1" 
              gutterBottom 
              sx={{ 
                color: 'white',
                mb: 2,
                textShadow: '0 4px 8px rgba(0,0,0,0.2)',
              }}
            >
              Across the Board
            </Typography>
            <Typography 
              variant="h5" 
              sx={{ 
                color: 'rgba(255,255,255,0.9)',
                fontWeight: 400,
                mb: 4,
              }}
            >
              Learn with a custom crossword puzzle crafted just for you
            </Typography>
          </Box>

          <Box
            sx={{
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(20px)',
              borderRadius: 4,
              p: 4,
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
            }}
          >
            <CrosswordForm onSubmit={handleFormSubmit} isLoading={isLoading} />

            {isLoading && (
              <Box textAlign="center" py={4}>
                <CircularProgress 
                  sx={{ 
                    mb: 2,
                    color: 'primary.main',
                  }} 
                />
              </Box>
            )}
          </Box>
        </Container>
      </Box>
    );
  }

  // Crossword Page
  return (
    <Box sx={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      py: 4,
    }}>
      <Container maxWidth="xl">
        <Button 
            variant="outlined" 
            onClick={() => setCurrentPage('form')}
            startIcon={<Box component="span">←</Box>}
            sx={{ 
              bgcolor: 'rgba(255, 255, 255, 0.95)',
              mb: 4,
              px: 3,
              py: 1.5,
            }}
          >
            Back to Form
          </Button>

        {grid && placements.length > 0 && (
          <Box
            sx={{
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(20px)',
              borderRadius: 4,
              p: 4,
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
            }}
          >
            <Box sx={{ display: 'flex', gap: 4, alignItems: 'flex-start' }}>
              {/* Crossword Grid Section */}
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'left', gap: 3, flex: '0 0 auto' }}>
                <CrosswordGrid
                  grid={grid}
                  userGrid={userGrid || undefined}
                  showAnswer={showAnswers}
                  onCellChange={handleCellChange}
                />
                <Box sx={{ display: 'flex', alignItems: 'left', gap: 1 }}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={showAnswers}
                        onChange={(e) => setShowAnswers(e.target.checked)}
                      />
                    }
                    label="Show answers"
                  />
                </Box>
              </Box>

              {/* Clues Section */}
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <CrosswordClues
                  placements={placements}
                  showAnswer={showAnswers}
                  onClueSelect={handleClueSelect}
                />
              </Box>
            </Box>
          </Box>
        )}

        {/* Chat Dialog */}
        <Dialog
          open={chatOpen}
          onClose={() => setChatOpen(false)}
          maxWidth="md"
          fullWidth
          slotProps={{
            paper: {
              sx: {
                borderRadius: 3,
                minHeight: '60vh',
              }
            }
          }}
        >
          <DialogTitle sx={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            color: 'white',
          }}>
            <Typography variant="h6" component="div">
              {chatType === 'Get a Hint' ? '💡 Get a Hint' : '🔍 Deep Dive'}
            </Typography>
            <IconButton
              aria-label="close"
              onClick={() => setChatOpen(false)}
              sx={{ color: 'white' }}
            >
              <CloseIcon />
            </IconButton>
          </DialogTitle>
          <DialogContent sx={{ p: 0 }}>
            <ChatInterface
              selectedClue={selectedClue}
              onSendMessage={handleSendMessage}
              isLoading={isChatLoading}
              chatType={chatType}
            />
          </DialogContent>
        </Dialog>
      </Container>
    </Box>
  );
}
