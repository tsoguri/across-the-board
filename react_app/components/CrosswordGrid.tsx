'use client';

import React from 'react';
import { Box, TextField, Paper } from '@mui/material';
import { CrosswordGrid as GridType, BLOCK_TOKEN, EMPTY_CELL } from '../lib/types';

interface CrosswordGridProps {
  grid: GridType;
  userGrid?: GridType;
  showAnswer?: boolean;
  onCellChange?: (row: number, col: number, value: string) => void;
}

export default function CrosswordGrid({
  grid,
  userGrid,
  showAnswer = false,
  onCellChange,
}: CrosswordGridProps) {
  if (!grid || grid.length === 0) return null;


  const handleCellChange = (row: number, col: number, value: string) => {
    if (onCellChange && !showAnswer) {
      onCellChange(row, col, value.toUpperCase());
    }
  };

  const getCellValue = (row: number, col: number): string => {
    const originalCell = grid[row]?.[col];
    
    // Don't show anything for block cells
    if (isBlockCell(row, col)) {
      return '';
    }
    
    if (showAnswer) {
      return originalCell || '';
    }
    
    return userGrid?.[row]?.[col] || '';
  };

  const isBlockCell = (row: number, col: number): boolean => {
    const originalCell = grid[row]?.[col];
    return originalCell === null || 
           originalCell === EMPTY_CELL || 
           originalCell === BLOCK_TOKEN ||
           originalCell === '#' ||
           originalCell === '##' ||
           originalCell === '⬛⬛';
  };

  return (
    <Paper 
      elevation={3}
      sx={{ 
        display: 'inline-block', 
        p: 3, 
      }}
    >
      {grid.map((row, rowIndex) => (
        <Box key={rowIndex} sx={{ display: 'flex', gap: 0.5 }}>
          {row.map((_, colIndex) => {
            const cellValue = getCellValue(rowIndex, colIndex);
            const isBlock = isBlockCell(rowIndex, colIndex);
            
            return (
              <Box key={colIndex} sx={{ position: 'relative' }}>
                {!isBlock ? (
                  <TextField
                    value={cellValue}
                    onChange={(e) => handleCellChange(rowIndex, colIndex, e.target.value)}
                    disabled={showAnswer}
                    variant="outlined"
                    slotProps={{
                      htmlInput: {
                        maxLength: 1,
                        style: {
                          padding: 0,
                          textAlign: 'center',
                          fontWeight: 'bold',
                          fontSize: '20px',
                          textTransform: 'uppercase'
                        }
                      }
                    }}
                    sx={{
                      width: '48px',
                      height: '48px',
                      '& .MuiOutlinedInput-root': {
                        width: '48px',
                        height: '48px',
                        borderRadius: '8px',
                        '& fieldset': {
                          borderColor: showAnswer ? 'success.main' : 'grey.300',
                          borderWidth: 2,
                        },
                        '&:hover fieldset': {
                          borderColor: showAnswer ? 'success.main' : 'primary.main',
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: 'primary.main',
                          borderWidth: 2,
                        },
                        '&.Mui-disabled': {
                          bgcolor: showAnswer ? 'success.50' : 'background.paper',
                          color: 'text.primary',
                          '& input': {
                            color: showAnswer ? 'success.800' : 'text.primary',
                            WebkitTextFillColor: 'currentColor',
                            fontWeight: 'bold',
                          }
                        },
                      },
                    }}
                  />
                ) : (
                  <Box sx={{
                    width: '48px',
                    height: '48px',
                    bgcolor: 'grey.900',
                    borderRadius: '8px',
                    border: '2px solid',
                    borderColor: 'grey.700',
                  }} />
                )}
                
                {/* Row and column numbers for first row/column */}
                {rowIndex === 0 && (
                  <Box sx={{
                    position: 'absolute',
                    top: -20,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    fontSize: '11px',
                    color: 'text.secondary',
                    fontWeight: 500,
                  }}>
                    {colIndex}
                  </Box>
                )}
                {colIndex === 0 && (
                  <Box sx={{
                    position: 'absolute',
                    left: -20,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    fontSize: '11px',
                    color: 'text.secondary',
                    fontWeight: 500,
                  }}>
                    {rowIndex}
                  </Box>
                )}
              </Box>
            );
          })}
        </Box>
      ))}
    </Paper>
  );
}