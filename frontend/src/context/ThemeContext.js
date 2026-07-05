import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { api } from '../api/client';

const ThemeModeContext = createContext(null);

const buildTheme = (mode) => createTheme({
  palette: {
    mode,
    primary: { main: '#39ff14', light: '#6bff47', dark: '#2ecc12', contrastText: '#0a0f1a' },
    secondary: { main: '#b8ffcc' },
    success: { main: '#39ff14' },
    error: { main: '#f87171' },
    warning: { main: '#fbbf24' },
    background: mode === 'dark'
      ? { default: '#0a0f1a', paper: 'rgba(12, 18, 32, 0.88)' }
      : { default: '#f8fafc', paper: '#ffffff' },
  },
  shape: { borderRadius: 16 },
  typography: {
    fontFamily: '"Inter", "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
    h4: { fontWeight: 700, letterSpacing: '-0.02em' },
    button: { textTransform: 'none', fontWeight: 600 },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          background: mode === 'dark'
            ? 'radial-gradient(circle at top left, rgba(57,255,20,0.12), transparent 35%), radial-gradient(circle at top right, rgba(57,255,20,0.06), transparent 30%), #0a0f1a'
            : 'linear-gradient(180deg, #eef2ff 0%, #f8fafc 40%)',
          minHeight: '100vh',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          border: mode === 'dark' ? '1px solid rgba(148, 163, 184, 0.12)' : '1px solid rgba(148, 163, 184, 0.25)',
        },
      },
    },
  },
});

export const AppThemeProvider = ({ children }) => {
  const [mode, setMode] = useState('dark');

  useEffect(() => {
    api.authStatus()
      .then((status) => setMode(status.theme || 'dark'))
      .catch(() => {});
  }, []);

  const toggleTheme = useCallback(async () => {
    const next = mode === 'dark' ? 'light' : 'dark';
    setMode(next);
    try {
      await api.updateTheme(next);
    } catch {
      // ignore if not logged in yet
    }
  }, [mode]);

  const theme = useMemo(() => buildTheme(mode), [mode]);
  const value = useMemo(() => ({ mode, toggleTheme, setMode }), [mode, toggleTheme]);

  return (
    <ThemeModeContext.Provider value={value}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ThemeModeContext.Provider>
  );
};

export const useThemeMode = () => useContext(ThemeModeContext);
