import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  LinearProgress,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import { useTranslation } from 'react-i18next';
import { api } from '../api/client';

const LogsPage = () => {
  const { t, i18n } = useTranslation();
  const [tab, setTab] = useState(0);
  const [logs, setLogs] = useState([]);
  const [audit, setAudit] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const [logData, auditData] = await Promise.all([api.getLogs(200), api.getAuditLogs(100)]);
      setLogs(logData.logs || []);
      setAudit(auditData);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load().catch(() => setLoading(false));
    const interval = setInterval(load, 10000);
    return () => clearInterval(interval);
  }, []);

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
            <Box component="pre" sx={{ m: 0, minHeight: 360, maxHeight: 560, overflow: 'auto', p: 2, borderRadius: 3, bgcolor: 'rgba(15, 23, 42, 0.9)', fontSize: '0.82rem', whiteSpace: 'pre-wrap' }}>
              {logs.length > 0 ? logs.join('\n') : t('logs.empty')}
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
