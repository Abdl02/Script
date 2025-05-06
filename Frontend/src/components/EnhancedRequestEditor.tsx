import React, { useState, useEffect } from 'react';
import { APIRequest, Assertion } from 'types/models';
import { Card, Typography, TextField, Select, MenuItem, IconButton, FormControl,
         InputLabel, Box, Button, Grid, Accordion, AccordionSummary,
         AccordionDetails, Switch, FormControlLabel, Tabs, Tab, Tooltip, Alert } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import SaveIcon from '@mui/icons-material/Save';
import JsonView from '@uiw/react-json-view';
import { FieldSelector } from './FieldSelector';
import { api } from 'api/client';

interface EnhancedRequestEditorProps {
  request: APIRequest;
  onChange: (request: Partial<APIRequest>) => void;
  onRemove: () => void;
  onDuplicate: () => void;
  availableRefs: string[];
  index: number;
}

export const EnhancedRequestEditor: React.FC<EnhancedRequestEditorProps> = ({
  request, onChange, onRemove, onDuplicate, availableRefs, index
}) => {
  const [expanded, setExpanded] = useState(true);
  const [bodyTemplates, setBodyTemplates] = useState<Record<string, any>>({});
  const [tabValue, setTabValue] = useState(0);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showBodyEditor, setShowBodyEditor] = useState(!!request.body);
  const [templateName, setTemplateName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const httpMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'];

  useEffect(() => {
    const loadTemplates = async () => {
      try {
        setLoading(true);
        const endpointType = getEndpointType(request.url);
        const templates = await api.getBodyTemplates(endpointType);
        setBodyTemplates(templates);
        setError(null);
      } catch (error) {
        console.error('Failed to load body templates:', error);
        setError('Failed to load templates. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    if (request.url) {
      loadTemplates();
    }
  }, [request.url]);

  useEffect(() => {
    if (['POST', 'PUT', 'PATCH'].includes(request.method) && !request.body) {
      onChange({ body: {} });
    }
  }, [request.method]);

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

  const handleSaveTemplate = async () => {
    if (!templateName || !request.body) return;

    try {
      setLoading(true);
      const endpointType = getEndpointType(request.url);
      await api.saveBodyTemplate(endpointType, templateName, request.body);
      const templates = await api.getBodyTemplates(endpointType);
      setBodyTemplates(templates);
      setTemplateName('');
      setError(null);
    } catch (error) {
      console.error('Failed to save template:', error);
      setError('Failed to save template. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadTemplate = (templateBody: any) => {
    onChange({ body: templateBody });
    setShowBodyEditor(true);
  };

  const getEndpointType = (url: string): string => {
    if (!url) return 'api-specs'; // Default

    try {
      const urlParts = url.split('/');
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

  const handleMethodChange = (method: string) => {
    const newData: Partial<APIRequest> = { method };
    if (['POST', 'PUT', 'PATCH'].includes(method) && !request.body) {
      newData.body = {};
      setShowBodyEditor(true);
    }
    onChange(newData);
  };

  const handleHeadersChange = (headerJson: string) => {
    try {
      const headers = JSON.parse(headerJson);
      onChange({ headers });
    } catch (err) {
      console.error('Invalid header JSON:', err);
    }
  };

  return (
    <Accordion expanded={expanded} onChange={() => setExpanded(!expanded)} sx={{ mb: 2 }}>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
          <Typography variant="h6">
            {index + 1}. {request.name || "New Request"}
            <Typography component="span" variant="subtitle2" sx={{ ml: 1 }}>
              {request.method} {request.url && `- ${request.url.split('/').pop()}`}
            </Typography>
          </Typography>
          <Box onClick={(e) => e.stopPropagation()}>
            <Tooltip title="Duplicate Request">
              <IconButton
                onClick={onDuplicate}
                size="small"
              >
                <ContentCopyIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Remove Request">
              <IconButton
                color="error"
                onClick={onRemove}
                size="small"
              >
                <DeleteIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </AccordionSummary>

      <AccordionDetails>
        <Tabs
          value={tabValue}
          onChange={(_, newValue) => setTabValue(newValue)}
          sx={{ mb: 2 }}
        >
          <Tab label="Basic" />
          <Tab label="Body" disabled={!['POST', 'PUT', 'PATCH'].includes(request.method || '')} />
          <Tab label="Assertions" />
          {showAdvanced && <Tab label="Advanced" />}
        </Tabs>

        {tabValue === 0 && (
          <Grid container spacing={2}>
            <Grid item xs={4}>
              <TextField
                fullWidth
                label="Request Name"
                value={request.name || ''}
                onChange={(e) => onChange({ name: e.target.value })}
                placeholder="E.g., Create API"
                required
              />
            </Grid>
            <Grid item xs={4}>
              <FormControl fullWidth>
                <InputLabel>Method</InputLabel>
                <Select
                  value={request.method || 'GET'}
                  label="Method"
                  onChange={(e) => handleMethodChange(e.target.value)}
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
                helperText={
                  <>
                    Use <code>{'{variable}'}</code> or <code>${'{variable.property}'}</code> for parameters
                  </>
                }
                required
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={showAdvanced}
                    onChange={(e) => setShowAdvanced(e.target.checked)}
                  />
                }
                label="Show Advanced Options"
              />
            </Grid>
          </Grid>
        )}

        {tabValue === 1 && ['POST', 'PUT', 'PATCH'].includes(request.method || '') && (
          <Box>
            <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
              <Button
                variant="outlined"
                onClick={() => setShowBodyEditor(!showBodyEditor)}
              >
                {showBodyEditor ? 'Hide Body Editor' : 'Show Body Editor'}
              </Button>

              {Object.keys(bodyTemplates).length > 0 && (
                <FormControl sx={{ minWidth: 200 }}>
                  <InputLabel>Load Template</InputLabel>
                  <Select
                    value=""
                    onChange={(e) => {
                      if (e.target.value) {
                        loadTemplate(bodyTemplates[e.target.value]);
                      }
                    }}
                    label="Load Template"
                  >
                    <MenuItem value="">Select a template</MenuItem>
                    {Object.keys(bodyTemplates).map(name => (
                      <MenuItem key={name} value={name}>{name}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}

              {request.body && (
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <TextField
                    size="small"
                    label="Template Name"
                    value={templateName}
                    onChange={(e) => setTemplateName(e.target.value)}
                    placeholder="E.g., My Template"
                  />
                  <Button
                    variant="outlined"
                    startIcon={<SaveIcon />}
                    onClick={handleSaveTemplate}
                    disabled={!templateName || loading}
                  >
                    Save
                  </Button>
                </Box>
              )}
            </Box>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            {showBodyEditor && (
              <FieldSelector
                endpointType={getEndpointType(request.url)}
                value={request.body || {}}
                onChange={handleBodyUpdate}
                availableRefs={availableRefs}
              />
            )}

            {request.body && Object.keys(request.body).length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Request Body Preview:
                </Typography>
                <JsonView
                  value={request.body}
                  displayDataTypes={false}
                  style={{
                    backgroundColor: 'transparent',
                    padding: '10px',
                    borderRadius: '4px',
                    border: '1px solid #ccc'
                  }}
                />
              </Box>
            )}
          </Box>
        )}

        {tabValue === 2 && (
          <Box>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>
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
          </Box>
        )}

        {tabValue === 3 && showAdvanced && (
          <Box>
            <Typography variant="subtitle1" gutterBottom>
              Advanced Options
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Custom Headers (JSON)"
                  multiline
                  rows={4}
                  value={request.headers ? JSON.stringify(request.headers, null, 2) : '{}'}
                  onChange={(e) => handleHeadersChange(e.target.value)}
                  placeholder='{"Content-Type": "application/json"}'
                />
              </Grid>

              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={!!request.headers?.Authorization}
                      onChange={(e) => {
                        const headers = { ...request.headers } || {};
                        if (e.target.checked) {
                          headers.Authorization = 'Bearer ${token}';
                        } else {
                          delete headers.Authorization;
                        }
                        onChange({ headers });
                      }}
                    />
                  }
                  label="Use Authorization"
                />
              </Grid>
            </Grid>
          </Box>
        )}
      </AccordionDetails>
    </Accordion>
  );
};