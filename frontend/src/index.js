import React from 'react';
import { createRoot } from 'react-dom/client'; // Import createRoot
import './index.css';
import App from './App';
import * as serviceWorker from './serviceWorker';
import 'bootstrap/dist/css/bootstrap.min.css';

const root = createRoot(document.getElementById('root')); // Use createRoot

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Service worker code remains the same
serviceWorker.unregister();
