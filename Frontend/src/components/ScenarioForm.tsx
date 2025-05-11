import React, { useState, useEffect } from 'react';
import { TestScenario, APIRequest } from 'types/models';
import {
  TextField, Button, Box, Grid, Typography, Paper, Alert, Snackbar,
  Dialog, DialogTitle, DialogContent, DialogActions, CircularProgress
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { EnhancedRequestEditor } from './EnhancedRequestEditor';

interface ScenarioFormProps {
  scenario?: TestScenario;
  onSave: (scenario: Partial<TestScenario>) => void;
  onCancel: () => void;
  onRun?: () => void;
  environment?: string;
}

export const ScenarioForm: React.FC<ScenarioFormProps> = ({
  scenario, onSave, onCancel, onRun, environment = 'localDev'
}) => {
  const [formData, setFormData] = useState<Partial<TestScenario>>(
    scenario || {
      name: '',
      id: `id_${Date.now()}`,
      description: '',
      version: '1.0.0',
      requests: []
    }
  );
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error' | 'info'>('info');
  const [loading, setLoading] = useState(false);
  const [debug, setDebug] = useState<any>(null);
  const [showDebug, setShowDebug] = useState(false);

  useEffect(() => {
    if (scenario) {
      setFormData({
        ...scenario,
        requests: scenario.requests ? [...scenario.requests] : []
      });
    }
  }, [scenario]);

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

  const duplicateRequest = (index: number) => {
    const requests = [...(formData.requests || [])];
    const originalRequest = requests[index];
    const duplicatedRequest = {
      ...JSON.parse(JSON.stringify(originalRequest)),
      name: `${originalRequest.name} (Copy)`
    };
    requests.splice(index + 1, 0, duplicatedRequest);
    setFormData(prev => ({ ...prev, requests }));
  };

  const validateForm = (): string[] => {
    const errors: string[] = [];

    if (!formData.name) errors.push('Scenario name is required');

    if (formData.requests && formData.requests.length > 0) {
      formData.requests.forEach((request, index) => {
        if (!request.name) errors.push(`Request ${index + 1}: Name is required`);
        if (!request.method) errors.push(`Request ${index + 1}: Method is required`);
        if (!request.url) errors.push(`Request ${index + 1}: URL is required`);
      });
    }

    return errors;
  };

  const handleSubmit = async () => {
    const errors = validateForm();
    if (errors.length > 0) {
      setValidationErrors(errors);
      setSnackbarMessage('Please fix validation errors');
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
      return;
    }

    setValidationErrors([]);
    setLoading(true);

    try {
      const preparedRequests = formData.requests?.map(request => {
        // Make sure body is properly initialized for POST/PUT requests
        if ((['POST', 'PUT', 'PATCH'].includes(request.method || '')) && !request.body) {
          return { ...request, body: {} };
        }
        return request;
      }) || [];

      const finalData = {
        ...formData,
        id: formData.id || `id_${formData.name}_${Date.now()}`,
        description: formData.description || `Scenario for ${formData.name}`,
        version: formData.version || '1.0.0',
        created_at: formData.created_at || new Date().toISOString(),
        updated_at: new Date().toISOString(),
        requests: preparedRequests
      };

      console.log('Submitting scenario data:', finalData);

      await onSave(finalData);

      setSnackbarMessage('Scenario saved successfully');
      setSnackbarSeverity('success');
      setSnackbarOpen(true);
    } catch (error) {
      console.error('Error saving scenario:', error);
      setDebug(error);
      setSnackbarMessage('Failed to save scenario. Please check the console for details.');
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    } finally {
      setLoading(false);
    }
  };

  const getAvailableRefsForIndex = (index: number): string[] => {
    return formData.requests
      ?.slice(0, index)
      .map(r => r.save_as)
      .filter((name): name is string => name !== undefined) || [];
  };

  const closeDebug = () => {
    setShowDebug(false);
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
              value={formData.name || ''}
              onChange={(e) => handleChange('name', e.target.value)}
              required
              error={!formData.name}
              helperText={!formData.name ? "Name is required" : ""}
            />
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              label="ID"
              value={formData.id || ''}
              onChange={(e) => handleChange('id', e.target.value)}
              placeholder="Generated automatically if empty"
              disabled={!!scenario} // Disable editing ID for existing scenarios
            />
          </Grid>
        </Grid>
      </Paper>

      <Typography variant="h5" sx={{ mt: 4, mb: 2 }}>
        Requests
        <Typography variant="body2" component="span" sx={{ ml: 2, color: 'text.secondary' }}>
          Define the API requests in your test scenario
        </Typography>
      </Typography>

      {!formData.requests?.length ? (
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
          {formData.requests.map((request, index) => (
            <EnhancedRequestEditor
              key={index}
              index={index}
              request={request}
              onChange={(updated) => updateRequest(index, updated)}
              onRemove={() => removeRequest(index)}
              onDuplicate={() => duplicateRequest(index)}
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
        <Button
          variant="contained"
          color="primary"
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Save Scenario'}
        </Button>
        <Button variant="outlined" onClick={onCancel}>
          Cancel
        </Button>
        {scenario && onRun && (
          <Button
            variant="contained"
            color="secondary"
            onClick={onRun}
            disabled={!scenario.name || loading}
          >
            Run Scenario
          </Button>
        )}
        {debug && (
          <Button
            variant="outlined"
            color="error"
            onClick={() => setShowDebug(true)}
          >
            Show Error Details
          </Button>
        )}
      </Box>

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert severity={snackbarSeverity} onClose={() => setSnackbarOpen(false)}>
          {snackbarMessage}
        </Alert>
      </Snackbar>

      <Dialog open={showDebug} onClose={closeDebug} maxWidth="md" fullWidth>
        <DialogTitle>Error Details</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle1">Error Object:</Typography>
            <pre style={{ overflow: 'auto', maxHeight: '400px' }}>
              {JSON.stringify(debug, null, 2)}
            </pre>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeDebug}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};