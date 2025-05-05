import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Container, AppBar, Toolbar, Typography, Box } from '@mui/material';
import { ScenarioList } from '@components/ScenarioList';
import { ScenarioForm } from '@components/ScenarioForm';
import { api } from '@api/client';
import type { TestScenario } from 'types/models';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [view, setView] = useState<'list' | 'create' | 'edit'>('list');
  const [selectedScenario, setSelectedScenario] = useState<TestScenario | null>(null);

  const handleSelectScenario = async (name: string) => {
    try {
      const scenario = await api.getScenario(name);
      setSelectedScenario(scenario);
      setView('edit');
    } catch (error) {
      console.error('Failed to load scenario:', error);
    }
  };

  const handleSaveScenario = async (scenario: Partial<TestScenario>) => {
    try {
      await api.createScenario(scenario);
      setView('list');
      setSelectedScenario(null);
    } catch (error) {
      console.error('Failed to save scenario:', error);
    }
  };

  const handleRunScenario = async () => {
    if (selectedScenario) {
      try {
        const result = await api.runScenario(selectedScenario.name);
        console.log('Scenario run result:', result);
        // Handle result display
      } catch (error) {
        console.error('Failed to run scenario:', error);
      }
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="sticky">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            APIFlow: Test Scenario System
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {view === 'list' && (
          <ScenarioList
            onSelect={handleSelectScenario}
            onNew={() => setView('create')}
          />
        )}

        {(view === 'create' || view === 'edit') && (
          <ScenarioForm
            scenario={selectedScenario}
            onSave={handleSaveScenario}
            onCancel={() => {
              setView('list');
              setSelectedScenario(null);
            }}
            onRun={handleRunScenario}
          />
        )}
      </Container>
    </ThemeProvider>
  );
}

export default App;