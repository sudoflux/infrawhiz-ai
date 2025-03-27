import React, { useState, useEffect } from 'react';
import { Box, Grid, Paper, Typography } from '@mui/material';
import ServerList from './components/ServerList';
import ChatInterface from './components/ChatInterface';
import ServerMetrics from './components/ServerMetrics';
import ServerForm from './components/ServerForm';
import socket from './socket';
import axios from 'axios';

function App() {
  const [servers, setServers] = useState([]);
  const [selectedServer, setSelectedServer] = useState(null);
  const [metrics, setMetrics] = useState({});
  const [showAddServer, setShowAddServer] = useState(false);
  
  // Get servers on initial load
  useEffect(() => {
    fetchServers();
  }, []);
  
  // Setup socket listeners
  useEffect(() => {
    socket.on('metrics_update', (data) => {
      setMetrics(prev => ({
        ...prev,
        [data.server_id]: data.metrics
      }));
    });
    
    return () => {
      socket.off('metrics_update');
    };
  }, []);
  
  // Fetch servers from API
  const fetchServers = async () => {
    try {
      const response = await axios.get('/api/servers');
      setServers(response.data);
      
      if (response.data.length > 0 && !selectedServer) {
        setSelectedServer(response.data[0]);
      }
    } catch (error) {
      console.error('Failed to fetch servers:', error);
    }
  };
  
  // Add a new server
  const addServer = async (serverData) => {
    try {
      const response = await axios.post('/api/servers', serverData);
      setServers(prev => [...prev, response.data]);
      setShowAddServer(false);
      
      if (!selectedServer) {
        setSelectedServer(response.data);
      }
    } catch (error) {
      console.error('Failed to add server:', error);
    }
  };
  
  // Remove a server
  const removeServer = async (serverId) => {
    try {
      await axios.delete(`/api/servers/${serverId}`);
      
      // Update servers list
      setServers(prev => prev.filter(server => server.id !== serverId));
      
      // Update selected server if needed
      if (selectedServer && selectedServer.id === serverId) {
        const remainingServers = servers.filter(server => server.id !== serverId);
        setSelectedServer(remainingServers.length > 0 ? remainingServers[0] : null);
      }
      
      // Clean up metrics
      setMetrics(prev => {
        const newMetrics = { ...prev };
        delete newMetrics[serverId];
        return newMetrics;
      });
    } catch (error) {
      console.error('Failed to remove server:', error);
    }
  };
  
  // Fetch metrics for a server
  const fetchMetrics = (serverId) => {
    socket.emit('get_metrics', { server_id: serverId });
  };
  
  return (
    <Box sx={{ flexGrow: 1, height: '100vh', p: 2 }}>
      <Grid container spacing={2} sx={{ height: '100%' }}>
        {/* Left sidebar */}
        <Grid item xs={12} md={3} sx={{ height: '100%' }}>
          <Paper sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h5" gutterBottom>
              InfraWhiz
            </Typography>
            <ServerList 
              servers={servers} 
              selectedServer={selectedServer}
              onSelectServer={setSelectedServer}
              onAddServer={() => setShowAddServer(true)}
              onRemoveServer={removeServer}
              onRefreshMetrics={fetchMetrics}
            />
          </Paper>
        </Grid>
        
        {/* Main content */}
        <Grid item xs={12} md={9} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          {selectedServer ? (
            <>
              <ServerMetrics 
                server={selectedServer} 
                metrics={metrics[selectedServer.id] || {}} 
                onRefresh={() => fetchMetrics(selectedServer.id)}
              />
              <Box sx={{ flexGrow: 1, mt: 2 }}>
                <ChatInterface 
                  selectedServer={selectedServer}
                />
              </Box>
            </>
          ) : (
            <Paper sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
              <Typography variant="h6" gutterBottom>
                No servers configured
              </Typography>
              <Typography variant="body1">
                Add a server to start managing it with InfraWhiz.
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>
      
      {/* Add server dialog */}
      <ServerForm 
        open={showAddServer} 
        onClose={() => setShowAddServer(false)} 
        onSubmit={addServer} 
      />
    </Box>
  );
}

export default App;