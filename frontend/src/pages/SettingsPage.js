import React, { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  Snackbar,
  TextField,
  Typography,
} from '@mui/material';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';
import VpnKeyIcon from '@mui/icons-material/VpnKey';
import { api } from '../api/client';
import { useThemeMode } from '../context/ThemeContext';

const SettingsPage = () => {
  const { mode, toggleTheme } = useThemeMode();
  const [settings, setSettings] = useState(null);
  const [password, setPassword] = useState('');
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    api.getSettings().then(setSettings).catch(() => {});
  }, []);

  const show = (message, severity = 'success') => setNotification({ open: true, message, severity });

  const handleExport = async () => {
    const data = await api.exportDevices('json');
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'proxywake-export.json';
    link.click();
    show('Export gedownload.');
  };

  const handleImport = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    const data = JSON.parse(text);
    const result = await api.importDevices(data.devices || data, true);
    show(`${result.imported} apparaten geïmporteerd.`);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Instellingen</Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>Beveiliging, thema, export en geavanceerde opties.</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Thema</Typography>
              <Button variant="outlined" startIcon={mode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />} onClick={toggleTheme}>
                Schakel naar {mode === 'dark' ? 'licht' : 'donker'} thema
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>API-sleutel</Typography>
              <TextField fullWidth value={settings?.api_key || ''} InputProps={{ readOnly: true }} sx={{ mb: 2 }} />
              <Button variant="outlined" startIcon={<VpnKeyIcon />} onClick={() => api.rotateApiKey().then((result) => { setSettings({ ...settings, api_key: result.api_key }); show(result.message); })}>
                Roteer API-sleutel
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Wachtwoord wijzigen</Typography>
              <TextField fullWidth type="password" label="Nieuw wachtwoord" value={password} onChange={(e) => setPassword(e.target.value)} sx={{ mb: 2 }} />
              <Button variant="contained" onClick={() => api.updatePassword(password).then(() => show('Wachtwoord bijgewerkt.'))}>Opslaan</Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Export / Import</Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Button variant="outlined" onClick={handleExport}>Exporteer JSON</Button>
                <Button variant="outlined" component="label">
                  Importeer JSON
                  <input hidden type="file" accept="application/json" onChange={handleImport} />
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Observability</Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Prometheus metrics: <code>/api/metrics</code> — Health check: <code>/api/health</code>
              </Typography>
              <Alert severity="info">
                Wake-on-WAN: gebruik Tailscale/WireGuard i.p.v. open poorten. HTTPS: stel een NPM reverse proxy in op ProxyWake zelf.
              </Alert>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Snackbar open={notification.open} autoHideDuration={4000} onClose={() => setNotification({ ...notification, open: false })}>
        <Alert severity={notification.severity}>{notification.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default SettingsPage;
