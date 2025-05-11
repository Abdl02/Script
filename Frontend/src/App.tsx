import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Container, AppBar, Toolbar, Typography, Box,
         Drawer, List, ListItem, ListItemIcon, ListItemText, Divider,
         IconButton, Snackbar, Alert } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import SettingsIcon from '@mui/icons-material/Settings';
import MenuIcon from '@mui/icons-material/Menu';
import { ScenarioList } from 'components/ScenarioList';
import { ScenarioForm } from 'components/ScenarioForm';
import { EnvironmentSelector } from 'components/EnvironmentSelector';
import { api } from 'api/client';
import type { TestScenario } from 'types/models';
import ScenarioResults from './components/ScenarioResults';

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
  const [view, setView] = useState<'list' | 'create' | 'edit' | 'settings'>('list');
  const [selectedScenario, setSelectedScenario] = useState<TestScenario | undefined>(undefined);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [environment, setEnvironment] = useState('localDev');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' as 'info' | 'success' | 'error' });
  const [scenarioResults, setScenarioResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const showSnackbar = (message: string, severity: 'info' | 'success' | 'error' = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleSelectScenario = async (name: string) => {
    try {
      const scenario = await api.getScenario(name);
      setSelectedScenario(scenario);
      setView('edit');
    } catch (error) {
      console.error('Failed to load scenario:', error);
      showSnackbar('Failed to load scenario', 'error');
    }
  };

  const handleSaveScenario = async (scenario: Partial<TestScenario>) => {
    try {
      await api.createScenario(scenario);
      setView('list');
      setSelectedScenario(undefined);
      showSnackbar('Scenario saved successfully', 'success');
    } catch (error) {
      console.error('Failed to save scenario:', error);
      showSnackbar('Failed to save scenario', 'error');
    }
  };

  const handleRunScenario = async () => {
    if (!selectedScenario) {
      showSnackbar('No scenario selected', 'error');
      return;
    }

    setLoading(true); // Set loading to true
    try {
      const result = await api.runScenario(selectedScenario.name, environment);
      setScenarioResults(result);
      showSnackbar('Scenario executed successfully', 'success');
    } catch (error) {
      console.error('Failed to run scenario:', error);
      showSnackbar('Failed to run scenario', 'error');
    } finally {
      setLoading(false); // Set loading to false
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex' }}>
        <AppBar position="fixed">
          <Toolbar>
            <IconButton
              color="inherit"
              edge="start"
              onClick={() => setDrawerOpen(!drawerOpen)}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              APIFlow: Test Scenario System
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography variant="body2" sx={{ mr: 2 }}>
                Environment: {environment}
              </Typography>
            </Box>
          </Toolbar>
        </AppBar>

        <Drawer
          anchor="left"
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
        >
          <Box sx={{ width: 250 }} role="presentation">
            <List>
              <ListItem button onClick={() => { setView('list'); setDrawerOpen(false); }}>
                <ListItemIcon><DashboardIcon /></ListItemIcon>
                <ListItemText primary="Scenarios" />
              </ListItem>
              <ListItem button onClick={() => { setView('settings'); setDrawerOpen(false); }}>
                <ListItemIcon><SettingsIcon /></ListItemIcon>
                <ListItemText primary="Settings" />
              </ListItem>
            </List>
            <Divider />
            <List>
              {selectedScenario && (
                <ListItem button onClick={() => { handleRunScenario(); setDrawerOpen(false); }}>
                  <ListItemIcon><PlayArrowIcon /></ListItemIcon>
                  <ListItemText primary="Run Scenario" />
                </ListItem>
              )}
            </List>
          </Box>
        </Drawer>

        <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
          {view === 'settings' && (
            <Box>
              <Typography variant="h4" gutterBottom>Settings</Typography>
              <EnvironmentSelector
                value={environment}
                onChange={setEnvironment}
              />
            </Box>
          )}

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
                setSelectedScenario(undefined);
              }}
              onRun={handleRunScenario}
              environment={environment}
            />
          )}
        </Box>
        {scenarioResults && (
        <Box
          sx={{
            position: 'fixed',
            bottom: 16,
            right: 16,
            zIndex: 1300, // Ensures it appears above other elements
            boxShadow: 3,
            borderRadius: 2,
            backgroundColor: 'background.paper',
          }}
        >
          <ScenarioResults results={scenarioResults} loading={loading} />
        </Box>
      )}
      </Box>
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
}

export default App;