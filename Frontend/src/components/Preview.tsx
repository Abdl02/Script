import React from 'react';
import { Box, Typography, Paper, Tabs, Tab } from '@mui/material';
import JsonView from '@uiw/react-json-view';

interface PreviewProps {
  data: any;
  title?: string;
}

export const Preview: React.FC<PreviewProps> = ({ data, title = "Preview" }) => {
  const [tabValue, setTabValue] = React.useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Typography variant="h6" gutterBottom>{title}</Typography>

      <Tabs value={tabValue} onChange={handleTabChange}>
        <Tab label="JSON" />
        <Tab label="Raw" />
      </Tabs>

      <Box sx={{ mt: 2 }}>
        {tabValue === 0 && (
          <JsonView  // Changed from JsonViewer to JsonView
            value={data}
            collapsed={2}
            displayDataTypes={false}
            style={{
              backgroundColor: 'transparent',
              padding: '10px',
              borderRadius: '4px',
              border: '1px solid #ccc'
            }}
          />
        )}
        {tabValue === 1 && (
          <pre style={{
            padding: '10px',
            backgroundColor: '#f5f5f5',
            borderRadius: '4px',
            overflow: 'auto'
          }}>
            {JSON.stringify(data, null, 2)}
          </pre>
        )}
      </Box>
    </Paper>
  );
};