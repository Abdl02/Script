import React, { useState, useEffect } from 'react';
import { APIRequest } from 'types/models';
import { 
  Box, 
  Accordion, 
  AccordionSummary, 
  AccordionDetails, 
  Typography, 
  IconButton, 
  Tooltip, 
  Tabs, 
  Tab, 
  Snackbar, 
  Alert 
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { api } from 'api/client';
import { RequestBasicInfo, RequestBodyEditor, RequestAdvancedOptions } from './RequestEditor';
import { getEndpointType } from '../utils/form/fieldUtils';

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
  const [showBodyEditor, setShowBodyEditor] = useState(!!request.body || ['POST', 'PUT', 'PATCH'].includes(request.method));
  const [templateName, setTemplateName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error' | 'info'>('info');
  const [urlSuggestions, setUrlSuggestions] = useState<string[]>([]);
  const [isLoadingUrlSuggestions, setIsLoadingUrlSuggestions] = useState(false);

  const httpMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'];



  useEffect(() => {
    const loadTemplates = async () => {
      if (!request.url) return;
      try {
        setLoading(true);
        const endpointType = getEndpointType(request.url);
        // console.log(`EnhancedRequestEditor: Loading templates for endpointType: ${endpointType} from URL: ${request.url}`);
        const templates = await api.getBodyTemplates(endpointType);
        setBodyTemplates(templates || {}); // Ensure bodyTemplates is an object
        setError(null);
      } catch (error) {
        console.error('Failed to load body templates:', error);
        setError('Failed to load templates. Please try again.');
        setBodyTemplates({}); // Reset to empty object on error
      } finally {
        setLoading(false);
      }
    };

    if (request.url) {
      loadTemplates();
    }
  }, [request.url]); // Reload templates when URL changes

  useEffect(() => {
    // Automatically show body editor if method requires a body and body is not yet defined
    if (['POST', 'PUT', 'PATCH'].includes(request.method) && !request.body) {
      onChange({ body: {} }); // Initialize body if not present
      if (!showBodyEditor) setShowBodyEditor(true);
    }
  }, [request.method, request.body, onChange, showBodyEditor]);

  // Load initial URL suggestions
  useEffect(() => {
    fetchUrlSuggestions('');
  }, []);

  const showSnackbar = (message: string, severity: 'success' | 'error' | 'info' = 'info') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const handleBodyUpdate = (newBody: any) => {
    onChange({ body: newBody });
  };

  const handleSaveTemplate = async () => {
    if (!templateName || !request.body || !request.url) {
        showSnackbar('Template name, body, and URL are required to save a template.', 'error');
        return;
    }

    try {
      setLoading(true);
      const endpointType = getEndpointType(request.url);
      await api.saveBodyTemplate(endpointType, templateName, request.body);
      const templates = await api.getBodyTemplates(endpointType); // Refresh templates
      setBodyTemplates(templates || {});
      setTemplateName(''); // Clear template name input
      setError(null);
      showSnackbar('Template saved successfully', 'success');
    } catch (error) {
      console.error('Failed to save template:', error);
      setError('Failed to save template. Please try again.');
      showSnackbar('Failed to save template', 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadTemplate = (templateKey: string) => {
    if (bodyTemplates && bodyTemplates[templateKey]) {
      onChange({ body: JSON.parse(JSON.stringify(bodyTemplates[templateKey])) }); // Deep copy
      if (!showBodyEditor) setShowBodyEditor(true);
      showSnackbar(`Template '${templateKey}' loaded`, 'success');
    } else {
      showSnackbar(`Template '${templateKey}' not found.`, 'error');
    }
  };

  const handleMethodChange = (method: string) => {
    const newData: Partial<APIRequest> = { method };
    if (['POST', 'PUT', 'PATCH'].includes(method)) {
      if (!request.body) newData.body = {}; // Initialize body if not present
      if (!showBodyEditor) setShowBodyEditor(true); // Show body editor for these methods
    } else {
      if (showBodyEditor) setShowBodyEditor(false); // Optionally hide for GET/DELETE etc.
    }
    onChange(newData);
  };

  const handleHeadersChange = (headerJson: string) => {
    try {
      const headers = JSON.parse(headerJson);
      onChange({ headers });
    } catch (err) {
      console.error('Invalid header JSON:', err);
      showSnackbar('Invalid JSON format for headers', 'error');
    }
  };

  // Helper function to get value at a path
  const getValueAtPath = (obj: any, path: string) => {
    if (!obj || !path) return undefined;

    const parts = path.split('.');
    let current = obj;

    for (const part of parts) {
      // Handle array notation like field[0]
      if (part.includes('[') && part.includes(']')) {
        const name = part.substring(0, part.indexOf('['));
        const index = parseInt(part.substring(part.indexOf('[') + 1, part.indexOf(']')));

        if (!current || !current[name] || !Array.isArray(current[name]) || index >= current[name].length) {
          return undefined;
        }
        current = current[name][index];
      } else {
        if (current === undefined || current === null || !(part in current)) {
          return undefined;
        }
        current = current[part];
      }
    }
    return current;
  };

  // Helper function to set a value at a specific path in an object
  const setValueAtPath = (obj: any, path: string, value: any) => {
    if (!path) return obj;

    const parts = path.split('.');
    let current = obj;

    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      if (part.includes('[') && part.includes(']')) {
        const name = part.substring(0, part.indexOf('['));
        const index = parseInt(part.substring(part.indexOf('[') + 1, part.indexOf(']')));

        if (!current[name]) current[name] = [];
        while (current[name].length <= index) {
          current[name].push({});
        }
        current = current[name][index];
      } else {
        if (typeof current[part] !== 'object' || current[part] === null) current[part] = {};
        current = current[part];
      }
    }

    const lastPart = parts[parts.length - 1];
    if (lastPart.includes('[') && lastPart.includes(']')) {
      const name = lastPart.substring(0, lastPart.indexOf('['));
      const index = parseInt(lastPart.substring(lastPart.indexOf('[') + 1, lastPart.indexOf(']')));

      if (!current[name] || !Array.isArray(current[name])) current[name] = [];
      while (current[name].length <= index) {
        current[name].push(null);
      }
      current[name][index] = value;
    } else {
      current[lastPart] = value;
    }
    return obj;
  };

  const getDefaultValueForType = (type: string) => {
    switch (type) {
      case 'string': return '';
      case 'number': case 'integer': return 0;
      case 'boolean': return false;
      case 'array': return [];
      case 'object': return {};
      default: return '';
    }
  };

  const fetchUrlSuggestions = async (inputValue: string) => {
    try {
      setIsLoadingUrlSuggestions(true);
      const suggestions = await api.getUrls(inputValue);
      setUrlSuggestions(suggestions || []);
    } catch (error) {
      console.error('Error fetching URL suggestions:', error);
      setUrlSuggestions([]);
    } finally {
      setIsLoadingUrlSuggestions(false);
    }
  };

  const fetchFields = async () => {
    try {
      if (!request.url) {
        showSnackbar('Please enter a URL first', 'error');
        return;
      }
      setLoading(true);
      setError(null);

      const endpointType = getEndpointType(request.url);
      // console.log(`EnhancedRequestEditor: Fetching fields for endpointType: ${endpointType} from URL: ${request.url}`);
      const response = await api.fetchBodyFields(endpointType, request.url); // Pass URL if API expects it

      if (response && response.fields && Array.isArray(response.fields) && response.fields.length > 0) {
        if (!showBodyEditor && ['POST', 'PUT', 'PATCH'].includes(request.method)) {
          setShowBodyEditor(true);
        }

        if (['POST', 'PUT', 'PATCH'].includes(request.method)) {
          let newBody = request.body ? { ...request.body } : {};

          response.fields.forEach((field: any) => {
            if (field.required && getValueAtPath(newBody, field.path) === undefined) {
              // setValueAtPath might create nested structures. Ensure it's robust.
              newBody = setValueAtPath(newBody, field.path, getDefaultValueForType(field.type));
            }
          });
          onChange({ body: newBody });
          showSnackbar(`${response.fields.length} fields fetched successfully`, 'success');
          if (tabValue !== 1) setTabValue(1); // Switch to body tab
        } else {
          showSnackbar(`${response.fields.length} fields retrieved but not applied (method is ${request.method})`, 'info');
        }
      } else {
        showSnackbar(response.message || 'No fields returned from server or fields array is empty/invalid.', 'info');
      }
    } catch (error: any) {
      console.error('Error fetching fields:', error);
      setError(`Failed to fetch fields: ${error.message || 'Please try again.'}`);
      showSnackbar(`Failed to fetch fields: ${error.message || 'Check console.'}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Accordion expanded={expanded} onChange={() => setExpanded(!expanded)} sx={{ mb: 2, boxShadow: 3 }}>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
          <Typography variant="h6">
            {index + 1}. {request.name || "New Request"}
            <Typography component="span" variant="subtitle2" sx={{ ml: 1, color: 'text.secondary' }}>
              {request.method} {request.url && `- ${request.url.split('/').pop()?.split('?')[0]}`}
            </Typography>
          </Typography>
          <Box onClick={(e) => e.stopPropagation()}>
            <Tooltip title="Duplicate Request">
              <IconButton onClick={onDuplicate} size="small">
                <ContentCopyIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Remove Request">
              <IconButton color="error" onClick={onRemove} size="small">
                <DeleteIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </AccordionSummary>

      <AccordionDetails sx={{ backgroundColor: '#f9f9f9' }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)} sx={{ mb: 2 }} indicatorColor="primary" textColor="primary">
          <Tab label="Basic" />
          <Tab label="Body" disabled={!['POST', 'PUT', 'PATCH'].includes(request.method || '')} />
          {showAdvanced && <Tab label="Advanced" />}
        </Tabs>

        {tabValue === 0 && (
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <TextField fullWidth label="Request Name" value={request.name || ''} onChange={(e) => onChange({ name: e.target.value })} placeholder="E.g., Create API" required />
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>Method</InputLabel>
                <Select value={request.method || 'GET'} label="Method" onChange={(e) => handleMethodChange(e.target.value)}>
                  {httpMethods.map(method => (<MenuItem key={method} value={method}>{method}</MenuItem>))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField fullWidth label="Save Response As" value={request.save_as || ''} onChange={(e) => onChange({ save_as: e.target.value })} placeholder="E.g., api_response" helperText="Variable name for response" />
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-start' }}>
                <Autocomplete
                  freeSolo
                  fullWidth
                  options={urlSuggestions}
                  value={request.url || ''}
                  onInputChange={(_, newValue) => {
                    onChange({ url: newValue });
                    if (newValue && newValue.length > 1) { // Fetch suggestions on more input
                      fetchUrlSuggestions(newValue);
                    } else if (!newValue) {
                      fetchUrlSuggestions(''); // Fetch initial/all suggestions if cleared
                    }
                  }}
                  loading={isLoadingUrlSuggestions}
                  renderInput={(params) => (
                    <TextField {...params} label="URL" placeholder="e.g., /api-specs or http://..." helperText={<>Use <code>{'{variable}'}</code> or <code>${'{variable.property}'}</code></>} required />
                  )}
                />
                <Button variant="outlined" onClick={fetchFields} disabled={loading || !request.url} startIcon={<RefreshIcon />} sx={{ minWidth: '100px', height: '56px' }}>Fetch Fields</Button>
              </Box>
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel control={<Switch checked={showAdvanced} onChange={(e) => setShowAdvanced(e.target.checked)} />} label="Show Advanced Options" />
            </Grid>
          </Grid>
        )}

        {tabValue === 1 && ['POST', 'PUT', 'PATCH'].includes(request.method || '') && (
          <Box>
            <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'center' }}>
              <Button variant="outlined" onClick={() => setShowBodyEditor(!showBodyEditor)}>
                {showBodyEditor ? 'Hide Body Editor' : 'Show Body Editor'}
              </Button>

              {Object.keys(bodyTemplates).length > 0 && (
                <FormControl sx={{ minWidth: 200 }} size="small">
                  <InputLabel>Load Template</InputLabel>
                  <Select value="" onChange={(e) => { if (e.target.value) { loadTemplate(e.target.value as string); } }} label="Load Template">
                    <MenuItem value="" disabled><em>Select a template</em></MenuItem>
                    {Object.keys(bodyTemplates).map(name => (<MenuItem key={name} value={name}>{name}</MenuItem>))}
                  </Select>
                </FormControl>
              )}

              {request.body && (
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                  <TextField size="small" label="Save as Template Name" value={templateName} onChange={(e) => setTemplateName(e.target.value)} placeholder="E.g., My API Spec" />
                  <Button variant="outlined" startIcon={<SaveIcon />} onClick={handleSaveTemplate} disabled={!templateName || loading}>Save</Button>
                </Box>
              )}
            </Box>

            {error && (<Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>)}

            {showBodyEditor && request.url && (
              <FieldSelector
                endpointType={getEndpointType(request.url)}
                value={request.body || {}}
                onChange={handleBodyUpdate}
                availableRefs={availableRefs}
              />
            )}
             {!request.url && showBodyEditor && (
                <Alert severity="warning" sx={{ mb: 2 }}>
                    Please enter a URL first to determine the correct fields for the body editor.
                </Alert>
            )}


            {request.body && Object.keys(request.body).length > 0 && (
              <Box sx={{ mt: 2, p: 1, border: '1px solid #ddd', borderRadius: 1, backgroundColor: 'white' }}>
                <Typography variant="subtitle2" gutterBottom>Request Body Preview:</Typography>
                <JsonView value={request.body} displayDataTypes={false} style={{ backgroundColor: 'transparent', padding: '10px' }} collapsed={2}/>
              </Box>
            )}
          </Box>
        )}

        {tabValue === 2 && showAdvanced && ( // Changed tabValue to 2 for Advanced
          <Box>
            <Typography variant="subtitle1" gutterBottom>Advanced Options</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField fullWidth label="Custom Headers (JSON)" multiline rows={4} value={request.headers ? JSON.stringify(request.headers, null, 2) : '{}'} onChange={(e) => handleHeadersChange(e.target.value)} placeholder='{\n  "Content-Type": "application/json",\n  "X-Custom-Header": "value"\n}' />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel control={
                  <Switch
                    checked={!!(request.headers && request.headers.Authorization)}
                    onChange={(e) => {
                      const currentHeaders = request.headers ? { ...request.headers } : {};
                      if (e.target.checked) {
                        currentHeaders.Authorization = 'Bearer ${token}'; // Example token placeholder
                      } else {
                        delete currentHeaders.Authorization;
                      }
                      onChange({ headers: currentHeaders });
                    }}
                  />
                } label="Use Authorization Header (Bearer Token)" />
              </Grid>
              {/* TODO: Add assertion editor here if needed */}
            </Grid>
          </Box>
        )}
      </AccordionDetails>

      <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={() => setSnackbarOpen(false)} anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}>
        <Alert severity={snackbarSeverity} onClose={() => setSnackbarOpen(false)} sx={{ width: '100%' }}>{snackbarMessage}</Alert>
      </Snackbar>
    </Accordion>
  );
};
