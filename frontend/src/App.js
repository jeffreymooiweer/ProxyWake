import React, { useState } from 'react';
import { Box, CircularProgress } from '@mui/material';
import Layout from './components/Layout';
import DashboardPage from './pages/DashboardPage';
import DevicesPage from './pages/DevicesPage';
import GroupsPage from './pages/GroupsPage';
import IntegrationPage from './pages/IntegrationPage';
import AutomationPage from './pages/AutomationPage';
import StatisticsPage from './pages/StatisticsPage';
import LogsPage from './pages/LogsPage';
import SettingsPage from './pages/SettingsPage';
import LoginPage from './pages/LoginPage';
import SetupWizard from './pages/SetupWizard';
import WaitingPage from './pages/WaitingPage';
import { useAuth } from './context/AuthContext';

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
      {pages[activeTab]}
    </Layout>
  );
};

export default App;
