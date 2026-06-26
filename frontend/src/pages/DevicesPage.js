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
import { api } from '../api/client';

const emptyForm = { name: '', domain: '', ip: '', mac: '', group_id: '', use_broadcast: false, wake_cooldown_seconds: 30 };

const DevicesPage = () => {
  const [devices, setDevices] = useState([]);
  const [groups, setGroups] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editing, setEditing] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [scanOpen, setScanOpen] = useState(false);
  const [scanSubnet, setScanSubnet] = useState('192.168.1.0/24');
  const [scanResults, setScanResults] = useState([]);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });

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
      showMessage('Apparaat succesvol toegevoegd.');
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
      showMessage('Apparaat bijgewerkt.');
    } catch (err) {
      showMessage(err.message, 'error');
    }
  };

  const handleDelete = async (device) => {
    if (!window.confirm(`Weet je zeker dat je "${device.name}" wilt verwijderen?`)) return;
    try {
      await api.deleteDevice(device.id);
      await loadDevices();
      showMessage('Apparaat verwijderd.');
    } catch (err) {
      showMessage(err.message, 'error');
    }
  };

  const handleWake = async (device) => {
    try {
      const result = await api.wakeDevice(device.id);
      showMessage(result.message);
    } catch (err) {
      showMessage(err.message, 'error');
    }
  };

  const copyText = async (text) => {
    await navigator.clipboard.writeText(text);
    showMessage('Gekopieerd naar klembord.');
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" gutterBottom>Apparaten</Typography>
          <Typography color="text.secondary">Koppel domeinen aan IP/MAC voor slimme Wake-on-LAN.</Typography>
        </Box>
        <Button variant="outlined" startIcon={<SearchIcon />} onClick={() => setScanOpen(true)}>Netwerk scannen</Button>
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Nieuw apparaat</Typography>
          <Box component="form" onSubmit={handleCreate}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  label="Naam (optioneel)"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="Bijv. NAS"
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  required
                  label="Domeinnaam"
                  value={form.domain}
                  onChange={(e) => setForm({ ...form, domain: e.target.value })}
                  placeholder="nas.jouwdomein.nl"
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <TextField
                  fullWidth
                  required
                  label="Intern IP"
                  value={form.ip}
                  onChange={(e) => setForm({ ...form, ip: e.target.value })}
                  placeholder="192.168.1.50"
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <TextField
                  fullWidth
                  required
                  label="MAC-adres"
                  value={form.mac}
                  onChange={(e) => setForm({ ...form, mac: e.target.value })}
                  placeholder="AA:BB:CC:DD:EE:FF"
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <TextField
                  fullWidth
                  type="number"
                  label="Cooldown (s)"
                  value={form.wake_cooldown_seconds}
                  onChange={(e) => setForm({ ...form, wake_cooldown_seconds: Number(e.target.value) })}
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <FormControl fullWidth>
                  <InputLabel>Groep</InputLabel>
                  <Select value={form.group_id} label="Groep" onChange={(e) => setForm({ ...form, group_id: e.target.value })}>
                    <MenuItem value="">Geen</MenuItem>
                    {groups.map((group) => <MenuItem key={group.id} value={group.id}>{group.name}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={2}>
                <FormControlLabel
                  control={<Switch checked={form.use_broadcast} onChange={(e) => setForm({ ...form, use_broadcast: e.target.checked })} />}
                  label="Broadcast WOL"
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
                  Toevoegen
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
                <TableCell>Naam</TableCell>
                <TableCell>Domein</TableCell>
                <TableCell>IP</TableCell>
                <TableCell>MAC</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Acties</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {devices.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography color="text.secondary" sx={{ py: 4 }}>
                      Nog geen apparaten. Voeg je eerste apparaat hierboven toe.
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
                        <Tooltip title="MAC kopiëren">
                          <IconButton size="small" onClick={() => copyText(device.mac)}>
                            <ContentCopyIcon fontSize="inherit" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        label={device.online ? 'Online' : 'Offline'}
                        color={device.online ? 'success' : 'default'}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="Wake-on-LAN testen">
                        <IconButton color="success" onClick={() => handleWake(device)}>
                          <PowerSettingsNewIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Bewerken">
                        <IconButton onClick={() => openEdit(device)}>
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Verwijderen">
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
        <DialogTitle>Apparaat bewerken</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Naam"
                value={editing?.name || ''}
                onChange={(e) => setEditing({ ...editing, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Domeinnaam"
                value={editing?.domain || ''}
                onChange={(e) => setEditing({ ...editing, domain: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Intern IP"
                value={editing?.ip || ''}
                onChange={(e) => setEditing({ ...editing, ip: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="MAC-adres"
                value={editing?.mac || ''}
                onChange={(e) => setEditing({ ...editing, mac: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Annuleren</Button>
          <Button variant="contained" onClick={handleUpdate}>Opslaan</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={scanOpen} onClose={() => setScanOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Netwerkscanner</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Subnet" value={scanSubnet} onChange={(e) => setScanSubnet(e.target.value)} sx={{ mt: 1, mb: 2 }} />
          <Button variant="contained" onClick={() => api.scanNetwork({ subnet: scanSubnet }).then((result) => setScanResults(result.hosts || []))}>
            Start scan
          </Button>
          {scanResults.map((host) => (
            <Box key={host.ip} sx={{ display: 'flex', justifyContent: 'space-between', py: 1 }}>
              <Typography>{host.ip}</Typography>
              <Button size="small" onClick={() => { setForm({ ...form, ip: host.ip }); setScanOpen(false); }}>Gebruik IP</Button>
            </Box>
          ))}
        </DialogContent>
        <DialogActions><Button onClick={() => setScanOpen(false)}>Sluiten</Button></DialogActions>
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
