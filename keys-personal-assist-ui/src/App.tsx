import { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'sonner';
import { Box, CircularProgress } from '@mui/material';
import { ThemeProvider } from '@/theme/ThemeProvider';

// Lazy load all route components for code splitting
const HomePage = lazy(() => import('@/pages/HomePage'));
const ChatPage = lazy(() => import('@/pages/ChatPage'));
const DashboardPage = lazy(() => import('@/pages/DashboardPage'));
const SpendingAccountSummaryPage = lazy(() => import('@/pages/SpendingAccountSummaryPage'));

// Loading fallback component
const LoadingFallback = () => (
  <Box
    display="flex"
    justifyContent="center"
    alignItems="center"
    minHeight="100vh"
  >
    <CircularProgress />
  </Box>
);

function App() {
  return (
    <ThemeProvider>
      <Router>
        <Suspense fallback={<LoadingFallback />}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/dashboard/spending-account-summary" element={<SpendingAccountSummaryPage />} />
          </Routes>
        </Suspense>
        <Toaster position="top-right" richColors />
      </Router>
    </ThemeProvider>
  );
}

export default App;
