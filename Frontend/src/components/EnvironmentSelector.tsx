import React, { useState, useEffect } from 'react';
import { FormControl, InputLabel, Select, MenuItem, Box, Typography } from '@mui/material';
import { api } from 'api/client';

interface EnvironmentSelectorProps {
  value: string;
  onChange: (environment: string) => void;
}

export const EnvironmentSelector: React.FC<EnvironmentSelectorProps> = ({ value, onChange }) => {
  const [environments, setEnvironments] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadEnvironments = async () => {
      try {
        setLoading(true);
        const data = await api.getEnvironments();
        setEnvironments(data);
      } catch (error) {
        console.error('Failed to load environments:', error);
      } finally {
        setLoading(false);
      }
    };

    loadEnvironments();
  }, []);

  return (
    <Box sx={{ mb: 3 }}>
      <Typography variant="subtitle1" gutterBottom>
        Environment Configuration
      </Typography>
      <FormControl fullWidth>
        <InputLabel>Environment</InputLabel>
        <Select
          value={value || ''}
          onChange={(e) => onChange(e.target.value as string)}
          disabled={loading}
        >
          {Object.keys(environments).map((envName) => (
            <MenuItem key={envName} value={envName}>
              {envName} - {environments[envName].url}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </Box>
  );
};