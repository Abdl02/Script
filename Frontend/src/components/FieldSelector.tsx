import React, { useState, useEffect } from 'react';
import { api } from 'api/client';
import { Field } from 'types/models';
import { Box, Typography, Button, Chip, TextField, Dialog, DialogTitle, DialogContent, DialogActions, CircularProgress } from '@mui/material';

const getValueAtPath = (obj: any, path: string | undefined): any => {
  if (!path) return undefined;

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

export const FieldSelector: React.FC<FieldSelectorProps> = ({ endpointType, value, onChange, availableRefs }) => {
  const [fields, setFields] = useState<Field[]>([]);
  const [selectedFields, setSelectedFields] = useState<Set<string>>(new Set());
  const [showReferenceDialog, setShowReferenceDialog] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    if (endpointType) {
      loadFields();
    }
  }, [endpointType, retryCount]);

  // Update selected fields when value changes externally
  useEffect(() => {
    if (value) {
      const fieldsToSelect = new Set<string>();

      // Function to recursively find all fields in the value object
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

      // If we received an empty array, show a message
      if (!response || response.length === 0) {
        console.warn(`No fields returned for ${endpointType}, using default fields`);
        // For api-specs, use some default fields based on your API structure
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
          // For other endpoints, use basic fields
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

    // Update body value
    const newValue = { ...value } || {};
    const parts = fieldPath.split('.');
    let current = newValue;

    // Safely create nested structure
    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      if (part.includes('[') && part.includes(']')) {
        const fieldName = part.split('[')[0];
        const index = parseInt(part.split('[')[1].replace(']', ''));
        if (!current[fieldName]) current[fieldName] = [];
        while (current[fieldName].length <= index) {
          current[fieldName].push({});
        }
        current = current[fieldName][index];
      } else {
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
      if (!current[fieldName]) current[fieldName] = [];

      if (newSelected.has(fieldPath)) {
        // Ensure array has enough elements
        while (current[fieldName].length <= index) {
          current[fieldName].push('');
        }
        current[fieldName][index] = '';
      } else {
        // If array exists and has this index, remove it
        if (current[fieldName].length > index) {
          current[fieldName].splice(index, 1);
        }
      }
    } else {
      if (newSelected.has(fieldPath)) {
        // Determine default value based on field type if available
        const field = fields.find(f => f.path === fieldPath);
        let defaultValue: any = '';  // Use 'any' type to allow different value types

        if (field) {
          switch(field.type.toLowerCase()) {
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
        }

        current[lastPart] = defaultValue;
      } else {
        delete current[lastPart];
      }
    }

    onChange(newValue);
  };

  const updateFieldValue = (fieldPath: string, fieldValue: any) => {
    if (!fieldPath) return; // Skip empty paths

    const newValue = { ...value } || {};
    const parts = fieldPath.split('.');
    let current = newValue;

    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      if (part.includes('[') && part.includes(']')) {
        const fieldName = part.split('[')[0];
        const index = parseInt(part.split('[')[1].replace(']', ''));
        if (!current[fieldName]) current[fieldName] = [];
        while (current[fieldName].length <= index) {
          current[fieldName].push({});
        }
        current = current[fieldName][index];
      } else {
        if (!current[part]) {
          current[part] = {};
        }
        current = current[part];
      }
    }

    const field = fields.find(f => f.path === fieldPath);

    const lastPart = parts[parts.length - 1];
    if (lastPart.includes('[') && lastPart.includes(']')) {
      const fieldName = lastPart.split('[')[0];
      const index = parseInt(lastPart.split('[')[1].replace(']', ''));
      if (!current[fieldName]) current[fieldName] = [];
      while (current[fieldName].length <= index) {
        current[fieldName].push('');
      }
      current[fieldName][index] = fieldValue;
    } else {
      let convertedValue: any = fieldValue;

      if (field) {
        switch(field.type.toLowerCase()) {
          case 'boolean':
            if (typeof fieldValue === 'string') {
              convertedValue = fieldValue.toLowerCase() === 'true';
            }
            break;
          case 'number':
          case 'integer':
            if (typeof fieldValue === 'string' && fieldValue.trim() !== '') {
              convertedValue = Number(fieldValue);
            }
            break;
        }
      }

      current[lastPart] = convertedValue;
    }

    onChange(newValue);
  };

  const setReference = (fieldPath: string, reference: string) => {
    updateFieldValue(fieldPath, `\${${reference}}`);
    setShowReferenceDialog(null);
  };

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
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

  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom>
        Available Fields for {endpointType}:
      </Typography>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
          <CircularProgress size={24} />
        </Box>
      ) : error ? (
        <Box>
          <Typography color="error">{error}</Typography>
          <Button onClick={handleRetry} variant="outlined" size="small" sx={{ mt: 1 }}>
            Retry
          </Button>
        </Box>
      ) : (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
          {fields.length === 0 ? (
            <Box>
              <Typography>No fields available. Using default fields.</Typography>
              <Button onClick={handleRetry} variant="outlined" size="small" sx={{ mt: 1 }}>
                Retry
              </Button>
            </Box>
          ) : (
            fields.map((field) => (
              <Chip
                key={field.path}
                label={field.path}
                clickable
                color={selectedFields.has(field.path) ? 'primary' : 'default'}
                onClick={() => toggleField(field.path)}
              />
            ))
          )}
        </Box>
      )}

      {selectedFields.size > 0 && (
        <Box>
          <Typography variant="subtitle2" gutterBottom>
            Selected Fields:
          </Typography>

          {Array.from(selectedFields).filter(Boolean).map(fieldPath => {
            const fieldValue = getValueAtPath(value, fieldPath) || '';
            const field = fields.find(f => f.path === fieldPath);

            return (
              <Box key={fieldPath} sx={{ display: 'flex', gap: 2, mb: 2, alignItems: 'center' }}>
                <Typography sx={{ minWidth: 200 }}>
                  {fieldPath}
                  {field?.required && <span style={{ color: 'red' }}> *</span>}
                </Typography>
                <TextField
                  size="small"
                  value={fieldValue}
                  onChange={(e) => updateFieldValue(fieldPath, e.target.value)}
                  placeholder={`Enter ${fieldPath}`}
                  sx={{ flexGrow: 1 }}
                  required={field?.required}
                  type={field?.type === 'number' || field?.type === 'integer' ? 'number' : 'text'}
                />
                <Button
                  size="small"
                  onClick={() => setShowReferenceDialog(fieldPath)}
                  disabled={availableRefs.length === 0}
                >
                  Reference
                </Button>
              </Box>
            );
          })}
        </Box>
      )}

      {showReferenceDialog && (
        <Dialog open={!!showReferenceDialog} onClose={() => setShowReferenceDialog(null)}>
          <DialogTitle>Select Reference for {showReferenceDialog}</DialogTitle>
          <DialogContent>
            {availableRefs.length > 0 ? (
              availableRefs.map(ref => (
                <Button
                  key={ref}
                  fullWidth
                  onClick={() => setReference(showReferenceDialog, ref)}
                  sx={{ mb: 1 }}
                >
                  {ref}
                </Button>
              ))
            ) : (
              <Typography>No references available</Typography>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowReferenceDialog(null)}>Cancel</Button>
          </DialogActions>
        </Dialog>
      )}
    </Box>
  );
};