import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Chip,
  Grid,
  LinearProgress,
  Typography,
} from '@mui/material';
import DevicesIcon from '@mui/icons-material/Devices';
import WifiIcon from '@mui/icons-material/Wifi';
import WifiOffIcon from '@mui/icons-material/WifiOff';
import BoltIcon from '@mui/icons-material/Bolt';
import { useTranslation } from 'react-i18next';
import { api } from '../api/client';

const StatCard = ({ title, value, subtitle, icon, color = 'primary' }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography color="text.secondary" variant="body2">{title}</Typography>
          <Typography variant="h4" sx={{ mt: 1, mb: 0.5 }}>{value}</Typography>
          <Typography color="text.secondary" variant="body2">{subtitle}</Typography>
        </Box>
        <Box
          sx={{
            width: 48,
            height: 48,
            borderRadius: 3,
            display: 'grid',
            placeItems: 'center',
            bgcolor: `${color}.main`,
            color: 'background.default',
            opacity: 0.9,
          }}
        >
          {icon}
        </Box>
      </Box>
    </CardContent>
  </Card>
);

const DashboardPage = ({ onNavigate }) => {
  const { t } = useTranslation();
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await api.getDevices(true);
        setDevices(data);
      } finally {
        setLoading(false);
      }
    };
    load();
    const interval = setInterval(load, 15000);
    return () => clearInterval(interval);
  }, []);

  const onlineCount = devices.filter((device) => device.online).length;
  const offlineCount = devices.length - onlineCount;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>{t('dashboard.title')}</Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        {t('dashboard.subtitle')}
      </Typography>

      {loading && <LinearProgress sx={{ mb: 3 }} />}

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <StatCard
            title={t('dashboard.devices')}
            value={devices.length}
            subtitle={t('dashboard.devicesSub')}
            icon={<DevicesIcon />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <StatCard
            title={t('dashboard.online')}
            value={onlineCount}
            subtitle={t('dashboard.onlineSub')}
            icon={<WifiIcon />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <StatCard
            title={t('dashboard.offline')}
            value={offlineCount}
            subtitle={t('dashboard.offlineSub')}
            icon={<WifiOffIcon />}
            color="warning"
          />
        </Grid>
      </Grid>

      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <BoltIcon color="secondary" />
            <Typography variant="h6">{t('dashboard.quickStart')}</Typography>
          </Box>
          <Typography color="text.secondary" paragraph>
            {t('dashboard.quickStartText')}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip label={t('dashboard.addDevice')} onClick={() => onNavigate(1)} clickable color="primary" />
            <Chip label={t('dashboard.setupNpm')} onClick={() => onNavigate(2)} clickable color="secondary" />
          </Box>
        </CardContent>
      </Card>

      {devices.length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>{t('dashboard.statusOverview')}</Typography>
            <Grid container spacing={2}>
              {devices.map((device) => (
                <Grid item xs={12} sm={6} key={device.id}>
                  <Box
                    sx={{
                      p: 2,
                      borderRadius: 3,
                      border: '1px solid rgba(148, 163, 184, 0.12)',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <Box>
                      <Typography fontWeight={600}>{device.name}</Typography>
                      <Typography variant="body2" color="text.secondary">{device.domain}</Typography>
                    </Box>
                    <Chip
                      size="small"
                      label={device.online ? t('common.online') : t('common.offline')}
                      color={device.online ? 'success' : 'default'}
                    />
                  </Box>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default DashboardPage;
