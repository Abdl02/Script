import React, { useState, useEffect } from 'react';
import { api } from 'api/client';
import { Field } from 'types/models';
import {
  Box, Typography, Button, Chip, TextField, Dialog, DialogTitle,
  DialogContent, DialogActions, CircularProgress, Alert, FormControl,
  InputLabel, Select, MenuItem, Paper, Divider, Switch, FormControlLabel,
  IconButton, Tooltip, Snackbar
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import RefreshIcon from '@mui/icons-material/Refresh';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import ContentPasteIcon from '@mui/icons-material/ContentPaste';
import FileUploadIcon from '@mui/icons-material/FileUpload';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import DeleteIcon from "@mui/icons-material/Delete";

const getValueAtPath = (obj: any, path: string | undefined): any => {
  if (!path) return undefined;
  if (!obj) return undefined;

  return path.split('.').reduce((acc, part) => {
    if (!acc) return undefined;

    if (part.includes('[') && part.includes(']')) {
      const fieldName = part.split('[')[0];
      const index = parseInt(part.split('[')[1].replace(']', ''));
      return acc?.[fieldName]?.[index];
    }
    return acc?.[part];
  }, obj);
};

interface FieldSelectorProps {
  endpointType: string;
  value: any;
  onChange: (value: any) => void;
  availableRefs: string[];
}

export const FieldSelector: React.FC<FieldSelectorProps> = ({
  endpointType,
  value,
  onChange,
  availableRefs
}) => {
  const [fields, setFields] = useState<Field[]>([]);
  const [selectedFields, setSelectedFields] = useState<Set<string>>(new Set());
  const [showReferenceDialog, setShowReferenceDialog] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [showAllFields, setShowAllFields] = useState(false);
  const [customField, setCustomField] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error' | 'info'>('info');
  const [showJsonDialog, setShowJsonDialog] = useState(false);
  const [jsonDialogMode, setJsonDialogMode] = useState<'import' | 'export'>('export');
  const [jsonText, setJsonText] = useState('');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (endpointType) {
      loadFields();
    }
  }, [endpointType, retryCount]);

  useEffect(() => {
    if (value) {
      const fieldsToSelect = new Set<string>();

      const findFields = (obj: any, prefix = '') => {
        if (!obj || typeof obj !== 'object') return;

        Object.keys(obj).forEach(key => {
          const path = prefix ? `${prefix}.${key}` : key;
          fieldsToSelect.add(path);

          if (obj[key] && typeof obj[key] === 'object' && !Array.isArray(obj[key])) {
            findFields(obj[key], path);
          }
        });
      };

      findFields(value);
      setSelectedFields(fieldsToSelect);
    }
  }, [value]);

  const loadFields = async () => {
    if (!endpointType) return;

    try {
      setLoading(true);
      setError(null);
      console.log(`Loading fields for endpoint type: ${endpointType}`);
      const response = await api.getEndpointFields(endpointType);

      if (!response || response.length === 0) {
        console.warn(`No fields returned for ${endpointType}, using default fields`);

        if (endpointType === 'api-specs') {
          const defaultFields: Field[] = [
            { path: 'name', type: 'string', required: true },
            { path: 'description', type: 'string' },
            { path: 'contextPath', type: 'string' },
            { path: 'backendServiceUrl', type: 'string' },
            { path: 'status', type: 'string' },
            { path: 'type', type: 'string' },
            { path: 'style', type: 'string' },
            { path: 'authType', type: 'string' },
            { path: 'metaData.version', type: 'string' },
            { path: 'metaData.owner', type: 'string' },
            { path: 'addVersionToContextPath', type: 'boolean' }
          ];
          setFields(defaultFields);
        } else {
          setFields([
            { path: 'name', type: 'string', required: true },
            { path: 'description', type: 'string' }
          ]);
        }
      } else {
        setFields(response);
      }

      if (value) {
        const existingFields = new Set<string>();

        const findFields = (obj: any, prefix = '') => {
          if (!obj || typeof obj !== 'object') return;

          Object.keys(obj).forEach(key => {
            const path = prefix ? `${prefix}.${key}` : key;
            existingFields.add(path);

            if (obj[key] && typeof obj[key] === 'object' && !Array.isArray(obj[key])) {
              findFields(obj[key], path);
            }
          });
        };

        findFields(value);
        setSelectedFields(existingFields);
      }
    } catch (error) {
      console.error('Failed to load fields:', error);
      setError('Failed to load fields. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const toggleField = (fieldPath: string) => {
    if (!fieldPath) return;

    const newSelected = new Set(selectedFields);
    if (newSelected.has(fieldPath)) {
      newSelected.delete(fieldPath);
    } else {
      newSelected.add(fieldPath);
    }
    setSelectedFields(newSelected);

    const newValue = { ...value } || {};
    const parts = fieldPath.split('.');
    let current = newValue;

    // Find the field definition to determine its type
    const field = fields.find(f => f.path === fieldPath);
    const fieldType = field?.type?.toLowerCase() || 'string';

    // Create parent objects/arrays if they don't exist
    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      if (part.includes('[') && part.includes(']')) {
        const fieldName = part.split('[')[0];
        const index = parseInt(part.split('[')[1].replace(']', ''));

        // Initialize array if it doesn't exist
        if (!current[fieldName]) {
          current[fieldName] = [];
        }

        // Ensure array has enough elements
        while (current[fieldName].length <= index) {
          // Use empty object as default for array elements
          current[fieldName].push({});
        }

        current = current[fieldName][index];
      } else {
        // Initialize object if it doesn't exist
        if (!current[part]) {
          current[part] = {};
        }
        current = current[part];
      }
    }

    const lastPart = parts[parts.length - 1];
    if (lastPart.includes('[') && lastPart.includes(']')) {
      const fieldName = lastPart.split('[')[0];
      const index = parseInt(lastPart.split('[')[1].replace(']', ''));

      // Initialize array if it doesn't exist
      if (!current[fieldName]) {
        current[fieldName] = [];
      }

      if (newSelected.has(fieldPath)) {
        // Adding or updating an array element
        while (current[fieldName].length <= index) {
          // Use appropriate default value based on context
          const defaultValue = fieldType === 'object' ? {} : 
                              fieldType === 'array' ? [] : 
                              fieldType === 'number' || fieldType === 'integer' ? 0 : 
                              fieldType === 'boolean' ? false : '';
          current[fieldName].push(defaultValue);
        }
      } else {
        // Removing an array element
        if (current[fieldName].length > index) {
          current[fieldName].splice(index, 1);
        }
      }
    } else {
      if (newSelected.has(fieldPath)) {
        // Adding or updating a field
        let defaultValue: any = '';

        // Set appropriate default value based on field type
        switch(fieldType) {
          case 'boolean':
            defaultValue = false;
            break;
          case 'number':
          case 'integer':
            defaultValue = 0;
            break;
          case 'array':
            defaultValue = [];
            break;
          case 'object':
            defaultValue = {};
            break;
          default:
            defaultValue = '';
        }

        current[lastPart] = defaultValue;
      } else {
        // Removing a field
        delete current[lastPart];
      }
    }

    onChange(newValue);
  };

  const validateField = (fieldPath: string, fieldValue: any): string => {
    if (!fieldPath) return '';

    // Find the field definition to determine its type and requirements
    const field = fields.find(f => f.path === fieldPath);
    if (!field) return '';

    const fieldType = field.type.toLowerCase();

    // Check if field is required but empty
    if (field.required) {
      if (fieldValue === undefined || fieldValue === null || fieldValue === '') {
        return 'This field is required';
      }

      if (Array.isArray(fieldValue) && fieldValue.length === 0) {
        return 'At least one item is required';
      }

      if (fieldType === 'object' && typeof fieldValue === 'object' && Object.keys(fieldValue).length === 0) {
        return 'At least one property is required';
      }
    }

    // Type-specific validation
    if (fieldValue !== undefined && fieldValue !== null && fieldValue !== '') {
      if (fieldType === 'number' || fieldType === 'integer') {
        if (typeof fieldValue === 'string') {
          if (!/^-?\d*\.?\d*$/.test(fieldValue)) {
            return 'Must be a valid number';
          }
        } else if (typeof fieldValue !== 'number') {
          return 'Must be a number';
        }

        if (fieldType === 'integer' && !Number.isInteger(Number(fieldValue))) {
          return 'Must be an integer';
        }
      }
    }

    return '';
  };

  const updateFieldValue = (fieldPath: string, fieldValue: any) => {
    if (!fieldPath) return; // Skip empty paths

    const newValue = { ...value } || {};
    const parts = fieldPath.split('.');
    let current = newValue;

    // Find the field definition to determine its type
    const field = fields.find(f => f.path === fieldPath);
    const fieldType = field?.type?.toLowerCase() || 'string';

    // Create parent objects/arrays if they don't exist
    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      if (part.includes('[') && part.includes(']')) {
        const fieldName = part.split('[')[0];
        const index = parseInt(part.split('[')[1].replace(']', ''));

        // Initialize array if it doesn't exist
        if (!current[fieldName]) {
          current[fieldName] = [];
        }

        // Ensure array has enough elements
        while (current[fieldName].length <= index) {
          // Use empty object as default for array elements
          current[fieldName].push({});
        }

        current = current[fieldName][index];
      } else {
        // Initialize object if it doesn't exist
        if (!current[part]) {
          current[part] = {};
        }
        current = current[part];
      }
    }

    const lastPart = parts[parts.length - 1];
    if (lastPart.includes('[') && lastPart.includes(']')) {
      const fieldName = lastPart.split('[')[0];
      const index = parseInt(lastPart.split('[')[1].replace(']', ''));

      // Initialize array if it doesn't exist
      if (!current[fieldName]) {
        current[fieldName] = [];
      }

      // Handle array element update
      if (Array.isArray(current[fieldName])) {
        // Ensure array has enough elements
        while (current[fieldName].length <= index) {
          // Use appropriate default value based on context
          const defaultValue = fieldType === 'object' ? {} : 
                              fieldType === 'array' ? [] : 
                              fieldType === 'number' || fieldType === 'integer' ? 0 : 
                              fieldType === 'boolean' ? false : '';
          current[fieldName].push(defaultValue);
        }

        // Convert value based on field type
        let convertedValue = fieldValue;

        // If the array element is an object or array, handle it specially
        if (typeof fieldValue === 'object' && fieldValue !== null) {
          convertedValue = fieldValue; // Keep objects and arrays as is
        } else if (fieldType === 'boolean') {
          convertedValue = typeof fieldValue === 'string' 
            ? fieldValue.toLowerCase() === 'true' 
            : Boolean(fieldValue);
        } else if (fieldType === 'number' || fieldType === 'integer') {
          if (typeof fieldValue === 'string' && fieldValue.trim() !== '') {
            const num = Number(fieldValue);
            convertedValue = isNaN(num) ? 0 : num;
          } else if (typeof fieldValue !== 'number') {
            convertedValue = 0;
          }
        }

        current[fieldName][index] = convertedValue;
      }
    } else {
      // Handle regular field update
      let convertedValue: any = fieldValue;

      // Convert value based on field type
      if (fieldType === 'boolean') {
        if (typeof fieldValue === 'string') {
          convertedValue = fieldValue.toLowerCase() === 'true';
        } else {
          convertedValue = Boolean(fieldValue);
        }
      } else if (fieldType === 'number' || fieldType === 'integer') {
        if (typeof fieldValue === 'string' && fieldValue.trim() !== '') {
          const num = Number(fieldValue);
          convertedValue = isNaN(num) ? 0 : num;
        } else if (typeof fieldValue !== 'number') {
          convertedValue = 0;
        }
      } else if (fieldType === 'array') {
        // Ensure value is an array
        if (!Array.isArray(fieldValue)) {
          convertedValue = fieldValue ? [fieldValue] : [];
        }
      } else if (fieldType === 'object') {
        // Ensure value is an object
        if (typeof fieldValue !== 'object' || fieldValue === null || Array.isArray(fieldValue)) {
          convertedValue = {};
        }
      }

      current[lastPart] = convertedValue;
    }

    // Validate the field after update
    const errorMessage = validateField(fieldPath, fieldValue);
    const newFieldErrors = { ...fieldErrors };

    if (errorMessage) {
      newFieldErrors[fieldPath] = errorMessage;
    } else {
      delete newFieldErrors[fieldPath];
    }

    setFieldErrors(newFieldErrors);
    onChange(newValue);
  };

  const setReference = (fieldPath: string, reference: string) => {
    updateFieldValue(fieldPath, `\${${reference}}`);
    setShowReferenceDialog(null);
  };

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
  };

  const showSnackbar = (message: string, severity: 'success' | 'error' | 'info' = 'info') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const handleJsonExport = () => {
    try {
      setJsonText(JSON.stringify(value, null, 2));
      setJsonDialogMode('export');
      setShowJsonDialog(true);
    } catch (error) {
      console.error('Error exporting JSON:', error);
      showSnackbar('Failed to export JSON data', 'error');
    }
  };

  const handleJsonImport = () => {
    setJsonText('');
    setJsonDialogMode('import');
    setShowJsonDialog(true);
  };

  const processJsonImport = () => {
    try {
      if (!jsonText.trim()) {
        showSnackbar('Please enter valid JSON data', 'error');
        return;
      }

      const parsedJson = JSON.parse(jsonText);
      onChange(parsedJson);
      setShowJsonDialog(false);
      showSnackbar('JSON data imported successfully', 'success');

      // Update selected fields based on the imported JSON
      const fieldsToSelect = new Set<string>();

      const findFields = (obj: any, prefix = '') => {
        if (!obj || typeof obj !== 'object') return;

        Object.keys(obj).forEach(key => {
          const path = prefix ? `${prefix}.${key}` : key;
          fieldsToSelect.add(path);

          if (obj[key] && typeof obj[key] === 'object' && !Array.isArray(obj[key])) {
            findFields(obj[key], path);
          }
        });
      };

      findFields(parsedJson);
      setSelectedFields(fieldsToSelect);
    } catch (error) {
      console.error('Error importing JSON:', error);
      showSnackbar('Invalid JSON format. Please check your input.', 'error');
    }
  };

  const handleAddCustomField = () => {
    if (!customField.trim()) return;

    const newSelected = new Set(selectedFields);
    newSelected.add(customField);
    setSelectedFields(newSelected);

    const newValue = { ...value } || {};
    const parts = customField.split('.');
    let current = newValue;

    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      if (!current[part]) {
        current[part] = {};
      }
      current = current[part];
    }

    current[parts[parts.length - 1]] = '';

    onChange(newValue);
    setCustomField('');
  };

  const getCustomFields = (): string[] => {
    const customFields: string[] = [];

    const findCustomFields = (obj: any, prefix = '') => {
      if (!obj || typeof obj !== 'object') return;

      Object.keys(obj).forEach(key => {
        const path = prefix ? `${prefix}.${key}` : key;

        const isKnownField = fields.some(f => f.path === path);

        if (!isKnownField) {
          customFields.push(path);
        }

        if (obj[key] && typeof obj[key] === 'object' && !Array.isArray(obj[key])) {
          findCustomFields(obj[key], path);
        }
      });
    };

    findCustomFields(value);
    return customFields;
  };

  if (!endpointType) {
    return (
      <Box>
        <Typography variant="subtitle2" color="error">
          Endpoint type is not defined. Cannot load fields.
        </Typography>
      </Box>
    );
  }

  const customFields = getCustomFields();

  // Filter fields based on search term
  const filterBySearchTerm = (field: Field | string) => {
    if (!searchTerm) return true;
    const path = typeof field === 'string' ? field : field.path;
    return path.toLowerCase().includes(searchTerm.toLowerCase());
  };

  const availableFields = fields
    .filter(field => !selectedFields.has(field.path))
    .filter(filterBySearchTerm);

  const selectedFieldsList = fields
    .filter(field => selectedFields.has(field.path))
    .filter(filterBySearchTerm);

  const filteredCustomFields = customFields.filter(filterBySearchTerm);

  return (
    <Box>
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="subtitle1">
          Body Fields for {endpointType}
        </Typography>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Import JSON">
            <Button
              size="small"
              startIcon={<FileUploadIcon />}
              onClick={handleJsonImport}
              disabled={loading}
              variant="outlined"
            >
              Import
            </Button>
          </Tooltip>

          <Tooltip title="Export as JSON">
            <Button
              size="small"
              startIcon={<FileDownloadIcon />}
              onClick={handleJsonExport}
              disabled={loading || !value || Object.keys(value).length === 0}
              variant="outlined"
            >
              Export
            </Button>
          </Tooltip>

          <Button
            size="small"
            startIcon={<RefreshIcon />}
            onClick={handleRetry}
            disabled={loading}
          >
            Refresh Fields
          </Button>
        </Box>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
          <CircularProgress size={24} />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
          <Button onClick={handleRetry} size="small" sx={{ ml: 2 }}>
            Retry
          </Button>
        </Alert>
      ) : (
        <>
          <Paper sx={{ p: 2, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={showAllFields}
                    onChange={(e) => setShowAllFields(e.target.checked)}
                  />
                }
                label="Show all available fields"
              />
              <TextField
                size="small"
                label="Search fields"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Type to search..."
                sx={{ width: '250px' }}
              />
            </Box>

            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                {showAllFields ? 'All Available Fields:' : 'Add Fields:'}
              </Typography>

              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                {showAllFields ? (
                  fields.length === 0 ? (
                    <Typography>No fields available</Typography>
                  ) : (
                    fields.map((field) => (
                      <Chip
                        key={field.path}
                        label={field.path + (field.required ? ' *' : '')}
                        clickable
                        color={selectedFields.has(field.path) ? 'primary' : 'default'}
                        onClick={() => toggleField(field.path)}
                      />
                    ))
                  )
                ) : (
                  availableFields.length === 0 ? (
                    <Typography>No additional fields available</Typography>
                  ) : (
                    availableFields.map((field) => (
                      <Chip
                        key={field.path}
                        label={field.path + (field.required ? ' *' : '')}
                        clickable
                        onClick={() => toggleField(field.path)}
                      />
                    ))
                  )
                )}
              </Box>

              {/* Add custom field */}
              <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                <TextField
                  size="small"
                  label="Add Custom Field"
                  value={customField}
                  onChange={(e) => setCustomField(e.target.value)}
                  placeholder="e.g., customProperty or nested.property"
                  sx={{ flexGrow: 1 }}
                />
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<AddIcon />}
                  onClick={handleAddCustomField}
                  disabled={!customField.trim()}
                >
                  Add
                </Button>
              </Box>
            </Box>
          </Paper>

          {/* Show selected fields */}
          {selectedFields.size > 0 && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Selected Fields:
              </Typography>

              <Paper sx={{ p: 2 }}>
                {Array.from(selectedFields).filter(Boolean).map(fieldPath => {
                  const fieldValue = getValueAtPath(value, fieldPath) || '';
                  const field = fields.find(f => f.path === fieldPath);
                  const isCustomField = !field && customFields.includes(fieldPath);

                  return (
                    <Box key={fieldPath} sx={{
                      display: 'flex',
                      gap: 2,
                      mb: 2,
                      alignItems: 'center',
                      backgroundColor: isCustomField ? '#f5f8ff' : 'inherit',
                      p: isCustomField ? 1 : 0,
                      borderRadius: 1
                    }}>
                      <Typography sx={{ minWidth: 200 }}>
                        {fieldPath}
                        {field?.required && <span style={{ color: 'red' }}> *</span>}
                        {isCustomField && <span style={{ color: 'blue' }}> (custom)</span>}
                      </Typography>

                      {field?.type === 'boolean' ? (
                        <FormControlLabel
                          control={
                            <Switch
                              checked={!!fieldValue}
                              onChange={(e) => updateFieldValue(fieldPath, e.target.checked)}
                            />
                          }
                          label={fieldValue ? "True" : "False"}
                        />
                      ) : field?.type === 'enum' ? (
                        <Select
                          size="small"
                          value={fieldValue || ''}
                          onChange={(e) => updateFieldValue(fieldPath, e.target.value)}
                          sx={{ minWidth: 200 }}
                        >
                          <MenuItem value="DRAFT">DRAFT</MenuItem>
                          <MenuItem value="PUBLISHED">PUBLISHED</MenuItem>
                          <MenuItem value="DEPRECATED">DEPRECATED</MenuItem>
                        </Select>
                      ) : field?.type === 'array' ? (
                        <Box sx={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mb: 1 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                                Array ({Array.isArray(fieldValue) ? fieldValue.length : 0} items)
                              </Typography>
                              <Box sx={{ display: 'flex', gap: 1 }}>
                                <Tooltip title="Copy array to clipboard">
                                  <IconButton 
                                    size="small"
                                    onClick={() => {
                                      try {
                                        const jsonStr = JSON.stringify(fieldValue);
                                        navigator.clipboard.writeText(jsonStr);
                                        showSnackbar('Array copied to clipboard', 'success');
                                      } catch (error) {
                                        console.error('Error copying array:', error);
                                        showSnackbar('Failed to copy array', 'error');
                                      }
                                    }}
                                  >
                                    <ContentCopyIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="Paste array from clipboard">
                                  <IconButton 
                                    size="small"
                                    onClick={async () => {
                                      try {
                                        const text = await navigator.clipboard.readText();
                                        const data = JSON.parse(text);
                                        if (Array.isArray(data)) {
                                          updateFieldValue(fieldPath, data);
                                          showSnackbar('Array pasted successfully', 'success');
                                        } else {
                                          showSnackbar('Clipboard content is not an array', 'error');
                                        }
                                      } catch (error) {
                                        console.error('Error pasting array:', error);
                                        showSnackbar('Failed to paste array. Make sure clipboard contains valid JSON array.', 'error');
                                      }
                                    }}
                                  >
                                    <ContentPasteIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="Clear array">
                                  <IconButton 
                                    size="small"
                                    color="error"
                                    onClick={() => {
                                      if (confirm('Are you sure you want to clear this array?')) {
                                        updateFieldValue(fieldPath, []);
                                        showSnackbar('Array cleared', 'info');
                                      }
                                    }}
                                  >
                                    <DeleteIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              </Box>
                            </Box>
                            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                              <Button 
                                size="small" 
                                variant="outlined" 
                                onClick={() => {
                                  const newArray = Array.isArray(fieldValue) ? [...fieldValue] : [];
                                  newArray.push('');
                                  updateFieldValue(fieldPath, newArray);
                                }}
                              >
                                Add String
                              </Button>
                              <Button 
                                size="small" 
                                variant="outlined" 
                                onClick={() => {
                                  const newArray = Array.isArray(fieldValue) ? [...fieldValue] : [];
                                  newArray.push(0);
                                  updateFieldValue(fieldPath, newArray);
                                }}
                              >
                                Add Number
                              </Button>
                              <Button 
                                size="small" 
                                variant="outlined" 
                                onClick={() => {
                                  const newArray = Array.isArray(fieldValue) ? [...fieldValue] : [];
                                  newArray.push({});
                                  updateFieldValue(fieldPath, newArray);
                                }}
                              >
                                Add Object
                              </Button>
                              <Button 
                                size="small" 
                                variant="outlined" 
                                onClick={() => {
                                  const newArray = Array.isArray(fieldValue) ? [...fieldValue] : [];
                                  newArray.push([]);
                                  updateFieldValue(fieldPath, newArray);
                                }}
                              >
                                Add Array
                              </Button>
                            </Box>
                          </Box>
                          {Array.isArray(fieldValue) && fieldValue.map((item, index) => (
                            <Box key={index} sx={{ display: 'flex', mb: 1, alignItems: 'center' }}>
                              <Typography variant="body2" sx={{ minWidth: 50 }}>
                                [{index}]:
                              </Typography>
                              {typeof item === 'object' && item !== null ? (
                                <Box sx={{ flexGrow: 1, mr: 1, border: '1px solid #e0e0e0', borderRadius: 1, p: 1 }}>
                                  <Typography variant="body2" color="text.secondary">
                                    {Array.isArray(item) 
                                      ? `Array with ${item.length} item(s)` 
                                      : `Object with ${Object.keys(item).length} propert${Object.keys(item).length === 1 ? 'y' : 'ies'}`}
                                  </Typography>
                                  <Button 
                                    size="small" 
                                    variant="outlined" 
                                    sx={{ mt: 1 }}
                                    onClick={() => {
                                      // Create a custom field path for this nested object/array
                                      const nestedPath = `${fieldPath}[${index}]`;
                                      // Add it to selected fields to make it visible
                                      const newSelected = new Set(selectedFields);
                                      newSelected.add(nestedPath);
                                      setSelectedFields(newSelected);
                                    }}
                                  >
                                    Edit {Array.isArray(item) ? 'Array' : 'Object'}
                                  </Button>
                                </Box>
                              ) : (
                                <TextField
                                  size="small"
                                  value={item}
                                  onChange={(e) => {
                                    const newArray = [...fieldValue];
                                    newArray[index] = e.target.value;
                                    updateFieldValue(fieldPath, newArray);
                                  }}
                                  placeholder={`Item ${index}`}
                                  sx={{ flexGrow: 1, mr: 1 }}
                                  error={!!fieldErrors[`${fieldPath}[${index}]`]}
                                  helperText={fieldErrors[`${fieldPath}[${index}]`]}
                                />
                              )}
                              <Button 
                                size="small" 
                                color="error" 
                                onClick={() => {
                                  const newArray = [...fieldValue];
                                  newArray.splice(index, 1);
                                  updateFieldValue(fieldPath, newArray);
                                }}
                              >
                                Remove
                              </Button>
                            </Box>
                          ))}
                        </Box>
                      ) : field?.type === 'object' ? (
                        <Box sx={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mb: 1 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                                Object ({typeof fieldValue === 'object' && fieldValue !== null ? Object.keys(fieldValue).length : 0} properties)
                              </Typography>
                              <Box sx={{ display: 'flex', gap: 1 }}>
                                <Tooltip title="Copy object to clipboard">
                                  <IconButton 
                                    size="small"
                                    onClick={() => {
                                      try {
                                        const jsonStr = JSON.stringify(fieldValue);
                                        navigator.clipboard.writeText(jsonStr);
                                        showSnackbar('Object copied to clipboard', 'success');
                                      } catch (error) {
                                        console.error('Error copying object:', error);
                                        showSnackbar('Failed to copy object', 'error');
                                      }
                                    }}
                                  >
                                    <ContentCopyIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="Paste object from clipboard">
                                  <IconButton 
                                    size="small"
                                    onClick={async () => {
                                      try {
                                        const text = await navigator.clipboard.readText();
                                        const data = JSON.parse(text);
                                        if (typeof data === 'object' && data !== null && !Array.isArray(data)) {
                                          updateFieldValue(fieldPath, data);
                                          showSnackbar('Object pasted successfully', 'success');
                                        } else {
                                          showSnackbar('Clipboard content is not an object', 'error');
                                        }
                                      } catch (error) {
                                        console.error('Error pasting object:', error);
                                        showSnackbar('Failed to paste object. Make sure clipboard contains valid JSON object.', 'error');
                                      }
                                    }}
                                  >
                                    <ContentPasteIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="Clear object">
                                  <IconButton 
                                    size="small"
                                    color="error"
                                    onClick={() => {
                                      if (confirm('Are you sure you want to clear this object?')) {
                                        updateFieldValue(fieldPath, {});
                                        showSnackbar('Object cleared', 'info');
                                      }
                                    }}
                                  >
                                    <DeleteIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              </Box>
                            </Box>
                            <Box sx={{ display: 'flex', gap: 1 }}>
                              <Button 
                                size="small" 
                                variant="outlined" 
                                onClick={() => {
                                  const propertyName = prompt('Enter property name:');
                                  if (propertyName && propertyName.trim()) {
                                    const newObj = typeof fieldValue === 'object' && fieldValue !== null ? { ...fieldValue } : {};
                                    newObj[propertyName.trim()] = '';
                                    updateFieldValue(fieldPath, newObj);
                                  }
                                }}
                              >
                                Add Property
                              </Button>
                            </Box>
                          </Box>
                          {typeof fieldValue === 'object' && fieldValue !== null && Object.entries(fieldValue).map(([key, val]) => (
                            <Box key={key} sx={{ display: 'flex', mb: 1, alignItems: 'center' }}>
                              <Typography variant="body2" sx={{ minWidth: 100 }}>
                                {key}:
                              </Typography>
                              {typeof val === 'object' && val !== null ? (
                                <Box sx={{ flexGrow: 1, mr: 1, border: '1px solid #e0e0e0', borderRadius: 1, p: 1 }}>
                                  <Typography variant="body2" color="text.secondary">
                                    {Array.isArray(val) 
                                      ? `Array with ${val.length} item(s)` 
                                      : `Object with ${Object.keys(val).length} propert${Object.keys(val).length === 1 ? 'y' : 'ies'}`}
                                  </Typography>
                                  <Button 
                                    size="small" 
                                    variant="outlined" 
                                    sx={{ mt: 1 }}
                                    onClick={() => {
                                      // Create a custom field path for this nested object/array
                                      const nestedPath = `${fieldPath}.${key}`;
                                      // Add it to selected fields to make it visible
                                      const newSelected = new Set(selectedFields);
                                      newSelected.add(nestedPath);
                                      setSelectedFields(newSelected);
                                    }}
                                  >
                                    Edit {Array.isArray(val) ? 'Array' : 'Object'}
                                  </Button>
                                </Box>
                              ) : (
                                <TextField
                                  size="small"
                                  value={val}
                                  onChange={(e) => {
                                    const newObj = { ...fieldValue };
                                    newObj[key] = e.target.value;
                                    updateFieldValue(fieldPath, newObj);
                                  }}
                                  placeholder={`Value for ${key}`}
                                  sx={{ flexGrow: 1, mr: 1 }}
                                  error={!!fieldErrors[`${fieldPath}.${key}`]}
                                  helperText={fieldErrors[`${fieldPath}.${key}`]}
                                />
                              )}
                              <Button 
                                size="small" 
                                color="error" 
                                onClick={() => {
                                  const newObj = { ...fieldValue };
                                  delete newObj[key];
                                  updateFieldValue(fieldPath, newObj);
                                }}
                              >
                                Remove
                              </Button>
                            </Box>
                          ))}
                        </Box>
                      ) : (
                        <TextField
                          size="small"
                          value={fieldValue}
                          onChange={(e) => updateFieldValue(fieldPath, e.target.value)}
                          placeholder={`Enter ${fieldPath}`}
                          sx={{ flexGrow: 1 }}
                          required={field?.required}
                          type={field?.type === 'number' || field?.type === 'integer' ? 'number' : 'text'}
                          error={!!fieldErrors[fieldPath]}
                          helperText={fieldErrors[fieldPath]}
                        />
                      )}

                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => setShowReferenceDialog(fieldPath)}
                        disabled={availableRefs.length === 0}
                      >
                        Reference
                      </Button>

                      <Button
                        size="small"
                        color="error"
                        onClick={() => toggleField(fieldPath)}
                      >
                        Remove
                      </Button>
                    </Box>
                  );
                })}
              </Paper>
            </Box>
          )}
        </>
      )}

      {showReferenceDialog && (
        <Dialog 
          open={!!showReferenceDialog} 
          onClose={() => setShowReferenceDialog(null)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Select Reference for {showReferenceDialog}</DialogTitle>
          <DialogContent>
            {availableRefs.length > 0 ? (
              <>
                <TextField
                  autoFocus
                  margin="dense"
                  label="Search references"
                  fullWidth
                  variant="outlined"
                  onChange={(e) => {
                    // We're using a local state change here to avoid re-renders
                    const searchValue = e.target.value.toLowerCase();
                    const buttons = document.querySelectorAll('[data-ref-button]');
                    buttons.forEach((button) => {
                      const buttonText = button.textContent?.toLowerCase() || '';
                      if (buttonText.includes(searchValue)) {
                        (button as HTMLElement).style.display = 'block';
                      } else {
                        (button as HTMLElement).style.display = 'none';
                      }
                    });
                  }}
                  sx={{ mb: 2, mt: 1 }}
                />
                <Box sx={{ maxHeight: '300px', overflowY: 'auto', border: '1px solid #eee', borderRadius: 1, p: 1 }}>
                  {availableRefs.map(ref => (
                    <Button
                      key={ref}
                      fullWidth
                      onClick={() => setReference(showReferenceDialog, ref)}
                      sx={{ mb: 1, justifyContent: 'flex-start', textAlign: 'left' }}
                      data-ref-button="true"
                    >
                      {ref}
                    </Button>
                  ))}
                </Box>
              </>
            ) : (
              <Typography>No references available</Typography>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowReferenceDialog(null)}>Cancel</Button>
          </DialogActions>
        </Dialog>
      )}

      {/* JSON Import/Export Dialog */}
      <Dialog 
        open={showJsonDialog} 
        onClose={() => setShowJsonDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {jsonDialogMode === 'import' ? 'Import JSON Data' : 'Export JSON Data'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={15}
            value={jsonText}
            onChange={(e) => setJsonText(e.target.value)}
            placeholder={jsonDialogMode === 'import' 
              ? 'Paste your JSON data here...' 
              : 'JSON data will appear here...'}
            sx={{ mt: 1 }}
            InputProps={{
              readOnly: jsonDialogMode === 'export',
              sx: { fontFamily: 'monospace' }
            }}
          />
          {jsonDialogMode === 'export' && (
            <Button
              variant="outlined"
              sx={{ mt: 2 }}
              onClick={() => {
                navigator.clipboard.writeText(jsonText);
                showSnackbar('JSON copied to clipboard', 'success');
              }}
              startIcon={<ContentCopyIcon />}
            >
              Copy to Clipboard
            </Button>
          )}
        </DialogContent>
        <DialogActions>
          {jsonDialogMode === 'import' && (
            <Button 
              onClick={processJsonImport} 
              color="primary" 
              variant="contained"
            >
              Import
            </Button>
          )}
          <Button onClick={() => setShowJsonDialog(false)}>
            {jsonDialogMode === 'export' ? 'Close' : 'Cancel'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          severity={snackbarSeverity} 
          onClose={() => setSnackbarOpen(false)}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};
