import React, { useCallback, useEffect, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  LinearProgress,
  MenuItem,
  Select,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import { useTranslation } from 'react-i18next';
import { api } from '../api/client';

const LogsPage = () => {
  const { t, i18n } = useTranslation();
  const [tab, setTab] = useState(0);
  const [logs, setLogs] = useState([]);
  const [entries, setEntries] = useState([]);
  const [audit, setAudit] = useState([]);
  const [loading, setLoading] = useState(true);
  const [level, setLevel] = useState('');
  const [search, setSearch] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [logData, auditData] = await Promise.all([
        api.getLogs(200, level, search),
        api.getAuditLogs(100),
      ]);
      setLogs(logData.logs || []);
      setEntries(logData.entries || []);
      setAudit(auditData);
    } finally {
      setLoading(false);
    }
  }, [level, search]);

  useEffect(() => {
    load().catch(() => setLoading(false));
    const interval = setInterval(load, 10000);
    return () => clearInterval(interval);
  }, [load]);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3, gap: 2, flexWrap: 'wrap' }}>
        <Box>
          <Typography variant="h4" gutterBottom>{t('logs.title')}</Typography>
          <Typography color="text.secondary">{t('logs.subtitle')}</Typography>
        </Box>
        <Button variant="outlined" startIcon={<RefreshIcon />} onClick={load}>{t('common.refresh')}</Button>
      </Box>

      <Tabs value={tab} onChange={(_, value) => setTab(value)} sx={{ mb: 2 }}>
        <Tab label={t('logs.system')} />
        <Tab label={t('logs.audit')} />
      </Tabs>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {tab === 0 ? (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
              <FormControl sx={{ minWidth: 160 }}>
                <InputLabel>{t('settings.logLevel')}</InputLabel>
                <Select value={level} label={t('settings.logLevel')} onChange={(e) => setLevel(e.target.value)}>
                  <MenuItem value="">{t('common.none')}</MenuItem>
                  {['DEBUG', 'INFO', 'WARNING', 'ERROR'].map((item) => (
                    <MenuItem key={item} value={item}>{item}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField label={t('logs.search')} value={search} onChange={(e) => setSearch(e.target.value)} />
            </Box>
            <Box component="pre" sx={{ m: 0, minHeight: 360, maxHeight: 560, overflow: 'auto', p: 2, borderRadius: 3, bgcolor: 'rgba(15, 23, 42, 0.9)', fontSize: '0.82rem', whiteSpace: 'pre-wrap' }}>
              {entries.length > 0
                ? entries.map((entry) => `[${entry.level}] ${entry.message}`).join('\n')
                : logs.length > 0
                  ? logs.join('\n')
                  : t('logs.empty')}
            </Box>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent sx={{ overflowX: 'auto' }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>{t('logs.auditTime')}</TableCell>
                  <TableCell>{t('logs.auditAction')}</TableCell>
                  <TableCell>{t('logs.auditDetails')}</TableCell>
                  <TableCell>{t('logs.auditIp')}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {audit.map((entry) => (
                  <TableRow key={entry.id}>
                    <TableCell>{new Date(entry.created_at).toLocaleString(i18n.language)}</TableCell>
                    <TableCell>{entry.action}</TableCell>
                    <TableCell>{entry.details}</TableCell>
                    <TableCell>{entry.actor_ip}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default LogsPage;
