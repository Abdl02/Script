import { GlobalStyles } from '@mui/material';

export const AppGlobalStyles = () => (
  <GlobalStyles
    styles={{
      body: {
        margin: 0,
        padding: 0,
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif',
        WebkitFontSmoothing: 'antialiased',
        MozOsxFontSmoothing: 'grayscale',
      },
      code: {
        fontFamily: 'source-code-pro, Menlo, Monaco, Consolas, "Courier New", monospace',
      },
      '#root': {
        minHeight: '100vh',
      },
    }}
  />
);