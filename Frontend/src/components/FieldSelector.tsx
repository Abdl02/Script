import React, { useState, useEffect } from 'react';
import { api } from 'api/client';
import { Field } from 'types/models';
import { Box, Typography, Button, Chip, TextField, Dialog, DialogTitle, DialogContent, DialogActions, CircularProgress } from '@mui/material';

// Safe version of getValueAtPath that handles undefined inputs
const getValueAtPath = (obj: any, path: string | undefined): any => {
  if (!path) return undefined;

  return path.split('.').reduce((acc, part) => {
    if (!acc) return undefined; // Handle null/undefined parent object

    if (part.includes('[') && part.includes(']')) {
      const fieldName = part.split('[')[0];
      const index = parseInt(part.split('[')[1].replace(']', ''));
      return acc?.[fieldName]?.[index];
    }
    return acc?.[part];
  }, obj);
};

// Adapt the server response to match our Field interface
interface ApiFieldResponse {
  name?: string;
  path?: string;
  type?: string;
}

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

  useEffect(() => {
    if (endpointType) {
      loadFields();
    }
  }, [endpointType]);

  const loadFields = async () => {
    if (!endpointType) return;

    try {
      setLoading(true);
      setError(null);
      console.log(`Loading fields for endpoint type: ${endpointType}`);
      const response = await api.getEndpointFields(endpointType);

      // Convert the API response to our Field interface
      const fieldList: Field[] = (response as ApiFieldResponse[]).map(item => ({
        // Use path if available, otherwise use name, ensure we always have a string
        path: item.path || item.name || '',
        type: item.type || 'string',
      }));

      console.log('Fields loaded:', fieldList);
      setFields(fieldList);

      // Update selected fields from existing value
      if (value) {
        const existingFields = new Set(Object.keys(value).filter(Boolean));
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
    if (!fieldPath) return; // Skip empty paths

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
      if (!current[parts[i]]) {
        current[parts[i]] = {};
      }
      current = current[parts[i]];
    }

    const lastPart = parts[parts.length - 1];
    if (newSelected.has(fieldPath)) {
      current[lastPart] = '';
    } else {
      delete current[lastPart];
    }

    onChange(newValue);
  };

  const updateFieldValue = (fieldPath: string, fieldValue: any) => {
    if (!fieldPath) return; // Skip empty paths

    const newValue = { ...value } || {};
    const parts = fieldPath.split('.');
    let current = newValue;

    for (let i = 0; i < parts.length - 1; i++) {
      if (!current[parts[i]]) {
        current[parts[i]] = {};
      }
      current = current[parts[i]];
    }

    current[parts[parts.length - 1]] = fieldValue;
    onChange(newValue);
  };

  const setReference = (fieldPath: string, reference: string) => {
    updateFieldValue(fieldPath, `\${${reference}}`);
    setShowReferenceDialog(null);
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
        <Typography color="error">{error}</Typography>
      ) : (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
          {fields.length === 0 ? (
            <Typography>No fields available.</Typography>
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
            return (
              <Box key={fieldPath} sx={{ display: 'flex', gap: 2, mb: 2, alignItems: 'center' }}>
                <Typography sx={{ minWidth: 200 }}>{fieldPath}</Typography>
                <TextField
                  size="small"
                  value={fieldValue}
                  onChange={(e) => updateFieldValue(fieldPath, e.target.value)}
                  placeholder={`Enter ${fieldPath}`}
                  sx={{ flexGrow: 1 }}
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