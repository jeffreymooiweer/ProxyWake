import React, { useEffect, useState } from 'react';
import { Box, Card, CardContent, CircularProgress, LinearProgress, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import AppLogo from '../components/AppLogo';
import { api } from '../api/client';

const WaitingPage = () => {
  const { t } = useTranslation();
  const params = new URLSearchParams(window.location.search);
  const domain = params.get('domain') || '';
  const [status, setStatus] = useState({ online: false, name: domain });
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState(t('waiting.starting'));

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
          setMessage(t('waiting.onlineRedirect'));
          setProgress(100);
          setTimeout(() => {
            window.location.href = `https://${domain}`;
          }, 1500);
        } else {
          ticks += 1;
          setProgress(Math.min(95, ticks * 5));
          setMessage(t('waiting.waitingFor', { name: data.name || domain, seconds: ticks * 3 }));
        }
      } catch {
        setMessage(t('waiting.statusError'));
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
            <Typography>{t('waiting.noDomain')}</Typography>
          </CardContent>
        </Card>
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', display: 'grid', placeItems: 'center', p: 2 }}>
      <Card sx={{ maxWidth: 520, width: '100%' }}>
        <CardContent sx={{ textAlign: 'center', p: 4 }}>
          <AppLogo size={72} sx={{ mx: 'auto', mb: 2, display: 'block' }} />
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
