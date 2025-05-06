import React, { useState, useEffect } from 'react';
import { api } from 'api/client';
import { Card, TextField, Button, Box, Typography, CircularProgress } from '@mui/material';

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

      // The API returns an array of strings now
      setScenarios(data || []);
    } catch (error) {
      console.error('Failed to load scenarios:', error);
      setError('Failed to load scenarios. Please try again.');
    } finally {
      setLoading(false);
    }
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
        <Typography color="error" sx={{ my: 2 }}>{error}</Typography>
      ) : filteredScenarios.length === 0 ? (
        <Typography sx={{ my: 2 }}>No scenarios found. Create a new one!</Typography>
      ) : (
        filteredScenarios.map((name, index) => (
          <Card
            key={index}
            sx={{ mb: 2, p: 2, cursor: 'pointer' }}
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