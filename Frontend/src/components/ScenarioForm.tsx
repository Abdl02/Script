// src/components/ScenarioForm.tsx
import React, { useState } from 'react';
import { TestScenario, APIRequest } from 'types/models';
import { TextField, Button, Box, Grid, Typography, Paper, Alert, Snackbar } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { RequestEditor } from './RequestEditor';
import { validateScenario } from 'utils/validation';

interface ScenarioFormProps {
  scenario?: TestScenario;
  onSave: (scenario: Partial<TestScenario>) => void;
  onCancel: () => void;
  onRun?: () => void;
  environment?: string; // Added environment prop with optional flag
}

export const ScenarioForm: React.FC<ScenarioFormProps> = ({
  scenario, onSave, onCancel, onRun, environment = 'localDev' // Default value provided
}) => {
  const [formData, setFormData] = useState<Partial<TestScenario>>(
    scenario || {
      name: '',
      id: '',
      description: '',
      version: '1.0.0',
      requests: []
    }
  );
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  const handleChange = (field: keyof TestScenario, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const addRequest = () => {
    const newRequest: APIRequest = {
      name: `Request ${(formData.requests?.length || 0) + 1}`,
      method: 'GET',
      url: '',
      headers: {},
      body: null,
      assertions: [{
        type: 'status_code',
        value: '200'
      }]
    };
    setFormData(prev => ({
      ...prev,
      requests: [...(prev.requests || []), newRequest]
    }));
  };

  const updateRequest = (index: number, updated: Partial<APIRequest>) => {
    const requests = [...(formData.requests || [])];
    requests[index] = { ...requests[index], ...updated };
    setFormData(prev => ({ ...prev, requests }));
  };

  const removeRequest = (index: number) => {
    const requests = [...(formData.requests || [])];
    requests.splice(index, 1);
    setFormData(prev => ({ ...prev, requests }));
  };

  const handleSubmit = () => {
    // Validate scenario before submitting
    const errors = validateScenario(formData);
    if (errors.length > 0) {
      setValidationErrors(errors);
      return;
    }

    const finalData = {
      ...formData,
      created_at: formData.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    try {
      onSave(finalData);
      setSnackbarMessage('Scenario saved successfully');
      setSnackbarOpen(true);
    } catch (error) {
      console.error('Error saving scenario:', error);
      setSnackbarMessage('Failed to save scenario');
      setSnackbarOpen(true);
    }
  };

  // Get available references for each request
  const getAvailableRefsForIndex = (index: number): string[] => {
    return formData.requests
      ?.slice(0, index)
      .map(r => r.save_as)
      .filter((name): name is string => name !== undefined) || [];
  };

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          {scenario ? 'Edit Scenario' : 'Create New Scenario'}
        </Typography>

        {validationErrors.length > 0 && (
          <Alert severity="error" sx={{ mb: 2 }}>
            <Typography variant="subtitle1">Please fix the following errors:</Typography>
            <ul>
              {validationErrors.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
          </Alert>
        )}

        <Grid container spacing={3}>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="Scenario Name"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              required
            />
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="ID"
              value={formData.id}
              onChange={(e) => handleChange('id', e.target.value)}
              placeholder="Generated automatically if empty"
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Description"
              multiline
              rows={2}
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
            />
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="Version"
              value={formData.version}
              onChange={(e) => handleChange('version', e.target.value)}
            />
          </Grid>
          {environment && (
            <Grid item xs={6}>
              <Typography variant="body1">
                Environment: <strong>{environment}</strong>
              </Typography>
              <Typography variant="body2" color="textSecondary">
                You can change the environment in Settings
              </Typography>
            </Grid>
          )}
        </Grid>
      </Paper>

      <Typography variant="h5" sx={{ mt: 4, mb: 2 }}>
        Requests
        <Typography variant="body2" component="span" sx={{ ml: 2, color: 'text.secondary' }}>
          Define the API requests in your test scenario
        </Typography>
      </Typography>

      {formData.requests?.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center', backgroundColor: '#f5f5f5' }}>
          <Typography color="textSecondary" sx={{ mb: 2 }}>
            No requests added yet. Add your first request to build your scenario.
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={addRequest}
          >
            Add First Request
          </Button>
        </Paper>
      ) : (
        <>
          {formData.requests?.map((request, index) => (
            <RequestEditor
              key={index}
              index={index}
              request={request}
              onChange={(updated) => updateRequest(index, updated)}
              onRemove={() => removeRequest(index)}
              availableRefs={getAvailableRefsForIndex(index)}
            />
          ))}

          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={addRequest}
            sx={{ mt: 2 }}
          >
            Add Request
          </Button>
        </>
      )}

      <Box sx={{ mt: 4, display: 'flex', gap: 2 }}>
        <Button variant="contained" color="primary" onClick={handleSubmit}>
          Save Scenario
        </Button>
        <Button variant="outlined" onClick={onCancel}>
          Cancel
        </Button>
        {scenario && onRun && (
          <Button
            variant="contained"
            color="secondary"
            onClick={onRun}
            disabled={!scenario.name}
          >
            Run Scenario
          </Button>
        )}
      </Box>

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
      />
    </Box>
  );
};