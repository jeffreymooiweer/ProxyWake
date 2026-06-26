import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  LinearProgress,
  Typography,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import { api } from '../api/client';

const LogsPage = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await api.getLogs(200);
      setLogs(data.logs || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs().catch(() => setLoading(false));
    const interval = setInterval(loadLogs, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, gap: 2, flexWrap: 'wrap' }}>
        <Box>
          <Typography variant="h4" gutterBottom>Logboek</Typography>
          <Typography color="text.secondary">
            Volg wake-acties, wijzigingen en fouten in realtime.
          </Typography>
        </Box>
        <Button variant="outlined" startIcon={<RefreshIcon />} onClick={loadLogs}>
          Vernieuwen
        </Button>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      <Card>
        <CardContent>
          <Box
            component="pre"
            sx={{
              m: 0,
              minHeight: 360,
              maxHeight: 560,
              overflow: 'auto',
              p: 2,
              borderRadius: 3,
              bgcolor: 'rgba(15, 23, 42, 0.9)',
              border: '1px solid rgba(148, 163, 184, 0.12)',
              fontSize: '0.82rem',
              lineHeight: 1.6,
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
            }}
          >
            {logs.length > 0 ? logs.join('\n') : 'Nog geen logregels beschikbaar.'}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default LogsPage;
