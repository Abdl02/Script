import React, { useState, useEffect } from 'react';
import { TestScenario, APIRequest } from 'types/models';
import { TextField, Button, IconButton, Select, MenuItem, FormControl, InputLabel, Box, Grid, Typography } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import { FieldSelector } from './FieldSelector';
import { api } from 'api/client';
import { RequestEditor } from "components/RequestEditor";

interface ScenarioFormProps {
  scenario?: TestScenario;
  onSave: (scenario: Partial<TestScenario>) => void;
  onCancel: () => void;
  onRun: () => void;
}

export const ScenarioForm: React.FC<ScenarioFormProps> = ({ scenario, onSave, onCancel, onRun }) => {
  const [formData, setFormData] = useState<Partial<TestScenario>>(
    scenario || {
      name: '',
      id: '',
      description: '',
      version: '1.0.0',
      requests: []
    }
  );

  const handleChange = (field: keyof TestScenario, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const addRequest = () => {
    const newRequest: APIRequest = {
      name: '',
      method: 'GET',
      url: '',
      headers: {},
      body: null,
      assertions: []
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

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        {scenario ? 'Edit Scenario' : 'Create New Scenario'}
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={6}>
          <TextField
            fullWidth
            label="Scenario Name"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
          />
        </Grid>
        <Grid item xs={6}>
          <TextField
            fullWidth
            label="ID"
            value={formData.id}
            onChange={(e) => handleChange('id', e.target.value)}
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
      </Grid>

      <Typography variant="h5" sx={{ mt: 4, mb: 2 }}>
        Requests
      </Typography>

      {formData.requests?.map((request, index) => (
        <RequestEditor
          key={index}
          request={request}
          onChange={(updated) => updateRequest(index, updated)}
          onRemove={() => removeRequest(index)}
          // Fix the available names by filtering out undefined values
          availableNames={formData.requests
            ?.filter((_, i) => i < index)
            .map(r => r.save_as)
            .filter((name): name is string => name !== undefined) || []}
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

      <Box sx={{ mt: 4, display: 'flex', gap: 2 }}>
        <Button variant="contained" color="primary" onClick={() => onSave(formData)}>
          Save
        </Button>
        <Button variant="outlined" onClick={onCancel}>
          Cancel
        </Button>
        {scenario && (
          <Button variant="contained" color="secondary" onClick={onRun}>
            Run
          </Button>
        )}
      </Box>
    </Box>
  );
};