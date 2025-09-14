'use client';

import React, { useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Grid,
  Button,
  Fade,
} from '@mui/material';
import { Placement } from '../lib/types';

interface CrosswordCluesProps {
  placements: Placement[];
  showAnswer?: boolean;
  onClueSelect?: (clue: Placement, chatType: string) => void;
}

export default function CrosswordClues({
  placements,
  showAnswer = false,
  onClueSelect,
}: CrosswordCluesProps) {
  const [hoveredClue, setHoveredClue] = useState<string | null>(null);
  
  if (!placements || placements.length === 0) return null;

  const acrossClues = placements.filter(p => p.direction === 'across');
  const downClues = placements.filter(p => p.direction === 'down');

  const renderClueList = (title: string, clues: Placement[]) => (
    <Box>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
        {title}
      </Typography>
      <Box sx={{ mb: 2 }}>
        <Grid container spacing={1} sx={{ mb: 1 }}>
          <Grid item xs={1}>
            <Typography variant="caption" fontWeight="medium" color="text.secondary">
              Row
            </Typography>
          </Grid>
          <Grid item xs={1}>
            <Typography variant="caption" fontWeight="medium" color="text.secondary">
              Col
            </Typography>
          </Grid>
          <Grid item xs={10}>
            <Typography variant="caption" fontWeight="medium" color="text.secondary">
              Description
            </Typography>
          </Grid>
        </Grid>
        <List dense>
          {clues.map((placement, index) => {
            const clueKey = `${placement.direction}-${index}`;
            const clueText = showAnswer ? `${placement.clue} (${placement.word})` : placement.clue;
            const isHovered = hoveredClue === clueKey;
            
            return (
              <ListItem key={clueKey} disablePadding>
                <Box
                  sx={{ 
                    width: '100%', 
                    position: 'relative',
                    borderRadius: 1,
                    '&:hover': {
                      bgcolor: 'grey.50',
                    }
                  }}
                  onMouseEnter={() => setHoveredClue(clueKey)}
                  onMouseLeave={() => setHoveredClue(null)}
                >
                  <ListItemButton sx={{ borderRadius: 1, py: 1, pr: 20 }}>
                    <Grid container spacing={1} sx={{ width: '100%', alignItems: 'center' }}>
                      <Grid item xs={1}>
                        <Typography variant="body2" textAlign="center" fontWeight="medium">
                          {placement.row}
                        </Typography>
                      </Grid>
                      <Grid item xs={1}>
                        <Typography variant="body2" textAlign="center" fontWeight="medium">
                          {placement.col}
                        </Typography>
                      </Grid>
                      <Grid item xs={10}>
                        <Typography variant="body2">
                          {clueText}
                        </Typography>
                      </Grid>
                    </Grid>
                  </ListItemButton>
                  
                  {/* Hover Actions */}
                  <Fade in={isHovered}>
                    <Box
                      sx={{
                        position: 'absolute',
                        right: 8,
                        top: '50%',
                        transform: 'translateY(-50%)',
                        display: 'flex',
                        gap: 0.5,
                        zIndex: 10,
                      }}
                    >
                      <Button
                        size="small"
                        variant="contained"
                        onClick={(e) => {
                          e.stopPropagation();
                          onClueSelect?.(placement, 'Get a Hint');
                        }}
                        sx={{
                          minWidth: 'auto',
                          px: 1,
                          py: 0.25,
                          fontSize: '13px',
                          lineHeight: 1.5,
                          background: 'linear-gradient(135deg, #f59e0b, #d97706)',
                          '&:hover': {
                            background: 'linear-gradient(135deg, #d97706, #b45309)',
                          }
                        }}
                      >
                        💡 Hint
                      </Button>
                      <Button
                        size="small"
                        variant="contained"
                        onClick={(e) => {
                          e.stopPropagation();
                          onClueSelect?.(placement, 'Deep Dive into the Answer');
                        }}
                        sx={{
                          minWidth: 'auto',
                          px: 1,
                          py: 0.25,
                          fontSize: '13px',
                          lineHeight: 1.5,
                          background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                          '&:hover': {
                            background: 'linear-gradient(135deg, #4f46e5, #7c3aed)',
                          }
                        }}
                      >
                        🔍 Deep Dive
                      </Button>
                    </Box>
                  </Fade>
                </Box>
              </ListItem>
            );
          })}
        </List>
      </Box>
    </Box>
  );

  return (
    <Paper sx={{ p: 3, height: 'fit-content' }}>
      <Typography variant="h5" component="h3" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <span style={{ marginRight: 8 }}>🔍</span>
        Clues
      </Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {renderClueList('Across', acrossClues)}
        {renderClueList('Down', downClues)}
      </Box>
    </Paper>
  );
}