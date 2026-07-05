import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Chip,
  Grid,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { api } from '../api/client';

const StatisticsPage = () => {
  const { t, i18n } = useTranslation();
  const [stats, setStats] = useState(null);
  const [events, setEvents] = useState([]);

  useEffect(() => {
    Promise.all([api.getStats(), api.getWakeEvents(30)])
      .then(([statsData, eventsData]) => {
        setStats(statsData);
        setEvents(eventsData);
      })
      .catch(() => {});
  }, []);

  if (!stats) return <LinearProgress />;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>{t('statistics.title')}</Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>{t('statistics.subtitle')}</Typography>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}><Card><CardContent><Typography color="text.secondary">{t('statistics.totalWakes')}</Typography><Typography variant="h4">{stats.total_wake_events}</Typography></CardContent></Card></Grid>
        <Grid item xs={12} md={4}><Card><CardContent><Typography color="text.secondary">{t('statistics.last7Days')}</Typography><Typography variant="h4">{stats.wake_events_7d}</Typography></CardContent></Card></Grid>
        <Grid item xs={12} md={4}><Card><CardContent><Typography color="text.secondary">{t('statistics.successful')}</Typography><Typography variant="h4">{stats.successful_wakes}</Typography></CardContent></Card></Grid>
      </Grid>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>{t('statistics.perDevice')}</Typography>
          <Grid container spacing={2}>
            {stats.devices.map((item) => (
              <Grid item xs={12} md={6} key={item.device.id}>
                <Box sx={{ p: 2, borderRadius: 3, border: '1px solid rgba(148,163,184,0.12)' }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography fontWeight={600}>{item.device.name}</Typography>
                    <Chip size="small" label={item.device.online ? t('common.online') : t('common.offline')} color={item.device.online ? 'success' : 'default'} />
                  </Box>
                  <Typography variant="body2" color="text.secondary">{t('statistics.wakeCount', { count: item.wake_count })}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {t('statistics.avgBoot', { value: item.avg_wake_ms ? `${Math.round(item.avg_wake_ms / 1000)}s` : t('statistics.noBootData') })}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>{t('statistics.recentEvents')}</Typography>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>{t('statistics.time')}</TableCell>
                <TableCell>{t('automation.device')}</TableCell>
                <TableCell>{t('statistics.source')}</TableCell>
                <TableCell>{t('statistics.status')}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {events.map((event) => (
                <TableRow key={event.id}>
                  <TableCell>{new Date(event.created_at).toLocaleString(i18n.language)}</TableCell>
                  <TableCell>{event.device_name || event.domain}</TableCell>
                  <TableCell>{event.source}</TableCell>
                  <TableCell>
                    <Chip size="small" label={event.skipped ? t('common.skipped') : event.success ? t('common.ok') : t('common.error')} color={event.success ? 'success' : 'error'} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </Box>
  );
};

export default StatisticsPage;
