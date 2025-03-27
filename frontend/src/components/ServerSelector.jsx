import React from 'react';
import { FormControl, InputLabel, Select, MenuItem, Paper, Box, Typography } from '@mui/material';

/**
 * Server selector dropdown component
 * @param {Object} props - Component props
 * @param {Array} props.servers - List of server objects
 * @param {string} props.selectedServer - Currently selected server ID
 * @param {function} props.setSelectedServer - Function to set selected server
 */
function ServerSelector({ servers, selectedServer, setSelectedServer }) {
  const handleChange = (event) => {
    setSelectedServer(event.target.value);
  };

  return (
    <Paper
      elevation={2}
      sx={{
        p: 2,
        backgroundColor: 'background.paper',
      }}
    >
      <Box sx={{ mb: 1 }}>
        <Typography variant="subtitle2" color="text.secondary">
          Target Server
        </Typography>
      </Box>
      <FormControl fullWidth variant="outlined">
        <InputLabel id="server-select-label">Server</InputLabel>
        <Select
          labelId="server-select-label"
          id="server-select"
          value={selectedServer}
          onChange={handleChange}
          label="Server"
          disabled={servers.length === 0}
        >
          <MenuItem value="">
            <em>All Servers</em>
          </MenuItem>
          {servers.map((server) => (
            <MenuItem key={server.id} value={server.id}>
              {server.name} ({server.hostname})
            </MenuItem>
          ))}
          {servers.length === 0 && (
            <MenuItem disabled value="">
              <em>No servers available</em>
            </MenuItem>
          )}
        </Select>
      </FormControl>
      {servers.length === 0 && (
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          No servers configured. Commands will be interpreted as global actions.
        </Typography>
      )}
    </Paper>
  );
}

export default ServerSelector; 