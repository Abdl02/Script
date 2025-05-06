import React, { useState } from 'react';
import { Paper, Typography, Box, Accordion, AccordionSummary,
         AccordionDetails, Chip, Divider } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import JsonView from '@uiw/react-json-view';

interface ResultsViewerProps {
  results: any;
}

export const ResultsViewer: React.FC<ResultsViewerProps> = ({ results }) => {
  const [expandedRequest, setExpandedRequest] = useState<string | null>(null);

  const handleToggleRequest = (requestName: string) => {
    setExpandedRequest(expandedRequest === requestName ? null : requestName);
  };

  if (!results || !results.requests || results.requests.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography>No execution results available.</Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>Execution Results</Typography>

      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle1">
          Status: {' '}
          <Chip
            label={results.success ? "Success" : "Failed"}
            color={results.success ? "success" : "error"}
            icon={results.success ? <CheckCircleIcon /> : <ErrorIcon />}
          />
        </Typography>
        <Typography variant="body2">
          Duration: {results.duration || 'N/A'} ms
        </Typography>
      </Box>

      <Divider sx={{ my: 2 }} />

      {results.requests.map((request: any, index: number) => (
        <Accordion
          key={index}
          expanded={expandedRequest === request.name}
          onChange={() => handleToggleRequest(request.name)}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
              <Typography sx={{ flexGrow: 1 }}>
                {index + 1}. {request.name}
              </Typography>
              <Chip
                label={request.success ? "Passed" : "Failed"}
                color={request.success ? "success" : "error"}
                size="small"
              />
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2">Request:</Typography>
              <Box sx={{ backgroundColor: '#f5f5f5', p: 2, borderRadius: 1 }}>
                <Typography variant="body2">{request.method} {request.url}</Typography>
                {request.body && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2">Body:</Typography>
                    <JsonView value={request.body} displayDataTypes={false} />
                  </Box>
                )}
              </Box>
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2">Response:</Typography>
              <Box sx={{ backgroundColor: '#f5f5f5', p: 2, borderRadius: 1 }}>
                <Typography variant="body2">Status: {request.response?.status}</Typography>
                {request.response?.body && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2">Body:</Typography>
                    <JsonView value={request.response.body} displayDataTypes={false} />
                  </Box>
                )}
              </Box>
            </Box>

            {request.assertions && request.assertions.length > 0 && (
              <Box>
                <Typography variant="subtitle2">Assertions:</Typography>
                {request.assertions.map((assertion: any, i: number) => (
                  <Box key={i} sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <Chip
                      label={assertion.passed ? "Passed" : "Failed"}
                      color={assertion.passed ? "success" : "error"}
                      size="small"
                      sx={{ mr: 1 }}
                    />
                    <Typography>
                      {assertion.type}: {assertion.expected}
                      {assertion.path && ` (Path: ${assertion.path})`}
                    </Typography>
                  </Box>
                ))}
              </Box>
            )}
          </AccordionDetails>
        </Accordion>
      ))}
    </Paper>
  );
};