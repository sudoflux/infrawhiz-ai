import React, { useState, useEffect, useRef } from 'react';
import {
  Paper,
  Box,
  TextField,
  Button,
  Typography,
  List,
  ListItem,
  Divider,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions
} from '@mui/material';
import { 
  Send as SendIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Error as ErrorIcon,
  SystemUpdate as ExecuteIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import socket from '../socket';

const ChatInterface = ({ selectedServer }) => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [confirmAction, setConfirmAction] = useState(null);
  const messagesEndRef = useRef(null);
  
  // Setup socket listeners
  useEffect(() => {
    // Listen for AI responses
    socket.on('ai_response', (data) => {
      setLoading(false);
      
      // Add the message to the chat
      setMessages(prevMessages => [
        ...prevMessages,
        { sender: 'ai', content: data.message, actions: data.actions || [] }
      ]);
      
      // If there's a confirmation action, set it
      const confirmActions = data.actions?.filter(a => a.type === 'confirm') || [];
      if (confirmActions.length > 0) {
        setConfirmAction(confirmActions[0]);
      }
    });
    
    // Listen for command execution results
    socket.on('action_result', (data) => {
      setMessages(prevMessages => [
        ...prevMessages,
        { 
          sender: 'system', 
          content: 'Command execution result:',
          result: {
            stdout: data.result.stdout,
            stderr: data.result.stderr,
            exitCode: data.result.exit_code
          }
        }
      ]);
    });
    
    return () => {
      socket.off('ai_response');
      socket.off('action_result');
    };
  }, []);
  
  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // Handle sending a message
  const handleSendMessage = (e) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    
    // Add the user message to the chat
    setMessages(prevMessages => [
      ...prevMessages,
      { sender: 'user', content: input }
    ]);
    
    // Send the message to the backend
    socket.emit('user_message', { message: input });
    
    // Clear the input and show loading state
    setInput('');
    setLoading(true);
  };
  
  // Handle executing an action
  const handleExecuteAction = (action) => {
    // Execute the command on the server
    socket.emit('execute_action', {
      action: action.type,
      server_id: action.server_id,
      command: action.command
    });
    
    // Add a message showing we executed the command
    setMessages(prevMessages => [
      ...prevMessages,
      { 
        sender: 'system', 
        content: `Executing command: ${action.command}`
      }
    ]);
    
    // Close the confirmation dialog if open
    setConfirmAction(null);
  };
  
  // Format the message content based on type
  const formatMessage = (message) => {
    if (message.sender === 'system' && message.result) {
      // Command result
      return (
        <Box>
          <Typography variant="body1">{message.content}</Typography>
          <Paper sx={{ p: 1, mt: 1, bgcolor: 'background.paper' }}>
            {message.result.stdout && (
              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                  Standard Output:
                </Typography>
                <Box 
                  component="pre" 
                  sx={{ 
                    whiteSpace: 'pre-wrap', 
                    overflowX: 'auto',
                    fontSize: '0.875rem',
                    mt: 0.5
                  }}
                >
                  {message.result.stdout}
                </Box>
              </Box>
            )}
            
            {message.result.stderr && (
              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" sx={{ fontWeight: 'bold', color: 'error.main' }}>
                  Standard Error:
                </Typography>
                <Box 
                  component="pre" 
                  sx={{ 
                    whiteSpace: 'pre-wrap', 
                    overflowX: 'auto',
                    fontSize: '0.875rem',
                    mt: 0.5,
                    color: 'error.main'
                  }}
                >
                  {message.result.stderr}
                </Box>
              </Box>
            )}
            
            <Typography variant="body2">
              Exit code: <span style={{ color: message.result.exitCode === 0 ? 'green' : 'red' }}>
                {message.result.exitCode}
              </span>
            </Typography>
          </Paper>
        </Box>
      );
    }
    
    // Regular message with possible actions
    return (
      <Box>
        <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>{message.content}</Typography>
        
        {message.actions && message.actions.length > 0 && message.actions.some(a => a.type === 'execute') && (
          <Box sx={{ mt: 1 }}>
            {message.actions.filter(a => a.type === 'execute').map((action, index) => (
              <Button
                key={index}
                variant="contained"
                size="small"
                startIcon={<ExecuteIcon />}
                onClick={() => handleExecuteAction(action)}
                sx={{ mr: 1, mt: 1 }}
              >
                Execute Command
              </Button>
            ))}
          </Box>
        )}
      </Box>
    );
  };
  
  return (
    <Paper sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Chat messages */}
      <Box sx={{ p: 2, flexGrow: 1, overflow: 'auto', maxHeight: 'calc(100vh - 300px)' }}>
        {messages.length === 0 ? (
          <Box 
            sx={{ 
              height: '100%', 
              display: 'flex', 
              flexDirection: 'column', 
              justifyContent: 'center', 
              alignItems: 'center',
              color: 'text.secondary'
            }}
          >
            <InfoIcon sx={{ fontSize: 48, mb: 2, opacity: 0.7 }} />
            <Typography variant="h6">Welcome to InfraWhiz</Typography>
            <Typography variant="body1" align="center">
              Type natural language commands to manage your server.<br />
              For example: "What's the CPU usage?" or "Restart nginx"
            </Typography>
          </Box>
        ) : (
          <List>
            {messages.map((message, index) => (
              <React.Fragment key={index}>
                <ListItem 
                  sx={{ 
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: message.sender === 'user' ? 'flex-end' : 'flex-start',
                    p: 1
                  }}
                >
                  <Box 
                    sx={{ 
                      bgcolor: message.sender === 'user' ? 'primary.dark' : 'background.paper',
                      borderRadius: 2,
                      p: 1.5,
                      maxWidth: '80%'
                    }}
                  >
                    {formatMessage(message)}
                  </Box>
                </ListItem>
                {index < messages.length - 1 && <Divider variant="middle" />}
              </React.Fragment>
            ))}
            <div ref={messagesEndRef} />
          </List>
        )}
      </Box>
      
      {/* Input area */}
      <Box 
        component="form" 
        onSubmit={handleSendMessage}
        sx={{ 
          p: 2, 
          borderTop: 1, 
          borderColor: 'divider',
          display: 'flex',
          alignItems: 'center' 
        }}
      >
        <TextField
          fullWidth
          placeholder="Ask something about your server..."
          variant="outlined"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
          autoFocus
        />
        <Button 
          type="submit" 
          variant="contained" 
          sx={{ ml: 1, minWidth: 0, width: 56, height: 56 }}
          disabled={loading || !input.trim()}
        >
          {loading ? <CircularProgress size={24} /> : <SendIcon />}
        </Button>
      </Box>
      
      {/* Confirmation dialog for destructive actions */}
      <Dialog
        open={!!confirmAction}
        onClose={() => setConfirmAction(null)}
      >
        <DialogTitle>Confirm Action</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to run this command?
          </DialogContentText>
          {confirmAction && (
            <Paper sx={{ p: 1, mt: 2, bgcolor: 'background.paper' }}>
              <Typography variant="code" sx={{ fontFamily: 'monospace' }}>
                {confirmAction.command}
              </Typography>
            </Paper>
          )}
          <DialogContentText sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
            <ErrorIcon sx={{ mr: 1, color: 'warning.main' }} />
            This operation may affect server functionality.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setConfirmAction(null)} 
            startIcon={<CloseIcon />}
          >
            Cancel
          </Button>
          <Button 
            onClick={() => handleExecuteAction(confirmAction)}
            variant="contained" 
            color="error"
            startIcon={<CheckIcon />}
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default ChatInterface;