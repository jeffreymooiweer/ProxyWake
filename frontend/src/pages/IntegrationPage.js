import React, { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Snackbar,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { useTranslation } from 'react-i18next';
import { api } from '../api/client';

const CodeBlock = ({ title, description, value, onCopy, copyLabel }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Typography variant="h6" gutterBottom>{title}</Typography>
      <Typography color="text.secondary" sx={{ mb: 2 }}>{description}</Typography>
      <Box component="pre" sx={{ p: 2, borderRadius: 3, bgcolor: 'rgba(15, 23, 42, 0.9)', overflowX: 'auto', fontSize: '0.85rem', whiteSpace: 'pre-wrap', mb: 2 }}>{value}</Box>
      <Button variant="outlined" startIcon={<ContentCopyIcon />} onClick={() => onCopy(value)}>{copyLabel}</Button>
    </CardContent>
  </Card>
);

const IntegrationPage = () => {
  const { t } = useTranslation();
  const [tab, setTab] = useState(0);
  const [config, setConfig] = useState(null);
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('');
  const [haConfig, setHaConfig] = useState('');
  const [baseUrl, setBaseUrl] = useState('');
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    Promise.all([api.getSettings(), api.getNpmConfig(), api.getDevices(false)])
      .then(([settings, configData, deviceData]) => {
        setBaseUrl(settings.proxywake_url);
        setConfig(configData);
        setDevices(deviceData);
      })
      .catch((err) => setNotification({ open: true, message: err.message, severity: 'error' }));
  }, []);

  const refresh = async () => {
    const configData = await api.getNpmConfig(baseUrl);
    setConfig(configData);
  };

  const loadHa = async (deviceId) => {
    const data = await api.getNpmConfigForDevice(deviceId, baseUrl);
    setHaConfig(data.home_assistant);
  };

  const copyText = async (text) => {
    await navigator.clipboard.writeText(text);
    setNotification({ open: true, message: t('common.copied'), severity: 'success' });
  };

  const testNpm = async () => {
    if (!selectedDevice) return;
    const result = await api.testNpm(selectedDevice);
    setNotification({
      open: true,
      message: result.success ? t('integration.testSuccess') : t('integration.testFailed', { code: result.status_code }),
      severity: result.success ? 'success' : 'error',
    });
  };

  if (!config) return null;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>{t('integration.title')}</Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>{t('integration.subtitle')}</Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={9}>
              <TextField fullWidth label={t('integration.urlLabel')} value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)} />
            </Grid>
            <Grid item xs={12} md={3}>
              <Button fullWidth variant="contained" sx={{ height: '56px' }} onClick={refresh}>{t('integration.refresh')}</Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Tabs value={tab} onChange={(_, value) => setTab(value)} sx={{ mb: 3 }}>
        <Tab label={t('integration.tabs.npm')} />
        <Tab label={t('integration.tabs.traefik')} />
        <Tab label={t('integration.tabs.caddy')} />
        <Tab label={t('integration.tabs.ha')} />
        <Tab label={t('integration.tabs.test')} />
      </Tabs>

      {tab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} lg={6}>
            <CodeBlock title={t('integration.npmGlobal')} description={t('integration.npmGlobalDesc')} value={config.npm.global_config} onCopy={copyText} copyLabel={t('common.copy')} />
          </Grid>
          <Grid item xs={12} lg={6}>
            <CodeBlock title={t('integration.npmHost')} description={t('integration.npmHostDesc')} value={config.npm.host_config} onCopy={copyText} copyLabel={t('common.copy')} />
          </Grid>
        </Grid>
      )}

      {tab === 1 && <CodeBlock title={t('integration.traefikTitle')} description={t('integration.traefikDesc')} value={config.traefik.config} onCopy={copyText} copyLabel={t('common.copy')} />}
      {tab === 2 && <CodeBlock title={t('integration.caddyTitle')} description={t('integration.caddyDesc')} value={config.caddy.config} onCopy={copyText} copyLabel={t('common.copy')} />}

      {tab === 3 && (
        <Card>
          <CardContent>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>{t('integration.haSelect')}</InputLabel>
              <Select value={selectedDevice} label={t('integration.haSelect')} onChange={(e) => { setSelectedDevice(e.target.value); loadHa(e.target.value); }}>
                {devices.map((device) => <MenuItem key={device.id} value={device.id}>{device.name}</MenuItem>)}
              </Select>
            </FormControl>
            <Box component="pre" sx={{ p: 2, borderRadius: 3, bgcolor: 'rgba(15, 23, 42, 0.9)', whiteSpace: 'pre-wrap' }}>{haConfig || t('integration.haPlaceholder')}</Box>
          </CardContent>
        </Card>
      )}

      {tab === 4 && (
        <Card>
          <CardContent>
            <Typography gutterBottom>{t('integration.testDesc')}</Typography>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>{t('integration.haSelect')}</InputLabel>
              <Select value={selectedDevice} label={t('integration.haSelect')} onChange={(e) => setSelectedDevice(e.target.value)}>
                {devices.map((device) => <MenuItem key={device.id} value={device.id}>{device.name}</MenuItem>)}
              </Select>
            </FormControl>
            <Button variant="contained" startIcon={<PlayArrowIcon />} onClick={testNpm} disabled={!selectedDevice}>{t('integration.testButton')}</Button>
          </CardContent>
        </Card>
      )}

      <Snackbar open={notification.open} autoHideDuration={4000} onClose={() => setNotification({ ...notification, open: false })}>
        <Alert severity={notification.severity}>{notification.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default IntegrationPage;
