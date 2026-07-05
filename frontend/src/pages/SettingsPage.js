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
import { useTranslation } from 'react-i18next';
import { api } from '../api/client';
import LanguageSwitcher from '../components/LanguageSwitcher';
import { useThemeMode } from '../context/ThemeContext';

const SettingsPage = () => {
  const { t } = useTranslation();
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
    show(t('settings.exportDone'));
  };

  const handleImport = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    const data = JSON.parse(text);
    const result = await api.importDevices(data.devices || data, true);
    show(t('settings.importDone', { count: result.imported }));
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>{t('settings.title')}</Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>{t('settings.subtitle')}</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>{t('settings.themeSection')}</Typography>
              <Button variant="outlined" startIcon={mode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />} onClick={toggleTheme}>
                {mode === 'dark' ? t('common.switchToLight') : t('common.switchToDark')}
              </Button>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>{t('common.language')}</Typography>
                <LanguageSwitcher fullWidth />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>{t('settings.apiKeySection')}</Typography>
              <TextField fullWidth value={settings?.api_key || ''} InputProps={{ readOnly: true }} sx={{ mb: 2 }} />
              <Button variant="outlined" startIcon={<VpnKeyIcon />} onClick={() => api.rotateApiKey().then((result) => { setSettings({ ...settings, api_key: result.api_key }); show(result.message); })}>
                {t('settings.rotateKey')}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>{t('settings.passwordSection')}</Typography>
              <TextField fullWidth type="password" label={t('settings.newPassword')} value={password} onChange={(e) => setPassword(e.target.value)} sx={{ mb: 2 }} />
              <Button variant="contained" onClick={() => api.updatePassword(password).then(() => show(t('messages.PASSWORD_UPDATED')))}>{t('common.save')}</Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>{t('settings.exportSection')}</Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Button variant="outlined" onClick={handleExport}>{t('settings.exportJson')}</Button>
                <Button variant="outlined" component="label">
                  {t('settings.importJson')}
                  <input hidden type="file" accept="application/json" onChange={handleImport} />
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>{t('settings.observability')}</Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {t('settings.observabilityText')}
              </Typography>
              <Alert severity="info">
                {t('settings.securityHint')}
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
