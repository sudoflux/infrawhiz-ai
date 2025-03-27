import React from 'react';
import {
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Button,
  Box,
  Divider,
  Tooltip
} from '@mui/material';
import {
  Computer as ComputerIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Add as AddIcon
} from '@mui/icons-material';

const ServerList = ({ 
  servers, 
  selectedServer, 
  onSelectServer, 
  onAddServer, 
  onRemoveServer, 
  onRefreshMetrics 
}) => {
  return (
    <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
      <List sx={{ flexGrow: 1, overflow: 'auto' }}>
        {servers.length === 0 ? (
          <ListItem>
            <ListItemText 
              primary="No servers" 
              secondary="Add a server to begin monitoring" 
            />
          </ListItem>
        ) : (
          servers.map(server => (
            <ListItem 
              key={server.id} 
              button 
              selected={selectedServer && selectedServer.id === server.id}
              onClick={() => onSelectServer(server)}
            >
              <ListItemIcon>
                <ComputerIcon />
              </ListItemIcon>
              <ListItemText 
                primary={server.name} 
                secondary={`${server.username}@${server.hostname}`}
              />
              <ListItemSecondaryAction>
                <Tooltip title="Refresh metrics">
                  <IconButton 
                    edge="end" 
                    aria-label="refresh"
                    onClick={(e) => {
                      e.stopPropagation();
                      onRefreshMetrics(server.id);
                    }}
                  >
                    <RefreshIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Remove server">
                  <IconButton 
                    edge="end" 
                    aria-label="delete"
                    onClick={(e) => {
                      e.stopPropagation();
                      onRemoveServer(server.id);
                    }}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </ListItemSecondaryAction>
            </ListItem>
          ))
        )}
      </List>
      <Divider sx={{ my: 2 }} />
      <Button 
        variant="contained" 
        startIcon={<AddIcon />}
        fullWidth
        onClick={onAddServer}
      >
        Add Server
      </Button>
    </Box>
  );
};

export default ServerList;