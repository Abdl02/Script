import React, { useState, useEffect } from 'react';
import { APIRequest, Assertion } from '../types/models';
import { Card, Typography, TextField, Select, MenuItem, IconButton, FormControl, InputLabel, Box, Button, Grid } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { FieldSelector } from './FieldSelector';

interface RequestEditorProps {
  request: APIRequest;
  onChange: (request: Partial<APIRequest>) => void;
  onRemove: () => void;
  availableNames: string[];
}

export const RequestEditor: React.FC<RequestEditorProps> = ({ request, onChange, onRemove, availableNames }) => {
  const [showBodyEditor, setShowBodyEditor] = useState(!!request.body);

  const httpMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'];

  const handleBodyUpdate = (body: any) => {
    onChange({ body });
  };

  const addAssertion = () => {
    const newAssertions = [...(request.assertions || []), {
      type: 'status_code',
      value: '200'
    }];
    onChange({ assertions: newAssertions });
  };

  const updateAssertion = (index: number, updated: Partial<Assertion>) => {
    const assertions = [...(request.assertions || [])];
    assertions[index] = { ...assertions[index], ...updated };
    onChange({ assertions });
  };

  const removeAssertion = (index: number) => {
    const assertions = [...(request.assertions || [])];
    assertions.splice(index, 1);
    onChange({ assertions });
  };

  return (
    <Card sx={{ mb: 3, p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Request Configuration</Typography>
        <IconButton color="error" onClick={onRemove}>
          <DeleteIcon />
        </IconButton>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={4}>
          <TextField
            fullWidth
            label="Request Name"
            value={request.name}
            onChange={(e) => onChange({ name: e.target.value })}
          />
        </Grid>
        <Grid item xs={4}>
          <FormControl fullWidth>
            <InputLabel>Method</InputLabel>
            <Select
              value={request.method}
              label="Method"
              onChange={(e) => onChange({ method: e.target.value })}
            >
              {httpMethods.map(method => (
                <MenuItem key={method} value={method}>{method}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={4}>
          <TextField
            fullWidth
            label="Save As"
            value={request.save_as || ''}
            onChange={(e) => onChange({ save_as: e.target.value })}
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="URL"
            value={request.url}
            onChange={(e) => onChange({ url: e.target.value })}
            placeholder="https://api.example.com/endpoint"
          />
        </Grid>
      </Grid>

      {(request.method === 'POST' || request.method === 'PUT' || request.method === 'PATCH') && (
        <Box sx={{ mt: 2 }}>
          <Button
            variant="outlined"
            onClick={() => setShowBodyEditor(!showBodyEditor)}
            sx={{ mb: 2 }}
          >
            {showBodyEditor ? 'Hide Body Editor' : 'Show Body Editor'}
          </Button>

          {showBodyEditor && (
            <FieldSelector
              endpointType={request.url.split('/')[3] || 'api-specs'}
              value={request.body}
              onChange={handleBodyUpdate}
              availableRefs={availableNames}
            />
          )}
        </Box>
      )}

      <Typography variant="subtitle1" sx={{ mt: 3, mb: 1 }}>
        Assertions
      </Typography>

      {request.assertions?.map((assertion, index) => (
        <Box key={index} sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Type</InputLabel>
            <Select
              value={assertion.type}
              label="Type"
              onChange={(e) => updateAssertion(index, { type: e.target.value as Assertion['type'] })}
            >
              <MenuItem value="status_code">Status Code</MenuItem>
              <MenuItem value="json_path">JSON Path</MenuItem>
              <MenuItem value="response_body_contains">Body Contains</MenuItem>
            </Select>
          </FormControl>

          <TextField
            label="Expected Value"
            value={assertion.value}
            onChange={(e) => updateAssertion(index, { value: e.target.value })}
          />

          {assertion.type === 'json_path' && (
            <TextField
              label="JSON Path"
              value={assertion.path || ''}
              onChange={(e) => updateAssertion(index, { path: e.target.value })}
            />
          )}

          <IconButton color="error" onClick={() => removeAssertion(index)}>
            <DeleteIcon />
          </IconButton>
        </Box>
      ))}

      <Button variant="outlined" size="small" onClick={addAssertion}>
        Add Assertion
      </Button>
    </Card>
  );
};