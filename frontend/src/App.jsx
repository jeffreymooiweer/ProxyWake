import React, { Suspense, lazy, useState } from 'react';
import { Box, CircularProgress } from '@mui/material';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import SetupWizard from './pages/SetupWizard';
import WaitingPage from './pages/WaitingPage';
import { useAuth } from './context/AuthContext';

// Each tab is loaded on first use so the initial download stays small.
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const DevicesPage = lazy(() => import('./pages/DevicesPage'));
const GroupsPage = lazy(() => import('./pages/GroupsPage'));
const IntegrationPage = lazy(() => import('./pages/IntegrationPage'));
const AutomationPage = lazy(() => import('./pages/AutomationPage'));
const StatisticsPage = lazy(() => import('./pages/StatisticsPage'));
const LogsPage = lazy(() => import('./pages/LogsPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));

const Spinner = () => (
  <Box sx={{ minHeight: '40vh', display: 'grid', placeItems: 'center' }}>
    <CircularProgress color="secondary" />
  </Box>
);

const App = () => {
  const { loading, authenticated, passwordRequired, onboardingCompleted, refresh } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [setupDone, setSetupDone] = useState(false);

  if (window.location.pathname === '/waiting') {
    return <WaitingPage />;
  }

  if (loading) {
    return (
      <Box sx={{ minHeight: '100vh', display: 'grid', placeItems: 'center' }}>
        <CircularProgress color="secondary" />
      </Box>
    );
  }

  if (!onboardingCompleted && !setupDone) {
    return <SetupWizard onComplete={() => { setSetupDone(true); refresh(); }} />;
  }

  if (passwordRequired && !authenticated) {
    return <LoginPage />;
  }

  const pages = [
    <DashboardPage onNavigate={setActiveTab} />,
    <DevicesPage />,
    <GroupsPage />,
    <IntegrationPage />,
    <AutomationPage />,
    <StatisticsPage />,
    <LogsPage />,
    <SettingsPage />,
  ];

  return (
    <Layout activeTab={activeTab} onTabChange={setActiveTab}>
      <Suspense fallback={<Spinner />}>
        {pages[activeTab]}
      </Suspense>
    </Layout>
  );
};

export default App;
