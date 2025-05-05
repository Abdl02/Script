import React from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Box, Typography } from '@mui/material';

interface ReferenceSelectorProps {
  open: boolean;
  onClose: () => void;
  onSelect: (reference: string) => void;
  availableRefs: string[];
  fieldPath: string;
}

export const ReferenceSelector: React.FC<ReferenceSelectorProps> = ({
  open,
  onClose,
  onSelect,
  availableRefs,
  fieldPath
}) => {
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Select Reference for {fieldPath}</DialogTitle>
      <DialogContent>
        {availableRefs.length > 0 ? (
          availableRefs.map(ref => (
            <Button
              key={ref}
              fullWidth
              onClick={() => onSelect(ref)}
              sx={{ mb: 1, textAlign: 'left' }}
              variant="outlined"
            >
              {ref}
            </Button>
          ))
        ) : (
          <Typography>No references available</Typography>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
      </DialogActions>
    </Dialog>
  );
};