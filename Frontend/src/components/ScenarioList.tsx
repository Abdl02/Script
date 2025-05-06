import React, { useState, useEffect } from 'react';
import { api } from 'api/client';
import { Card, TextField, Button, Box, Typography, CircularProgress, Paper } from '@mui/material';

interface ScenarioListProps {
  onSelect: (name: string) => void;
  onNew: () => void;
}

export const ScenarioList: React.FC<ScenarioListProps> = ({ onSelect, onNew }) => {
  const [scenarios, setScenarios] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadScenarios();
  }, []);

  const loadScenarios = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching scenarios...');
      const data = await api.getScenarios();
      console.log('API response:', data);

      if (Array.isArray(data)) {
        // Filter out any non-string values
        const validScenarios = data.filter(name => name && typeof name === 'string');
        setScenarios(validScenarios);
      } else {
        console.warn('Unexpected data format from API:', data);
        setScenarios([]);
      }
    } catch (error) {
      console.error('Failed to load scenarios:', error);
      setError('Failed to load scenarios. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    loadScenarios();
  };

  const filteredScenarios = scenarios
    .filter(name => name && typeof name === 'string')
    .filter(name => name.toLowerCase().includes((searchTerm || '').toLowerCase()));

  return (
    <Box>
      <TextField
        fullWidth
        variant="outlined"
        placeholder="Search scenarios..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        margin="normal"
      />

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Box sx={{ my: 2 }}>
          <Typography color="error" sx={{ mb: 2 }}>{error}</Typography>
          <Button variant="outlined" color="primary" onClick={handleRetry}>
            Retry
          </Button>
        </Box>
      ) : filteredScenarios.length === 0 ? (
        <Paper sx={{ p: 3, my: 2, backgroundColor: '#f5f5f5', textAlign: 'center' }}>
          <Typography sx={{ mb: 2 }}>
            {scenarios.length === 0
              ? "No scenarios found. Create a new one to get started!"
              : "No scenarios match your search. Try a different term."}
          </Typography>
          {scenarios.length === 0 && (
            <Button variant="contained" color="primary" onClick={handleRetry} sx={{ mr: 2 }}>
              Refresh
            </Button>
          )}
        </Paper>
      ) : (
        filteredScenarios.map((name, index) => (
          <Card
            key={index}
            sx={{
              mb: 2,
              p: 2,
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              '&:hover': {
                boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
                transform: 'translateY(-2px)'
              }
            }}
            onClick={() => onSelect(name)}
          >
            <Typography variant="h6">{name}</Typography>
          </Card>
        ))
      )}

      <Button
        variant="contained"
        color="primary"
        fullWidth
        onClick={onNew}
        sx={{ mt: 2 }}
      >
        + New Scenario
      </Button>
    </Box>
  );
};