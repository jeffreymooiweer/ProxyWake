import React, { useEffect, useState } from 'react';
import { Box, Card, CardContent, CircularProgress, LinearProgress, Typography } from '@mui/material';
import PowerSettingsNewIcon from '@mui/icons-material/PowerSettingsNew';
import { api } from '../api/client';

const WaitingPage = () => {
  const params = new URLSearchParams(window.location.search);
  const domain = params.get('domain') || '';
  const [status, setStatus] = useState({ online: false, name: domain });
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('Apparaat wordt opgestart...');

  useEffect(() => {
    if (!domain) return undefined;

    let active = true;
    let ticks = 0;

    const poll = async () => {
      try {
        await api.publicWake(domain);
      } catch {
        // wake may already be in progress
      }
      try {
        const data = await api.publicStatus(domain);
        if (!active) return;
        setStatus(data);
        if (data.online) {
          setMessage('Apparaat is online! Doorsturen...');
          setProgress(100);
          setTimeout(() => {
            window.location.href = `https://${domain}`;
          }, 1500);
        } else {
          ticks += 1;
          setProgress(Math.min(95, ticks * 5));
          setMessage(`Wachten op ${data.name || domain}... (${ticks * 3}s)`);
        }
      } catch {
        setMessage('Kon status niet ophalen. Opnieuw proberen...');
      }
    };

    poll();
    const interval = setInterval(poll, 3000);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [domain]);

  if (!domain) {
    return (
      <Box sx={{ minHeight: '100vh', display: 'grid', placeItems: 'center', p: 2 }}>
        <Card sx={{ maxWidth: 480, width: '100%' }}>
          <CardContent>
            <Typography>Geen domein opgegeven. Gebruik: /waiting?domain=jouw.domein.nl</Typography>
          </CardContent>
        </Card>
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', display: 'grid', placeItems: 'center', p: 2 }}>
      <Card sx={{ maxWidth: 520, width: '100%' }}>
        <CardContent sx={{ textAlign: 'center', p: 4 }}>
          <PowerSettingsNewIcon color="secondary" sx={{ fontSize: 56, mb: 2 }} />
          <Typography variant="h5" gutterBottom>{status.name || domain}</Typography>
          <Typography color="text.secondary" sx={{ mb: 3 }}>{message}</Typography>
          {progress < 100 ? <CircularProgress sx={{ mb: 2 }} /> : null}
          <LinearProgress variant="determinate" value={progress} sx={{ height: 8, borderRadius: 4 }} />
        </CardContent>
      </Card>
    </Box>
  );
};

export default WaitingPage;
