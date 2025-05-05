import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { Field } from '../types/models';
import { Box, Typography, Button, Chip, TextField, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';

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

  useEffect(() => {
    loadFields();
  }, [endpointType]);

  const loadFields = async () => {
    try {
      const data = await api.getEndpointFields(endpointType);
      setFields(data);

      // Update selected fields from existing value
      if (value) {
        const existingFields = new Set(Object.keys(value));
        setSelectedFields(existingFields);
      }
    } catch (error) {
      console.error('Failed to load fields:', error);
    }
  };

  const toggleField = (fieldPath: string) => {
    const newSelected = new Set(selectedFields);
    if (newSelected.has(fieldPath)) {
      newSelected.delete(fieldPath);
    } else {
      newSelected.add(fieldPath);
    }
    setSelectedFields(newSelected);

    // Update body value
    const newValue = { ...value };
    const parts = fieldPath.split('.');
    let current = newValue;

    for (let i = 0; i < parts.length - 1; i++) {
      if (!current[parts[i]]) {
        current[parts[i]] = {};
      }
      current = current[parts[i]];
    }

    if (newSelected.has(fieldPath)) {
      current[parts[parts.length - 1]] = '';
    } else {
      delete current[parts[parts.length - 1]];
    }

    onChange(newValue);
  };

  const updateFieldValue = (fieldPath: string, fieldValue: any) => {
    const newValue = { ...value };
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

  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom>
        Available Fields for {endpointType}:
      </Typography>

      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
        {fields.map((field) => (
          <Chip
            key={field.path}
            label={field.path}
            clickable
            color={selectedFields.has(field.path) ? 'primary' : 'default'}
            onClick={() => toggleField(field.path)}
          />
        ))}
      </Box>

      {selectedFields.size > 0 && (
        <Box>
          <Typography variant="subtitle2" gutterBottom>
            Selected Fields:
          </Typography>

          {Array.from(selectedFields).map(fieldPath => {
            const value = getValueAtPath(value, fieldPath);
            return (
              <Box key={fieldPath} sx={{ display: 'flex', gap: 2, mb: 2, alignItems: 'center' }}>
                <Typography sx={{ minWidth: 200 }}>{fieldPath}</Typography>
                <TextField
                  size="small"
                  value={value || ''}
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
            {availableRefs.map(ref => (
              <Button
                key={ref}
                fullWidth
                onClick={() => setReference(showReferenceDialog, ref)}
                sx={{ mb: 1 }}
              >
                {ref}
              </Button>
            ))}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowReferenceDialog(null)}>Cancel</Button>
          </DialogActions>
        </Dialog>
      )}
    </Box>
  );
};