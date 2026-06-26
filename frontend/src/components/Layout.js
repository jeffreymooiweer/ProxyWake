import React, { useEffect, useState } from 'react';
import {
  AppBar,
  Box,
  Button,
  Container,
  IconButton,
  Tab,
  Tabs,
  Toolbar,
  Tooltip,
  Typography,
} from '@mui/material';
import PowerSettingsNewIcon from '@mui/icons-material/PowerSettingsNew';
import LogoutIcon from '@mui/icons-material/Logout';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';
import { useAuth } from '../context/AuthContext';
import { useThemeMode } from '../context/ThemeContext';

const tabLabels = [
  'Dashboard',
  'Apparaten',
  'Groepen',
  'Integratie',
  'Automatisering',
  'Statistieken',
  'Logboek',
  'Instellingen',
];

const Layout = ({ activeTab, onTabChange, children }) => {
  const { logout, passwordRequired } = useAuth();
  const { mode, toggleTheme } = useThemeMode();

  return (
    <Box sx={{ minHeight: '100vh', pb: 6 }}>
      <AppBar position="sticky" elevation={0} sx={{ background: 'rgba(11, 16, 32, 0.82)', backdropFilter: 'blur(16px)', borderBottom: '1px solid rgba(148, 163, 184, 0.12)' }}>
        <Toolbar sx={{ gap: 2, flexWrap: 'wrap' }}>
          <PowerSettingsNewIcon color="secondary" />
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6">ProxyWake</Typography>
            <Typography variant="caption" color="text.secondary">Wake-on-LAN platform v3.0</Typography>
          </Box>
          <Tooltip title="Thema wisselen">
            <IconButton color="inherit" onClick={toggleTheme}>
              {mode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>
          </Tooltip>
          {passwordRequired && (
            <Button color="inherit" startIcon={<LogoutIcon />} onClick={logout}>Uitloggen</Button>
          )}
        </Toolbar>
        <Container maxWidth="lg">
          <Tabs value={activeTab} onChange={(_, value) => onTabChange(value)} variant="scrollable" scrollButtons="auto">
            {tabLabels.map((label) => <Tab key={label} label={label} />)}
          </Tabs>
        </Container>
      </AppBar>
      <Container maxWidth="lg" sx={{ mt: 4 }}>{children}</Container>
    </Box>
  );
};

export default Layout;
