// src/index.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { AppGlobalStyles } from './styles/globalStyles';
import ErrorBoundary from './components/ErrorBoundary';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <AppGlobalStyles />
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);