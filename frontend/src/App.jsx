import React, { useState, useEffect, useRef } from 'react';
import { 
  Container, 
  Typography, 
  TextField, 
  Button, 
  Paper, 
  Box, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  AppBar, 
  Toolbar,
  IconButton,
  Grid,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import axios from 'axios';
import ServerSelector from './components/ServerSelector';
import CommandInput from './components/CommandInput';
import CommandOutput from './components/CommandOutput';

function App() {
  // State for server list, selected server, and command input
  const [servers, setServers] = useState([]);
  const [selectedServer, setSelectedServer] = useState('');
  const [commandInput, setCommandInput] = useState('');
  const [commandHistory, setCommandHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // Ref for scrolling to bottom of output
  const outputEndRef = useRef(null);

  // Auto-scroll to bottom when new command output is added
  useEffect(() => {
    if (outputEndRef.current) {
      outputEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [commandHistory]);

  // Function to process command input
  const handleCommandSubmit = async (e) => {
    e.preventDefault();
    
    if (!commandInput.trim()) return;
    
    // Add user input to history
    setCommandHistory(prev => [
      ...prev, 
      { 
        type: 'input', 
        content: commandInput,
        timestamp: new Date()
      }
    ]);
    
    // Clear input field
    setCommandInput('');
    
    try {
      setIsLoading(true);
      
      // Send command to API
      const response = await axios.post('http://localhost:5000/api/query', {
        input: commandInput
      });
      
      // Process response
      const responseData = response.data;
      
      // Add parsed intent to history
      if (responseData.parsed_intent) {
        setCommandHistory(prev => [
          ...prev,
          {
            type: 'intent',
            content: responseData.parsed_intent,
            timestamp: new Date()
          }
        ]);
      }
      
      // Add response message to history
      setCommandHistory(prev => [
        ...prev,
        {
          type: responseData.success ? 'success' : 'error',
          content: responseData,
          timestamp: new Date()
        }
      ]);
      
    } catch (error) {
      console.error('Error sending command:', error);
      
      // Add error to history
      setCommandHistory(prev => [
        ...prev,
        {
          type: 'error',
          content: {
            message: `Error: ${error.message || 'Unknown error'}`,
            error: error
          },
          timestamp: new Date()
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* App Bar */}
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            InfraWhiz Console
          </Typography>
        </Toolbar>
      </AppBar>
      
      {/* Main Content */}
      <Container maxWidth="lg" sx={{ mt: 3, mb: 3, flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <Grid container spacing={2} sx={{ mb: 2 }}>
          {/* Server Selector */}
          <Grid item xs={12} md={6}>
            <ServerSelector 
              servers={servers} 
              selectedServer={selectedServer} 
              setSelectedServer={setSelectedServer} 
            />
          </Grid>
        </Grid>
        
        {/* Command Output Area */}
        <Paper 
          elevation={3} 
          sx={{ 
            p: 2, 
            flexGrow: 1, 
            mb: 2, 
            backgroundColor: '#1e1e1e',
            overflow: 'auto',
            minHeight: '400px',
            maxHeight: '60vh'
          }}
        >
          <CommandOutput 
            commandHistory={commandHistory}
            isLoading={isLoading}
          />
          <div ref={outputEndRef} />
        </Paper>
        
        {/* Command Input */}
        <CommandInput 
          commandInput={commandInput}
          setCommandInput={setCommandInput}
          handleCommandSubmit={handleCommandSubmit}
          isLoading={isLoading}
        />
      </Container>
      
      {/* Footer */}
      <Box 
        component="footer" 
        sx={{ 
          py: 2, 
          px: 2, 
          mt: 'auto', 
          backgroundColor: 'background.paper',
          borderTop: '1px solid #333'
        }}
      >
        <Typography variant="body2" color="text.secondary" align="center">
          InfraWhiz - AI-Powered Linux Server Management
        </Typography>
      </Box>
    </Box>
  );
}

export default App; 