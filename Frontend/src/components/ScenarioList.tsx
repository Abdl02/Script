import React, { useState, useEffect } from 'react';
import { api } from 'api/client';
import { Card, TextField, Button, Box, Typography } from '@mui/material';

interface ScenarioListProps {
  onSelect: (name: string) => void;
  onNew: () => void;
}

export const ScenarioList: React.FC<ScenarioListProps> = ({ onSelect, onNew }) => {
  const [scenarios, setScenarios] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadScenarios();
  }, []);

  const loadScenarios = async () => {
    try {
      const data = await api.getScenarios();
      setScenarios(data);
    } catch (error) {
      console.error('Failed to load scenarios:', error);
    }
  };

  const filteredScenarios = scenarios.filter(name =>
    name.toLowerCase().includes(searchTerm.toLowerCase())
  );

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

      {filteredScenarios.map((name, index) => (
        <Card
          key={index}
          sx={{ mb: 2, p: 2, cursor: 'pointer' }}
          onClick={() => onSelect(name)}
        >
          <Typography variant="h6">{name}</Typography>
        </Card>
      ))}

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