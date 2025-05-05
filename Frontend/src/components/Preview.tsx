import React from 'react';
import { Box, Typography, Paper, Tabs, Tab } from '@mui/material';
import { JsonViewer } from '@textea/json-viewer';

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
          <JsonViewer
            value={data}
            theme="light"
            defaultInspectDepth={2}
            displayDataTypes={false}
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