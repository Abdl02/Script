import React from 'react';
import { Box, FormControl, InputLabel, Select, MenuItem, TextField, IconButton } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { Assertion } from 'types/models';

interface AssertionEditorProps {
  assertions: Assertion[];
  onChange: (assertions: Assertion[]) => void;
}

export const AssertionEditor: React.FC<AssertionEditorProps> = ({ assertions, onChange }) => {
  const updateAssertion = (index: number, updated: Partial<Assertion>) => {
    const newAssertions = [...assertions];
    newAssertions[index] = { ...newAssertions[index], ...updated };
    onChange(newAssertions);
  };

  const removeAssertion = (index: number) => {
    const newAssertions = [...assertions];
    newAssertions.splice(index, 1);
    onChange(newAssertions);
  };

  return (
    <Box>
      {assertions.map((assertion, index) => (
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
    </Box>
  );
};