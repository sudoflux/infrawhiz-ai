import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Grid
} from '@mui/material';

const ServerForm = ({ open, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    name: '',
    hostname: '',
    username: '',
    password: '',
    key_path: '',
    port: '22',
    auth_method: 'password' // 'password' or 'key'
  });
  
  const [errors, setErrors] = useState({});
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };
  
  const validate = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Server name is required';
    }
    
    if (!formData.hostname.trim()) {
      newErrors.hostname = 'Hostname is required';
    }
    
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    }
    
    if (formData.auth_method === 'password' && !formData.password) {
      newErrors.password = 'Password is required';
    }
    
    if (formData.auth_method === 'key' && !formData.key_path) {
      newErrors.key_path = 'SSH key path is required';
    }
    
    if (formData.port && !/^[0-9]+$/.test(formData.port)) {
      newErrors.port = 'Port must be a number';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = () => {
    if (validate()) {
      // Prepare data for submission
      const serverData = {
        name: formData.name,
        hostname: formData.hostname,
        username: formData.username,
        port: formData.port ? parseInt(formData.port) : 22
      };
      
      // Add auth details based on method
      if (formData.auth_method === 'password') {
        serverData.password = formData.password;
      } else {
        serverData.key_path = formData.key_path;
      }
      
      onSubmit(serverData);
      
      // Reset form
      setFormData({
        name: '',
        hostname: '',
        username: '',
        password: '',
        key_path: '',
        port: '22',
        auth_method: 'password'
      });
      setErrors({});
    }
  };
  
  const handleCancel = () => {
    // Reset form and close
    setFormData({
      name: '',
      hostname: '',
      username: '',
      password: '',
      key_path: '',
      port: '22',
      auth_method: 'password'
    });
    setErrors({});
    onClose();
  };
  
  return (
    <Dialog open={open} onClose={handleCancel} maxWidth="sm" fullWidth>
      <DialogTitle>Add Server</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              name="name"
              label="Server Name"
              fullWidth
              value={formData.name}
              onChange={handleChange}
              error={!!errors.name}
              helperText={errors.name}
            />
          </Grid>
          <Grid item xs={12} sm={8}>
            <TextField
              name="hostname"
              label="Hostname / IP Address"
              fullWidth
              value={formData.hostname}
              onChange={handleChange}
              error={!!errors.hostname}
              helperText={errors.hostname}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              name="port"
              label="SSH Port"
              fullWidth
              value={formData.port}
              onChange={handleChange}
              error={!!errors.port}
              helperText={errors.port}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              name="username"
              label="Username"
              fullWidth
              value={formData.username}
              onChange={handleChange}
              error={!!errors.username}
              helperText={errors.username}
            />
          </Grid>
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Authentication Method</InputLabel>
              <Select
                name="auth_method"
                value={formData.auth_method}
                label="Authentication Method"
                onChange={handleChange}
              >
                <MenuItem value="password">Password</MenuItem>
                <MenuItem value="key">SSH Key</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          {formData.auth_method === 'password' ? (
            <Grid item xs={12}>
              <TextField
                name="password"
                label="Password"
                type="password"
                fullWidth
                value={formData.password}
                onChange={handleChange}
                error={!!errors.password}
                helperText={errors.password}
              />
            </Grid>
          ) : (
            <Grid item xs={12}>
              <TextField
                name="key_path"
                label="SSH Key Path"
                fullWidth
                value={formData.key_path}
                onChange={handleChange}
                error={!!errors.key_path}
                helperText={errors.key_path || "Path to the private key file on the server running InfraWhiz"}
              />
            </Grid>
          )}
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleCancel}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained">Add Server</Button>
      </DialogActions>
    </Dialog>
  );
};

export default ServerForm;