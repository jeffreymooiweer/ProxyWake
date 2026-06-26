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
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import KeyIcon from '@mui/icons-material/Key';
import IntegrationInstructionsIcon from '@mui/icons-material/IntegrationInstructions';
import { api } from '../api/client';

const CodeBlock = ({ title, description, value, onCopy }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Typography variant="h6" gutterBottom>{title}</Typography>
      <Typography color="text.secondary" sx={{ mb: 2 }}>{description}</Typography>
      <Box
        component="pre"
        sx={{
          p: 2,
          borderRadius: 3,
          bgcolor: 'rgba(15, 23, 42, 0.9)',
          border: '1px solid rgba(148, 163, 184, 0.12)',
          overflowX: 'auto',
          fontSize: '0.85rem',
          lineHeight: 1.5,
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
          mb: 2,
        }}
      >
        {value}
      </Box>
      <Button variant="outlined" startIcon={<ContentCopyIcon />} onClick={() => onCopy(value)}>
        Kopiëren
      </Button>
    </CardContent>
  </Card>
);

const IntegrationPage = () => {
  const [settings, setSettings] = useState(null);
  const [npmConfig, setNpmConfig] = useState(null);
  const [baseUrl, setBaseUrl] = useState('');
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    const load = async () => {
      const [settingsData, configData] = await Promise.all([
        api.getSettings(),
        api.getNpmConfig(),
      ]);
      setSettings(settingsData);
      setBaseUrl(settingsData.proxywake_url);
      setNpmConfig(configData);
    };
    load().catch((err) => setNotification({ open: true, message: err.message, severity: 'error' }));
  }, []);

  const refreshConfig = async () => {
    const configData = await api.getNpmConfig(baseUrl);
    setNpmConfig(configData);
  };

  const copyText = async (text) => {
    await navigator.clipboard.writeText(text);
    setNotification({ open: true, message: 'Gekopieerd naar klembord.', severity: 'success' });
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>NPM Integratie</Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Koppel ProxyWake aan Nginx Proxy Manager zodat apparaten automatisch ontwaken bij het eerste bezoek.
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <KeyIcon color="secondary" />
            <Typography variant="h6">API-sleutel</Typography>
          </Box>
          <Typography color="text.secondary" sx={{ mb: 2 }}>
            Bewaar deze sleutel veilig. NPM gebruikt deze om wake-verzoeken te authenticeren.
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <TextField
              fullWidth
              value={settings?.api_key || ''}
              InputProps={{ readOnly: true }}
              sx={{ flex: 1, minWidth: 280 }}
            />
            <Button variant="outlined" onClick={() => copyText(settings?.api_key || '')}>
              Sleutel kopiëren
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <IntegrationInstructionsIcon color="primary" />
            <Typography variant="h6">ProxyWake URL</Typography>
          </Box>
          <Typography color="text.secondary" sx={{ mb: 2 }}>
            Gebruik het interne IP-adres dat NPM kan bereiken (niet localhost).
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={9}>
              <TextField
                fullWidth
                label="ProxyWake basis-URL"
                value={baseUrl}
                onChange={(e) => setBaseUrl(e.target.value)}
                placeholder="http://192.168.1.10:8462"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <Button fullWidth variant="contained" sx={{ height: '56px' }} onClick={refreshConfig}>
                Configuratie vernieuwen
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {npmConfig && (
        <>
          <Grid container spacing={3}>
            <Grid item xs={12} lg={6}>
              <CodeBlock
                title="Stap 1 — Globale NPM-configuratie"
                description="Plak dit eenmalig in NPM onder Custom Nginx Configuration (server_proxy.conf of vergelijkbaar)."
                value={npmConfig.global_config}
                onCopy={copyText}
              />
            </Grid>
            <Grid item xs={12} lg={6}>
              <CodeBlock
                title="Stap 2 — Per proxy host (Advanced)"
                description="Voeg dit toe aan de Advanced-tab van elke proxy host die Wake-on-LAN moet triggeren."
                value={npmConfig.host_config}
                onCopy={copyText}
              />
            </Grid>
          </Grid>

          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>Installatie-instructies</Typography>
              {npmConfig.instructions.map((step, index) => (
                <Typography key={step} sx={{ mb: 1 }}>
                  {index + 1}. {step}
                </Typography>
              ))}
              <Alert severity="info" sx={{ mt: 2 }}>
                ProxyWake gebruikt de nginx mirror-module: bij elk bezoek wordt op de achtergrond een wake-verzoek gestuurd zonder de gebruiker te vertragen.
              </Alert>
            </CardContent>
          </Card>
        </>
      )}

      <Snackbar
        open={notification.open}
        autoHideDuration={4000}
        onClose={() => setNotification({ ...notification, open: false })}
      >
        <Alert severity={notification.severity} onClose={() => setNotification({ ...notification, open: false })}>
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default IntegrationPage;
