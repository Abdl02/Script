import React from 'react';
import { Box, Typography, Button, Dialog, DialogTitle, DialogContent,
         DialogActions, TextField, List, ListItem, Chip } from '@mui/material';

interface ReferenceManagerProps {
  availableRefs: string[];
  onSelectReference: (field: string, reference: string) => void;
  onGenerateRandom: (field: string) => void;
}

export const ReferenceManager: React.FC<ReferenceManagerProps> = ({
  availableRefs,
  onSelectReference,
  onGenerateRandom
}) => {
  const [open, setOpen] = React.useState(false);
  const [selectedField, setSelectedField] = React.useState('');
  const [customPath, setCustomPath] = React.useState('');

  const handleOpen = (field: string) => {
    setSelectedField(field);
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setCustomPath('');
  };

  const handleSelectReference = (refName: string) => {
    onSelectReference(selectedField, refName);
    handleClose();
  };

  const handleCustomPath = () => {
    if (customPath.trim()) {
      onSelectReference(selectedField, customPath.trim());
      handleClose();
    }
  };

  return (
    <>
      <Box>
        <Typography variant="subtitle2" gutterBottom>
          Reference Management
        </Typography>

        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {availableRefs.map((ref) => (
            <Chip
              key={ref}
              label={ref}
              color="primary"
              variant="outlined"
              onClick={() => handleOpen('')}
            />
          ))}
        </Box>

        <Button
          variant="outlined"
          size="small"
          onClick={() => onGenerateRandom('')}
          sx={{ mt: 1 }}
        >
          Generate Random Values
        </Button>
      </Box>

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {selectedField ? `Select Reference for ${selectedField}` : 'Select Reference'}
        </DialogTitle>
        <DialogContent>
          <List>
            {availableRefs.map((ref) => (
              <ListItem
                key={ref}
                button
                onClick={() => handleSelectReference(ref)}
                sx={{ py: 1 }}
              >
                <Typography>{ref}</Typography>
              </ListItem>
            ))}
          </List>

          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2">
              Or specify custom path:
            </Typography>
            <TextField
              fullWidth
              size="small"
              value={customPath}
              onChange={(e) => setCustomPath(e.target.value)}
              placeholder="e.g., response.data.id"
              sx={{ mt: 1 }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleCustomPath} color="primary">
            Use Custom Path
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};