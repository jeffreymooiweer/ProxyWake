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
  TextField,
  Typography,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { api } from '../api/client';

const AutomationPage = () => {
  const { t } = useTranslation();
  const [webhooks, setWebhooks] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [devices, setDevices] = useState([]);
  const [hookForm, setHookForm] = useState({ name: '', url: '', events: ['wake_failed', 'wake_success'] });
  const [scheduleForm, setScheduleForm] = useState({ device_id: '', hour: 7, minute: 0 });
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  const load = async () => {
    const [hooks, scheds, devs] = await Promise.all([api.getWebhooks(), api.getSchedules(), api.getDevices(false)]);
    setWebhooks(hooks);
    setSchedules(scheds);
    setDevices(devs);
  };

  useEffect(() => { load().catch((err) => setNotification({ open: true, message: err.message, severity: 'error' })); }, []);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>{t('automation.title')}</Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>{t('automation.subtitle')}</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>{t('automation.webhooks')}</Typography>
              <TextField fullWidth label={t('automation.webhookName')} value={hookForm.name} onChange={(e) => setHookForm({ ...hookForm, name: e.target.value })} sx={{ mb: 2 }} />
              <TextField fullWidth label={t('automation.webhookUrl')} value={hookForm.url} onChange={(e) => setHookForm({ ...hookForm, url: e.target.value })} sx={{ mb: 2 }} />
              <Button variant="contained" onClick={() => api.createWebhook(hookForm).then(load)}>{t('automation.addWebhook')}</Button>
              <Box sx={{ mt: 2 }}>
                {webhooks.map((hook) => (
                  <Box key={hook.id} sx={{ display: 'flex', justifyContent: 'space-between', py: 1, borderBottom: '1px solid rgba(148,163,184,0.12)' }}>
                    <Typography>{hook.name}</Typography>
                    <Button size="small" color="error" onClick={() => api.deleteWebhook(hook.id).then(load)}>{t('common.remove')}</Button>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>{t('automation.scheduledWake')}</Typography>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>{t('automation.device')}</InputLabel>
                <Select value={scheduleForm.device_id} label={t('automation.device')} onChange={(e) => setScheduleForm({ ...scheduleForm, device_id: e.target.value })}>
                  {devices.map((device) => <MenuItem key={device.id} value={device.id}>{device.name}</MenuItem>)}
                </Select>
              </FormControl>
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={6}><TextField fullWidth type="number" label={t('automation.hour')} value={scheduleForm.hour} onChange={(e) => setScheduleForm({ ...scheduleForm, hour: Number(e.target.value) })} /></Grid>
                <Grid item xs={6}><TextField fullWidth type="number" label={t('automation.minute')} value={scheduleForm.minute} onChange={(e) => setScheduleForm({ ...scheduleForm, minute: Number(e.target.value) })} /></Grid>
              </Grid>
              <Button variant="contained" onClick={() => api.createSchedule(scheduleForm).then(load)}>{t('automation.addSchedule')}</Button>
              <Box sx={{ mt: 2 }}>
                {schedules.map((schedule) => (
                  <Box key={schedule.id} sx={{ display: 'flex', justifyContent: 'space-between', py: 1, borderBottom: '1px solid rgba(148,163,184,0.12)' }}>
                    <Typography>{schedule.device_name} — {String(schedule.hour).padStart(2, '0')}:{String(schedule.minute).padStart(2, '0')}</Typography>
                    <Button size="small" color="error" onClick={() => api.deleteSchedule(schedule.id).then(load)}>{t('common.remove')}</Button>
                  </Box>
                ))}
              </Box>
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

export default AutomationPage;
