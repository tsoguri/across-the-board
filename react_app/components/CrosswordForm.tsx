'use client';

import React, { useState } from 'react';
import {
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Typography,
  Box,
  Collapse,
} from '@mui/material';
import { ExpandMore, ExpandLess } from '@mui/icons-material';
import { APIClient } from '../lib/api-client';

interface CrosswordFormProps {
  onSubmit: (formData: {
    topics: string;
    difficulty: string;
    clueModel: string;
    numClues: number;
  }) => void;
  isLoading: boolean;
}

export default function CrosswordForm({ onSubmit, isLoading }: CrosswordFormProps) {
  const [topics, setTopics] = useState('');
  const [availableDifficulties, setAvailableDifficulties] = useState<string[]>([]);
  const [difficulty, setDifficulty] = useState('');
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [clueModel, setClueModel] = useState('');
  const [numClues, setNumClues] = useState(30);
  const [showAdvanced, setShowAdvanced] = useState(false);

  React.useEffect(() => {
    const apiClient = new APIClient();
    Promise.all([
      apiClient.getAvailableModels(),
      apiClient.getDifficultyLevels()
    ]).then(([models, difficulties]) => {
      setAvailableModels(models);
      setAvailableDifficulties(difficulties);
      
      if (models.length > 0) {
        setClueModel(models[0]); // Default to first model (Haiku)
      }
      if (difficulties.length > 0) {
        setDifficulty(difficulties[0]); // Default to first difficulty
      }
    });
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      topics,
      difficulty,
      clueModel,
      numClues,
    });
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      <TextField
        fullWidth
        label="What topics would you like to explore?"
        placeholder="e.g. Classical Music, Theoretical Physics, Gastronomy"
        value={topics}
        onChange={(e) => setTopics(e.target.value)}
        helperText="Enter topics separated by commas - the more specific, the better!"
        variant="outlined"
      />

      <FormControl fullWidth>
        <InputLabel sx={{ fontWeight: 600 }}>Difficulty Level</InputLabel>
        <Select
          value={difficulty}
          label="Difficulty Level"
          onChange={(e) => setDifficulty(e.target.value)}
        >
          {availableDifficulties.map((level) => (
            <MenuItem key={level} value={level}>
              {level}
            </MenuItem>
          ))}
        </Select>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1, p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
          <strong>Easy:</strong> Common facts, high school–level knowledge<br />
          <strong>Medium:</strong> Specific history/science/culture, college-level<br />
          <strong>Hard:</strong> Advanced references, grad-level knowledge
        </Typography>
      </FormControl>

      <Button
        onClick={() => setShowAdvanced(!showAdvanced)}
        startIcon={showAdvanced ? <ExpandLess /> : <ExpandMore />}
        sx={{ 
          textTransform: 'none',
          color: 'text.secondary',
          alignSelf: 'flex-start',
          '&:hover': {
            bgcolor: 'grey.100',
          },
        }}
      >
        Advanced Options
      </Button>

      <Collapse in={showAdvanced}>
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          gap: 3, 
          p: 3, 
          bgcolor: 'grey.50', 
          borderRadius: 1,
          border: '1px solid',
          borderColor: 'grey.200',
        }}>
          <FormControl fullWidth>
            <InputLabel sx={{ fontWeight: 600 }}>AI Model</InputLabel>
            <Select
              value={clueModel}
              label="Large Language Model"
              onChange={(e) => setClueModel(e.target.value)}
            >
              {availableModels.map((model) => (
                <MenuItem key={model} value={model}>
                  {model}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            fullWidth
            type="number"
            label="Number of clues"
            value={numClues}
            onChange={(e) => setNumClues(parseInt(e.target.value))}
            slotProps={{
              htmlInput: {
                min: 10,
                max: 50,
                step: 1
              }
            }}
          />
        </Box>
      </Collapse>

      <Button
        type="submit"
        variant="contained"
        size="large"
        disabled={isLoading || !topics.trim()}
        fullWidth
        sx={{
          py: 2,
          fontSize: '1.1rem',
          fontWeight: 700,
          mt: 2,
        }}
      >
        {isLoading ? 'Generating Your Crossword...' : 'Generate Crossword'}
      </Button>
    </Box>
  );
}