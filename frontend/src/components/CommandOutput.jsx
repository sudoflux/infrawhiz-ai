import React from 'react';
import { Box, Typography, Divider, CircularProgress, Paper, Chip } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import TerminalIcon from '@mui/icons-material/Terminal';
import CodeIcon from '@mui/icons-material/Code';

/**
 * Command output component to display command history and responses
 * @param {Object} props - Component props
 * @param {Array} props.commandHistory - Array of command history items
 * @param {boolean} props.isLoading - Loading state indicator
 */
function CommandOutput({ commandHistory, isLoading }) {
  // Format timestamp to readable format
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    return date.toLocaleTimeString(undefined, {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  // Render intent info
  const renderIntent = (intent) => {
    return (
      <Box sx={{ my: 1, p: 1.5, backgroundColor: 'rgba(33, 150, 243, 0.1)', borderRadius: 1 }}>
        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          <CodeIcon fontSize="small" sx={{ mr: 1, verticalAlign: 'middle' }} />
          Parsed Intent:
        </Typography>
        <Box sx={{ pl: 2 }}>
          <Typography variant="body2" sx={{ mb: 0.5 }}>
            <strong>Intent:</strong> {intent.intent || 'Unknown'}
          </Typography>
          <Typography variant="body2" sx={{ mb: 0.5 }}>
            <strong>Target Server:</strong> {intent.target_server || 'All'}
          </Typography>
          <Typography variant="body2">
            <strong>Action:</strong> {intent.action || 'Unknown'}
          </Typography>
        </Box>
      </Box>
    );
  };

  // Render command result content
  const renderResultContent = (content) => {
    if (!content) return null;
    
    const { message, data, results } = content;
    
    return (
      <Box>
        {message && (
          <Typography variant="body1" sx={{ mb: 1 }}>
            {message}
          </Typography>
        )}
        
        {results && results.length > 0 && (
          <Box sx={{ mt: 2 }}>
            {results.map((result, idx) => (
              <Paper key={idx} variant="outlined" sx={{ p: 1.5, mb: 1, backgroundColor: 'rgba(0,0,0,0.2)' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Chip 
                    icon={result.success ? <CheckCircleIcon /> : <ErrorIcon />}
                    label={result.server || 'Unknown'}
                    color={result.success ? 'success' : 'error'}
                    variant="outlined"
                    size="small"
                    sx={{ mr: 1 }}
                  />
                  <Typography variant="body2">
                    {result.message}
                  </Typography>
                </Box>
                
                {result.data && result.data.stdout && (
                  <Box 
                    className="terminal-text"
                    sx={{ 
                      backgroundColor: 'rgba(0,0,0,0.4)', 
                      p: 1.5, 
                      borderRadius: 1,
                      maxHeight: '200px',
                      overflow: 'auto'
                    }}
                  >
                    <pre style={{ margin: 0 }}>{result.data.stdout}</pre>
                  </Box>
                )}
              </Paper>
            ))}
          </Box>
        )}
        
        {data && !results && (
          <Box sx={{ mt: 1 }}>
            {data.stdout && (
              <Box 
                className="terminal-text"
                sx={{ 
                  backgroundColor: 'rgba(0,0,0,0.4)', 
                  p: 1.5, 
                  borderRadius: 1,
                  maxHeight: '200px',
                  overflow: 'auto',
                  mb: data.stderr ? 1 : 0
                }}
              >
                <pre style={{ margin: 0 }}>{data.stdout}</pre>
              </Box>
            )}
            
            {data.stderr && (
              <Box 
                className="terminal-text"
                sx={{ 
                  backgroundColor: 'rgba(231, 76, 60, 0.2)', 
                  p: 1.5, 
                  borderRadius: 1,
                  maxHeight: '200px',
                  overflow: 'auto'
                }}
              >
                <Typography color="error.main" variant="caption" sx={{ mb: 0.5, display: 'block' }}>
                  Error Output:
                </Typography>
                <pre style={{ margin: 0, color: '#e74c3c' }}>{data.stderr}</pre>
              </Box>
            )}
          </Box>
        )}
      </Box>
    );
  };

  return (
    <Box>
      {commandHistory.length === 0 && (
        <Box sx={{ 
          height: '100%', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          flexDirection: 'column', 
          py: 8
        }}>
          <TerminalIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography color="text.secondary" variant="body1">
            Enter a command to get started
          </Typography>
          <Typography color="text.secondary" variant="caption" sx={{ mt: 1 }}>
            Try "Check CPU usage on all servers" or "Restart nginx on webserver"
          </Typography>
        </Box>
      )}
      
      {commandHistory.map((item, index) => (
        <Box key={index} sx={{ mb: 3 }}>
          {/* Timestamp and type indicator */}
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
            <Typography variant="caption" color="text.secondary" sx={{ mr: 1 }}>
              {formatTimestamp(item.timestamp)}
            </Typography>
            <Chip 
              label={item.type === 'input' ? 'Command' : 
                    item.type === 'intent' ? 'Intent' : 
                    item.type === 'success' ? 'Success' : 'Error'}
              size="small"
              color={item.type === 'error' ? 'error' : 
                    item.type === 'success' ? 'success' : 
                    item.type === 'intent' ? 'info' : 'default'}
              variant="outlined"
            />
          </Box>
          
          {/* Command text */}
          {item.type === 'input' && (
            <Typography 
              variant="body1" 
              sx={{ 
                fontFamily: 'monospace',
                backgroundColor: 'rgba(255,255,255,0.05)',
                p: 1.5,
                borderRadius: 1,
                wordBreak: 'break-word'
              }}
            >
              &gt; {item.content}
            </Typography>
          )}
          
          {/* Parsed intent */}
          {item.type === 'intent' && renderIntent(item.content)}
          
          {/* Command result */}
          {(item.type === 'success' || item.type === 'error') && (
            <Box sx={{ 
              p: 1.5, 
              backgroundColor: item.type === 'error' ? 'rgba(231, 76, 60, 0.1)' : 'rgba(46, 204, 113, 0.1)', 
              borderRadius: 1,
              borderLeft: item.type === 'error' ? '4px solid #e74c3c' : '4px solid #2ecc71'
            }}>
              {renderResultContent(item.content)}
            </Box>
          )}
          
          {index < commandHistory.length - 1 && (
            <Divider sx={{ my: 2, opacity: 0.3 }} />
          )}
        </Box>
      ))}
      
      {isLoading && (
        <Box sx={{ display: 'flex', alignItems: 'center', my: 2 }}>
          <CircularProgress size={20} sx={{ mr: 2 }} />
          <Typography variant="body2" color="text.secondary">
            Processing command...
          </Typography>
        </Box>
      )}
    </Box>
  );
}

export default CommandOutput; 