import React from 'react';
import { TextField, Button, Box, Paper, CircularProgress } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

/**
 * Command input component with form and submit button
 * @param {Object} props - Component props
 * @param {string} props.commandInput - Current command input value
 * @param {function} props.setCommandInput - Function to update command input
 * @param {function} props.handleCommandSubmit - Function to handle command submission
 * @param {boolean} props.isLoading - Loading state for form submission
 */
function CommandInput({ commandInput, setCommandInput, handleCommandSubmit, isLoading }) {
  return (
    <Paper
      component="form"
      onSubmit={handleCommandSubmit}
      elevation={3}
      sx={{
        p: 2,
        display: 'flex',
        alignItems: 'flex-start',
        gap: 2,
        backgroundColor: 'background.paper',
      }}
    >
      <TextField
        fullWidth
        id="command-input"
        label="Enter a natural language command"
        variant="outlined"
        value={commandInput}
        onChange={(e) => setCommandInput(e.target.value)}
        placeholder="e.g., Check CPU usage on server1"
        autoComplete="off"
        disabled={isLoading}
        multiline
        maxRows={3}
        InputProps={{
          sx: {
            '& .MuiOutlinedInput-notchedOutline': {
              borderColor: 'rgba(255, 255, 255, 0.23)',
            },
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: 'rgba(255, 255, 255, 0.4)',
            },
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: 'primary.main',
            },
          },
        }}
      />
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <Button
          variant="contained"
          color="primary"
          endIcon={isLoading ? <CircularProgress size={18} color="inherit" /> : <SendIcon />}
          type="submit"
          disabled={!commandInput.trim() || isLoading}
          sx={{
            height: '56px',
            minWidth: '100px',
          }}
        >
          {isLoading ? 'Sending' : 'Send'}
        </Button>
      </Box>
    </Paper>
  );
}

export default CommandInput; 