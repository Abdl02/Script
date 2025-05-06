import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { AppGlobalStyles } from './styles/globalStyles';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <AppGlobalStyles />
    <App />
  </React.StrictMode>
);