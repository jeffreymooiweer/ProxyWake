import React, { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  FormControlLabel,
  Grid,
  LinearProgress,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  Snackbar,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import PowerSettingsNewIcon from '@mui/icons-material/PowerSettingsNew';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import SearchIcon from '@mui/icons-material/Search';
import { useTranslation } from 'react-i18next';
import { api } from '../api/client';

const emptyForm = { name: '', domain: '', ip: '', mac: '', group_id: '', use_broadcast: false, wake_cooldown_seconds: 30 };

const DevicesPage = () => {
  const { t } = useTranslation();
  const [devices, setDevices] = useState([]);
  const [groups, setGroups] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editing, setEditing] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [scanOpen, setScanOpen] = useState(false);
  const [scanSubnet, setScanSubnet] = useState('192.168.1.0/24');
  const [scanResults, setScanResults] = useState([]);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });
  const [wakeJobs, setWakeJobs] = useState({});

  const loadDevices = async () => {
    const [data, groupData] = await Promise.all([api.getDevices(true), api.getGroups()]);
    setDevices(data);
    setGroups(groupData);
  };

  useEffect(() => {
    loadDevices().catch((err) => setNotification({ open: true, message: err.message, severity: 'error' }));
    const interval = setInterval(() => {
      loadDevices().catch(() => {});
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  const showMessage = (message, severity = 'success') => {
    setNotification({ open: true, message, severity });
  };

  const handleCreate = async (event) => {
    event.preventDefault();
    try {
      await api.createDevice(form);
      setForm(emptyForm);
      await loadDevices();
      showMessage(t('devices.added'));
    } catch (err) {
      showMessage(err.message, 'error');
    }
  };

  const openEdit = (device) => {
    setEditing(device);
    setDialogOpen(true);
  };

  const handleUpdate = async () => {
    try {
      await api.updateDevice(editing.id, editing);
      setDialogOpen(false);
      setEditing(null);
      await loadDevices();
      showMessage(t('devices.updated'));
    } catch (err) {
      showMessage(err.message, 'error');
    }
  };

  const handleDelete = async (device) => {
    if (!window.confirm(t('devices.deleteConfirm', { name: device.name }))) return;
    try {
      await api.deleteDevice(device.id);
      await loadDevices();
      showMessage(t('devices.deleted'));
    } catch (err) {
      showMessage(err.message, 'error');
    }
  };

  const handleWake = async (device) => {
    try {
      const started = await api.wakeDeviceVerify(device.id);
      setWakeJobs((prev) => ({ ...prev, [device.id]: started }));

      const poll = async () => {
        const job = await api.getWakeJob(started.job_id);
        setWakeJobs((prev) => ({ ...prev, [device.id]: job }));

        if (['online', 'failed', 'skipped', 'cooldown'].includes(job.status)) {
          if (job.message_code) {
            const translated = t(`messages.${job.message_code}`, {
              name: device.name,
              seconds: Math.round((job.waited_ms || 0) / 1000),
            });
            showMessage(translated, job.status === 'online' || job.status === 'skipped' ? 'success' : 'error');
          }
          setWakeJobs((prev) => {
            const next = { ...prev };
            delete next[device.id];
            return next;
          });
          await loadDevices();
          return;
        }
        setTimeout(poll, 1500);
      };
      poll();
    } catch (err) {
      showMessage(err.message, 'error');
    }
  };

  const wakeStatusLabel = (status) => {
    const key = `devices.wakeStatus.${status}`;
    const translated = t(key);
    return translated === key ? status : translated;
  };

  const copyText = async (text) => {
    await navigator.clipboard.writeText(text);
    showMessage(t('common.copied'));
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" gutterBottom>{t('devices.title')}</Typography>
          <Typography color="text.secondary">{t('devices.subtitle')}</Typography>
        </Box>
        <Button variant="outlined" startIcon={<SearchIcon />} onClick={() => setScanOpen(true)}>{t('devices.scanNetwork')}</Button>
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>{t('devices.newDevice')}</Typography>
          <Box component="form" onSubmit={handleCreate}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  label={t('devices.name')}
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder={t('devices.namePlaceholder')}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  required
                  label={t('devices.domain')}
                  value={form.domain}
                  onChange={(e) => setForm({ ...form, domain: e.target.value })}
                  placeholder={t('devices.domainPlaceholder')}
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <TextField
                  fullWidth
                  required
                  label={t('devices.ip')}
                  value={form.ip}
                  onChange={(e) => setForm({ ...form, ip: e.target.value })}
                  placeholder={t('devices.ipPlaceholder')}
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <TextField
                  fullWidth
                  required
                  label={t('devices.mac')}
                  value={form.mac}
                  onChange={(e) => setForm({ ...form, mac: e.target.value })}
                  placeholder={t('devices.macPlaceholder')}
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <TextField
                  fullWidth
                  type="number"
                  label={t('devices.cooldown')}
                  value={form.wake_cooldown_seconds}
                  onChange={(e) => setForm({ ...form, wake_cooldown_seconds: Number(e.target.value) })}
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <FormControl fullWidth>
                  <InputLabel>{t('devices.group')}</InputLabel>
                  <Select value={form.group_id} label={t('devices.group')} onChange={(e) => setForm({ ...form, group_id: e.target.value })}>
                    <MenuItem value="">{t('common.none')}</MenuItem>
                    {groups.map((group) => <MenuItem key={group.id} value={group.id}>{group.name}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={2}>
                <FormControlLabel
                  control={<Switch checked={form.use_broadcast} onChange={(e) => setForm({ ...form, use_broadcast: e.target.checked })} />}
                  label={t('devices.broadcast')}
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <Button
                  fullWidth
                  type="submit"
                  variant="contained"
                  startIcon={<AddIcon />}
                  sx={{ height: '56px' }}
                >
                  {t('devices.addButton')}
                </Button>
              </Grid>
            </Grid>
          </Box>
        </CardContent>
      </Card>

      <Card>
        <CardContent sx={{ overflowX: 'auto' }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>{t('devices.name')}</TableCell>
                <TableCell>{t('devices.domain')}</TableCell>
                <TableCell>{t('devices.ip')}</TableCell>
                <TableCell>{t('devices.mac')}</TableCell>
                <TableCell>{t('statistics.status')}</TableCell>
                <TableCell align="right">{t('common.edit')}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {devices.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography color="text.secondary" sx={{ py: 4 }}>
                      {t('devices.empty')}
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                devices.map((device) => (
                  <TableRow key={device.id} hover>
                    <TableCell>{device.name}</TableCell>
                    <TableCell>{device.domain}</TableCell>
                    <TableCell>{device.ip}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {device.mac}
                        <Tooltip title={t('devices.copyMac')}>
                          <IconButton size="small" onClick={() => copyText(device.mac)}>
                            <ContentCopyIcon fontSize="inherit" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5, minWidth: 100 }}>
                        <Chip
                          size="small"
                          label={device.online ? t('common.online') : t('common.offline')}
                          color={device.online ? 'success' : 'default'}
                        />
                        {device.last_wake_duration_seconds != null && (
                          <Typography variant="caption" color="text.secondary">
                            {t('devices.lastWake', { seconds: device.last_wake_duration_seconds })}
                          </Typography>
                        )}
                        {wakeJobs[device.id] && !['online', 'failed', 'skipped', 'cooldown'].includes(wakeJobs[device.id].status) && (
                          <Box>
                            <Typography variant="caption" color="secondary.main">
                              {wakeStatusLabel(wakeJobs[device.id].status)}
                            </Typography>
                            <LinearProgress color="secondary" sx={{ mt: 0.5 }} />
                          </Box>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title={t('devices.testWake')}>
                        <IconButton color="success" onClick={() => handleWake(device)}>
                          <PowerSettingsNewIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title={t('common.edit')}>
                        <IconButton onClick={() => openEdit(device)}>
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title={t('common.delete')}>
                        <IconButton color="error" onClick={() => handleDelete(device)}>
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>{t('devices.editTitle')}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label={t('devices.name')}
                value={editing?.name || ''}
                onChange={(e) => setEditing({ ...editing, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label={t('devices.domain')}
                value={editing?.domain || ''}
                onChange={(e) => setEditing({ ...editing, domain: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('devices.ip')}
                value={editing?.ip || ''}
                onChange={(e) => setEditing({ ...editing, ip: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('devices.mac')}
                value={editing?.mac || ''}
                onChange={(e) => setEditing({ ...editing, mac: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>{t('devices.statusCheckType')}</InputLabel>
                <Select
                  value={editing?.status_check_type || 'ping'}
                  label={t('devices.statusCheckType')}
                  onChange={(e) => setEditing({ ...editing, status_check_type: e.target.value })}
                >
                  <MenuItem value="ping">{t('devices.statusCheck.ping')}</MenuItem>
                  <MenuItem value="tcp">{t('devices.statusCheck.tcp')}</MenuItem>
                  <MenuItem value="http">{t('devices.statusCheck.http')}</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label={t('devices.statusCheckPort')}
                value={editing?.status_check_port ?? ''}
                onChange={(e) => setEditing({ ...editing, status_check_port: e.target.value ? Number(e.target.value) : null })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label={t('devices.statusCheckUrl')}
                value={editing?.status_check_url || ''}
                onChange={(e) => setEditing({ ...editing, status_check_url: e.target.value })}
                placeholder="http://192.168.1.50:32400/identity"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label={t('devices.wakeTimeout')}
                value={editing?.wake_timeout_seconds ?? 120}
                onChange={(e) => setEditing({ ...editing, wake_timeout_seconds: Number(e.target.value) })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>{t('common.cancel')}</Button>
          <Button variant="contained" onClick={handleUpdate}>{t('common.save')}</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={scanOpen} onClose={() => setScanOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>{t('devices.scannerTitle')}</DialogTitle>
        <DialogContent>
          <TextField fullWidth label={t('devices.subnet')} value={scanSubnet} onChange={(e) => setScanSubnet(e.target.value)} sx={{ mt: 1, mb: 2 }} />
          <Button variant="contained" onClick={() => api.scanNetwork({ subnet: scanSubnet }).then((result) => setScanResults(result.hosts || []))}>
            {t('devices.startScan')}
          </Button>
          {scanResults.map((host) => (
            <Box key={host.ip} sx={{ display: 'flex', justifyContent: 'space-between', py: 1 }}>
              <Typography>{host.ip}</Typography>
              <Button size="small" onClick={() => { setForm({ ...form, ip: host.ip }); setScanOpen(false); }}>{t('devices.useIp')}</Button>
            </Box>
          ))}
        </DialogContent>
        <DialogActions><Button onClick={() => setScanOpen(false)}>{t('common.close')}</Button></DialogActions>
      </Dialog>

      <Snackbar
        open={notification.open}
        autoHideDuration={5000}
        onClose={() => setNotification({ ...notification, open: false })}
      >
        <Alert severity={notification.severity} onClose={() => setNotification({ ...notification, open: false })}>
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default DevicesPage;
