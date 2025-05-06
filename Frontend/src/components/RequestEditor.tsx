import React, { useState } from 'react';
import { APIRequest, Assertion } from 'types/models';
import { Card, Typography, TextField, Select, MenuItem, IconButton, FormControl,
         InputLabel, Box, Button, Grid, Accordion, AccordionSummary,
         AccordionDetails } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { FieldSelector } from './FieldSelector';

interface RequestEditorProps {
  request: APIRequest;
  onChange: (request: Partial<APIRequest>) => void;
  onRemove: () => void;
  availableRefs: string[];
  index: number;
}

export const RequestEditor: React.FC<RequestEditorProps> = ({
  request, onChange, onRemove, availableRefs, index
}) => {
  const [showBodyEditor, setShowBodyEditor] = useState(!!request.body);
  const [expanded, setExpanded] = useState(true);
  const httpMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'];

  const handleBodyUpdate = (body: any) => {
    onChange({ body });
  };

  const addAssertion = () => {
    const newAssertions: Assertion[] = [...(request.assertions || []), {
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

  // Extract endpoint type from URL for field selection
  const getEndpointType = (url: string): string => {
    if (!url) return 'api-specs'; // Default

    try {
      const urlParts = url.split('/');
      // Try to find parts after the base URL
      const apiPathIndex = urlParts.findIndex(part => part === 'api');

      if (apiPathIndex >= 0 && apiPathIndex + 1 < urlParts.length) {
        return urlParts[apiPathIndex + 1];
      }

      return urlParts[3] || 'api-specs';
    } catch (error) {
      console.error('Error extracting endpoint type:', error);
      return 'api-specs';
    }
  };

  return (
    <Accordion expanded={expanded} onChange={() => setExpanded(!expanded)}>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
          <Typography variant="h6">
            {index + 1}. {request.name || "New Request"}
            <Typography component="span" variant="subtitle2" sx={{ ml: 1 }}>
              {request.method} {request.url && `- ${request.url.split('/').pop()}`}
            </Typography>
          </Typography>
          <IconButton
            color="error"
            onClick={(e) => {
              e.stopPropagation();
              onRemove();
            }}
            size="small"
          >
            <DeleteIcon />
          </IconButton>
        </Box>
      </AccordionSummary>

      <AccordionDetails>
        <Grid container spacing={2}>
          <Grid item xs={4}>
            <TextField
              fullWidth
              label="Request Name"
              value={request.name || ''}
              onChange={(e) => onChange({ name: e.target.value })}
              placeholder="E.g., Create API"
            />
          </Grid>
          <Grid item xs={4}>
            <FormControl fullWidth>
              <InputLabel>Method</InputLabel>
              <Select
                value={request.method || 'GET'}
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
              label="Save Response As"
              value={request.save_as || ''}
              onChange={(e) => onChange({ save_as: e.target.value })}
              placeholder="E.g., api_response"
              helperText="Variable name to store response for reference"
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="URL"
              value={request.url || ''}
              onChange={(e) => onChange({ url: e.target.value })}
              placeholder="http://localhost:8099/api-specs/{id}"
              helperText="Use {variable} for path parameters"
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
                endpointType={getEndpointType(request.url)}
                value={request.body || {}}
                onChange={handleBodyUpdate}
                availableRefs={availableRefs}
              />
            )}
          </Box>
        )}

        <Typography variant="subtitle1" sx={{ mt: 3, mb: 1 }}>
          Assertions
        </Typography>

        {(request.assertions || []).map((assertion, index) => (
          <Box key={index} sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Type</InputLabel>
              <Select
                value={assertion.type || 'status_code'}
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
              value={assertion.value || ''}
              onChange={(e) => updateAssertion(index, { value: e.target.value })}
            />

            {assertion.type === 'json_path' && (
              <TextField
                label="JSON Path"
                value={assertion.path || ''}
                onChange={(e) => updateAssertion(index, { path: e.target.value })}
                placeholder="$.data.id"
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
      </AccordionDetails>
    </Accordion>
  );
};