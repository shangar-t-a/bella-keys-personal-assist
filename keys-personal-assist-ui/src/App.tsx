import { lazy, Suspense } from 'react';
import { BrowserRouter, HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import { Box, CircularProgress } from '@mui/material';
import { ThemeProvider } from '@/theme/ThemeProvider';
import AppShell from '@/components/AppShell';
import { getAvailableServices } from '@/config/features';

const Router = import.meta.env.VITE_APP_ENV === 'electron' ? HashRouter : BrowserRouter;

// Lazy load all route components for code splitting
const HomePage = lazy(() => import('@/pages/HomePage'));
const ChatPage = lazy(() => import('@/pages/ChatPage'));
const SpendingAccountSummaryPage = lazy(() => import('@/pages/SpendingAccountSummaryPage'));
const MonthlyPlannerPage = lazy(() => import('@/pages/MonthlyPlannerPage'));
const SavingsFundSegregatorPage = lazy(() => import('@/pages/SavingsFundSegregatorPage'));
const SettingsPage = lazy(() => import('@/pages/SettingsPage'));

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
  const services = getAvailableServices();

  return (
    <ThemeProvider>
      <Router>
        <AppShell>
          <Suspense fallback={<LoadingFallback />}>
            <Routes>
              <Route path="/" element={<HomePage />} />
              {services.bellaChat && <Route path="/chat" element={<ChatPage />} />}
              {services.expenseManager && (
                <>
                  <Route path="/dashboard" element={<Navigate to="/dashboard/accounts" replace />} />
                  <Route path="/dashboard/accounts" element={<SpendingAccountSummaryPage />} />
                  <Route path="/budget" element={<MonthlyPlannerPage />} />
                  <Route path="/dashboard/envelopes" element={<SavingsFundSegregatorPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                </>
              )}
              {/* Fallback route for disabled features */}
              <Route path="*" element={<HomePage />} />
            </Routes>
          </Suspense>
        </AppShell>
        <Toaster position="top-right" richColors />
      </Router>
    </ThemeProvider>
  );
}

export default App;
