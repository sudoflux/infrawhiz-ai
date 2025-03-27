import React, { useEffect } from 'react';
import {
  Paper,
  Typography,
  Grid,
  Box,
  LinearProgress,
  IconButton,
  Tooltip
} from '@mui/material';
import { 
  Refresh as RefreshIcon,
  Memory as MemoryIcon,
  Storage as DiskIcon,
  Router as NetworkIcon,
  Speed as LoadIcon,
  AccessTime as UptimeIcon
} from '@mui/icons-material';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as RechartsTooltip,
  ResponsiveContainer 
} from 'recharts';

const MetricItem = ({ title, value, percentage, icon }) => (
  <Paper sx={{ p: 2, height: '100%' }}>
    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
      <Box sx={{ mr: 1 }}>{icon}</Box>
      <Typography variant="subtitle1">{title}</Typography>
    </Box>
    <Typography variant="h6" sx={{ mb: 1 }}>{value}</Typography>
    {percentage !== undefined && (
      <LinearProgress 
        variant="determinate" 
        value={percentage} 
        sx={{ 
          height: 10, 
          borderRadius: 5,
          '& .MuiLinearProgress-bar': {
            bgcolor: percentage > 80 ? 'error.main' : 
                   percentage > 60 ? 'warning.main' : 'success.main'
          }
        }} 
      />
    )}
  </Paper>
);

const ServerMetrics = ({ server, metrics, onRefresh }) => {
  // Auto-refresh metrics on initial load
  useEffect(() => {
    onRefresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [server.id]);
  
  // Whether we have metrics data
  const hasMetrics = Object.keys(metrics).length > 0 && !metrics.error;
  
  // Format the load average data for the chart
  const loadData = hasMetrics ? [
    { name: '1m', load: metrics.load_1 },
    { name: '5m', load: metrics.load_5 },
    { name: '15m', load: metrics.load_15 }
  ] : [];
  
  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          {server.name} Metrics
        </Typography>
        <Tooltip title="Refresh metrics">
          <IconButton onClick={onRefresh}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>
      
      {metrics.error ? (
        <Typography color="error">
          Error retrieving metrics: {metrics.error}
        </Typography>
      ) : !hasMetrics ? (
        <Typography>
          Loading metrics...
        </Typography>
      ) : (
        <Grid container spacing={2}>
          {/* CPU Usage */}
          <Grid item xs={12} sm={6} md={4}>
            <MetricItem 
              title="CPU Usage" 
              value={`${metrics.cpu_usage?.toFixed(1)}%`} 
              percentage={metrics.cpu_usage}
              icon={<MemoryIcon />}
            />
          </Grid>
          
          {/* Memory Usage */}
          <Grid item xs={12} sm={6} md={4}>
            <MetricItem 
              title="Memory" 
              value={`${metrics.memory_used} / ${metrics.memory_total} MB`} 
              percentage={metrics.memory_percent}
              icon={<MemoryIcon />}
            />
          </Grid>
          
          {/* Disk Usage */}
          <Grid item xs={12} sm={6} md={4}>
            <MetricItem 
              title="Disk Space" 
              value={`${metrics.disk_used} / ${metrics.disk_total}`} 
              percentage={metrics.disk_percent}
              icon={<DiskIcon />}
            />
          </Grid>
          
          {/* Network */}
          <Grid item xs={12} sm={6} md={4}>
            <MetricItem 
              title="Network" 
              value={metrics.network_interface ? 
                `${metrics.network_interface}: RX ${formatBytes(metrics.network_rx)}, TX ${formatBytes(metrics.network_tx)}` : 
                'N/A'
              }
              icon={<NetworkIcon />}
            />
          </Grid>
          
          {/* Uptime */}
          <Grid item xs={12} sm={6} md={4}>
            <MetricItem 
              title="Uptime" 
              value={metrics.uptime || 'N/A'}
              icon={<UptimeIcon />}
            />
          </Grid>
          
          {/* Load Average */}
          <Grid item xs={12} sm={6} md={4}>
            <Paper sx={{ p: 2, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Box sx={{ mr: 1 }}><LoadIcon /></Box>
                <Typography variant="subtitle1">Load Average</Typography>
              </Box>
              <ResponsiveContainer width="100%" height={100}>
                <AreaChart data={loadData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <RechartsTooltip />
                  <Area type="monotone" dataKey="load" stroke="#8884d8" fill="#8884d8" />
                </AreaChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      )}
    </Paper>
  );
};

// Helper function to format bytes
const formatBytes = (bytes, decimals = 2) => {
  if (!bytes) return '0 B';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

export default ServerMetrics;