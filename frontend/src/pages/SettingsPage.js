import React, { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Checkbox,
  FormControl,
  FormControlLabel,
  FormGroup,
  Grid,
  InputLabel,
  MenuItem,
  Select,
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
  const [selectedScopes, setSelectedScopes] = useState([]);
  const [logLevel, setLogLevel] = useState('INFO');
  const [notifications, setNotifications] = useState({
    slack_enabled: false,
    slack_webhook_url: '',
    telegram_enabled: false,
    telegram_bot_token: '',
    telegram_chat_id: '',
  });
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    api.getSettings().then((data) => {
      setSettings(data);
      setSelectedScopes(data.api_scopes || []);
      setLogLevel(data.log_level || 'INFO');
      setNotifications(data.notifications || {
        slack_enabled: false,
        slack_webhook_url: '',
        telegram_enabled: false,
        telegram_bot_token: '',
        telegram_chat_id: '',
      });
    }).catch(() => {});
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

  const handleFullBackup = async () => {
    const data = await api.downloadBackup();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'proxywake-full-backup.json';
    link.click();
    show(t('settings.fullBackupDone'));
  };

  const handleFullRestore = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    const data = JSON.parse(text);
    const result = await api.restoreBackup(data, true);
    show(t('settings.fullRestoreDone', { devices: result.restored?.devices || 0 }));
  };

  const toggleScope = (scope) => {
    setSelectedScopes((prev) => (
      prev.includes(scope) ? prev.filter((item) => item !== scope) : [...prev, scope]
    ));
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
                <Button variant="outlined" onClick={handleFullBackup}>{t('settings.fullBackup')}</Button>
                <Button variant="outlined" component="label">
                  {t('settings.fullRestore')}
                  <input hidden type="file" accept="application/json" onChange={handleFullRestore} />
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>{t('settings.apiScopesSection')}</Typography>
              <FormGroup>
                {(settings?.available_api_scopes || []).map((scope) => (
                  <FormControlLabel
                    key={scope}
                    control={<Checkbox checked={selectedScopes.includes(scope)} onChange={() => toggleScope(scope)} />}
                    label={t(`settings.apiScopes.${scope}`, scope)}
                  />
                ))}
              </FormGroup>
              <Button sx={{ mt: 2 }} variant="contained" onClick={() => api.updateApiScopes(selectedScopes).then((result) => show(t('settings.scopesUpdated', { scopes: result.api_scopes.join(', ') })))}>
                {t('common.save')}
              </Button>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                <a href="/api/docs" target="_blank" rel="noreferrer">{t('settings.openApiDocs')}</a>
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>{t('settings.notificationsSection')}</Typography>
              <FormControlLabel
                control={<Checkbox checked={notifications.slack_enabled} onChange={(e) => setNotifications({ ...notifications, slack_enabled: e.target.checked })} />}
                label={t('settings.slackEnabled')}
              />
              <TextField fullWidth label={t('settings.slackWebhook')} value={notifications.slack_webhook_url} onChange={(e) => setNotifications({ ...notifications, slack_webhook_url: e.target.value })} sx={{ mb: 2 }} />
              <FormControlLabel
                control={<Checkbox checked={notifications.telegram_enabled} onChange={(e) => setNotifications({ ...notifications, telegram_enabled: e.target.checked })} />}
                label={t('settings.telegramEnabled')}
              />
              <TextField fullWidth label={t('settings.telegramToken')} value={notifications.telegram_bot_token} onChange={(e) => setNotifications({ ...notifications, telegram_bot_token: e.target.value })} sx={{ mb: 1 }} />
              <TextField fullWidth label={t('settings.telegramChatId')} value={notifications.telegram_chat_id} onChange={(e) => setNotifications({ ...notifications, telegram_chat_id: e.target.value })} sx={{ mb: 2 }} />
              <Button variant="contained" onClick={() => api.updateNotifications(notifications).then(() => show(t('settings.notificationsUpdated')))}>
                {t('common.save')}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>{t('settings.loggingSection')}</Typography>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>{t('settings.logLevel')}</InputLabel>
                <Select value={logLevel} label={t('settings.logLevel')} onChange={(e) => setLogLevel(e.target.value)}>
                  {['DEBUG', 'INFO', 'WARNING', 'ERROR'].map((level) => (
                    <MenuItem key={level} value={level}>{level}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Button variant="contained" onClick={() => api.updateLogLevel(logLevel).then(() => show(t('settings.logLevelUpdated')))}>
                {t('common.save')}
              </Button>
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
