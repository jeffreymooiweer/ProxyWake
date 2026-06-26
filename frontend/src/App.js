import React, { useState } from 'react';
import { Box, CircularProgress } from '@mui/material';
import Layout from './components/Layout';
import DashboardPage from './pages/DashboardPage';
import DevicesPage from './pages/DevicesPage';
import IntegrationPage from './pages/IntegrationPage';
import LogsPage from './pages/LogsPage';
import LoginPage from './pages/LoginPage';
import { useAuth } from './context/AuthContext';

const App = () => {
  const { loading, authenticated, passwordRequired } = useAuth();
  const [activeTab, setActiveTab] = useState(0);

  if (loading) {
    return (
      <Box sx={{ minHeight: '100vh', display: 'grid', placeItems: 'center' }}>
        <CircularProgress color="secondary" />
      </Box>
    );
  }

  if (passwordRequired && !authenticated) {
    return <LoginPage />;
  }

  const pages = [
    <DashboardPage onNavigate={setActiveTab} />,
    <DevicesPage />,
    <IntegrationPage />,
    <LogsPage />,
  ];

  return (
    <Layout activeTab={activeTab} onTabChange={setActiveTab}>
      {pages[activeTab]}
    </Layout>
  );
};

export default App;
