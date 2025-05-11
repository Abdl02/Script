import React, { useState } from 'react';
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  Box,
  Chip,
  Divider,
  Stack,
  Backdrop,
  CircularProgress,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CloseIcon from '@mui/icons-material/Close';
import JsonView from '@uiw/react-json-view';

const RequestDetails = ({ request }: { request: any }) => (
  <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, backgroundColor: '#fafafa' }}>
    <Typography variant="body2" fontWeight="bold" gutterBottom>
      Request Info
    </Typography>
    <Stack spacing={1}>
      <Typography variant="body2">URL: {request.url}</Typography>
      <Typography variant="body2">Method: {request.method}</Typography>
      <Typography variant="body2">Headers:</Typography>
      <JsonView value={request.headers} displayDataTypes={false} />
      {request.body && (
        <>
          <Typography variant="body2">Body:</Typography>
          <JsonView value={request.body} displayDataTypes={false} />
        </>
      )}
    </Stack>
  </Paper>
);

const ResponseDetails = ({ response }: { response: any }) => (
  <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, backgroundColor: '#fafafa' }}>
    <Typography variant="body2" fontWeight="bold" gutterBottom>
      Response Info
    </Typography>
    <Stack spacing={1}>
      <Typography variant="body2">Status: {response.status}</Typography>
      <Typography variant="body2">Headers:</Typography>
      <JsonView value={response.headers} displayDataTypes={false} />
      {response.body && (
        <>
          <Typography variant="body2">Body:</Typography>
          <JsonView value={response.body} displayDataTypes={false} />
        </>
      )}
    </Stack>
  </Paper>
);

const ScenarioResults: React.FC<any> = ({ results, loading }) => {
  const [open, setOpen] = useState(false);

  if (loading) {
    return (
      <Backdrop open sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <CircularProgress color="inherit" />
      </Backdrop>
    );
  }

  return (
    <>
      <Button variant="contained" onClick={() => setOpen(true)}>
        View Scenario Results
      </Button>

<Dialog
  open={open}
  onClose={() => setOpen(false)}
  fullWidth
  maxWidth="lg" // Larger modal width
  scroll="paper"
  PaperProps={{
    sx: {
      height: '90vh', // Increase modal height
      maxHeight: '90vh', // Ensure it doesn't exceed viewport
    },
  }}
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          Scenario Results
          <IconButton onClick={() => setOpen(false)}>
            <CloseIcon />
          </IconButton>
        </DialogTitle>

        <DialogContent dividers>
          {!results ? (
            <Typography variant="body2" color="textSecondary">
              No results available.
            </Typography>
          ) : (
            <Box>
              <Stack direction="row" alignItems="center" spacing={2} mb={2}>
                <Typography variant="subtitle1">Status:</Typography>
                <Chip
                  label={results.status}
                  color={results.status === 'success' ? 'success' : 'error'}
                  variant="outlined"
                />
              </Stack>

              <Typography variant="body2" gutterBottom>
                Total Requests: {results.numberOfRequests}
              </Typography>

              <Divider sx={{ my: 2 }} />

              {results.requests.map((request: any, index: number) => (
                <Accordion key={index} sx={{ mb: 1 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                      <Typography sx={{ flexGrow: 1 }}>
                        {index + 1}. {request.name}
                      </Typography>
                      <Chip
                        label={request.status.text}
                        color={request.status.text === 'SUCCESS' ? 'success' : 'error'}
                        size="small"
                      />
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Stack spacing={2}>
                      <RequestDetails request={request.request} />
                      <ResponseDetails response={request.response} />
                    </Stack>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          )}
        </DialogContent>

        <DialogActions>
          <Button onClick={() => setOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
    );
}
export default ScenarioResults;