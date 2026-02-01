import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
// Load critical font weights immediately
import '@fontsource/space-grotesk/400.css';
import '@fontsource/space-grotesk/600.css';
import '@fontsource/dm-sans/400.css';
import '@fontsource/dm-sans/600.css';
import App from './App.tsx';

// Lazy load additional font weights after initial render
setTimeout(() => {
  import('@fontsource/space-grotesk/500.css');
  import('@fontsource/space-grotesk/700.css');
  import('@fontsource/dm-sans/500.css');
}, 100);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
