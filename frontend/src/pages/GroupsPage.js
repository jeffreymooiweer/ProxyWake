import React, { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  IconButton,
  Snackbar,
  TextField,
  Typography,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import PowerSettingsNewIcon from '@mui/icons-material/PowerSettingsNew';
import { useTranslation } from 'react-i18next';
import { api } from '../api/client';

const GroupsPage = () => {
  const { t } = useTranslation();
  const [groups, setGroups] = useState([]);
  const [name, setName] = useState('');
  const [color, setColor] = useState('#6366f1');
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  const load = () => api.getGroups().then(setGroups).catch((err) => setNotification({ open: true, message: err.message, severity: 'error' }));
  useEffect(() => { load(); }, []);

  const handleCreate = async (event) => {
    event.preventDefault();
    try {
      await api.createGroup({ name, color });
      setName('');
      load();
    } catch (err) {
      setNotification({ open: true, message: err.message, severity: 'error' });
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>{t('groups.title')}</Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>{t('groups.subtitle')}</Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box component="form" onSubmit={handleCreate} sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <TextField label={t('groups.name')} value={name} onChange={(e) => setName(e.target.value)} required sx={{ flex: 1, minWidth: 200 }} />
            <TextField label={t('groups.color')} type="color" value={color} onChange={(e) => setColor(e.target.value)} sx={{ width: 100 }} />
            <Button type="submit" variant="contained" startIcon={<AddIcon />} sx={{ height: 56 }}>{t('groups.add')}</Button>
          </Box>
        </CardContent>
      </Card>

      <Grid container spacing={2}>
        {groups.map((group) => (
          <Grid item xs={12} md={6} key={group.id}>
            <Card>
              <CardContent sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Chip label={group.name} sx={{ bgcolor: group.color, color: '#fff' }} />
                </Box>
                <Box>
                  <IconButton color="success" onClick={() => api.wakeGroup(group.id).then(() => setNotification({ open: true, message: t('groups.wakeStarted'), severity: 'success' }))}>
                    <PowerSettingsNewIcon />
                  </IconButton>
                  <IconButton color="error" onClick={() => api.deleteGroup(group.id).then(load)}>
                    <DeleteIcon />
                  </IconButton>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Snackbar open={notification.open} autoHideDuration={4000} onClose={() => setNotification({ ...notification, open: false })}>
        <Alert severity={notification.severity}>{notification.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default GroupsPage;
