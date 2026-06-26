import React, { useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Step,
  StepLabel,
  Stepper,
  TextField,
  Typography,
} from '@mui/material';
import PowerSettingsNewIcon from '@mui/icons-material/PowerSettingsNew';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';

const steps = ['Welkom', 'Beveiliging', 'Netwerk', 'Klaar'];

const SetupWizard = ({ onComplete }) => {
  const { refresh } = useAuth();
  const [activeStep, setActiveStep] = useState(0);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [proxywakeUrl, setProxywakeUrl] = useState(window.location.origin);
  const [error, setError] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [loading, setLoading] = useState(false);

  const handleFinish = async () => {
    if (password && password !== confirmPassword) {
      setError('Wachtwoorden komen niet overeen.');
      return;
    }
    if (password && password.length < 8) {
      setError('Wachtwoord moet minimaal 8 tekens zijn.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const result = await api.setup({
        password: password || undefined,
        proxywake_url: proxywakeUrl,
        theme: 'dark',
      });
      setApiKey(result.api_key);
      await refresh();
      setActiveStep(3);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', display: 'grid', placeItems: 'center', p: 2 }}>
      <Card sx={{ width: '100%', maxWidth: 720 }}>
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
            <PowerSettingsNewIcon color="primary" sx={{ fontSize: 36 }} />
            <Box>
              <Typography variant="h5">Welkom bij ProxyWake</Typography>
              <Typography color="text.secondary">Laten we je installatie in een paar stappen configureren.</Typography>
            </Box>
          </Box>

          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => <Step key={label}><StepLabel>{label}</StepLabel></Step>)}
          </Stepper>

          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

          {activeStep === 0 && (
            <Box>
              <Typography paragraph>
                ProxyWake maakt Wake-on-LAN eenvoudig in combinatie met Nginx Proxy Manager.
                Deze wizard helpt je met beveiliging en netwerkconfiguratie.
              </Typography>
              <Button variant="contained" onClick={() => setActiveStep(1)}>Start setup</Button>
            </Box>
          )}

          {activeStep === 1 && (
            <Box>
              <Typography color="text.secondary" sx={{ mb: 2 }}>
                Stel een wachtwoord in voor de webinterface (aanbevolen). Laat leeg om later in te stellen.
              </Typography>
              <TextField fullWidth type="password" label="Wachtwoord" value={password} onChange={(e) => setPassword(e.target.value)} sx={{ mb: 2 }} />
              <TextField fullWidth type="password" label="Bevestig wachtwoord" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} sx={{ mb: 2 }} />
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button onClick={() => setActiveStep(0)}>Terug</Button>
                <Button variant="contained" onClick={() => setActiveStep(2)}>Volgende</Button>
              </Box>
            </Box>
          )}

          {activeStep === 2 && (
            <Box>
              <Typography color="text.secondary" sx={{ mb: 2 }}>
                Geef het interne adres op dat NPM kan bereiken (niet localhost).
              </Typography>
              <TextField fullWidth label="ProxyWake URL" value={proxywakeUrl} onChange={(e) => setProxywakeUrl(e.target.value)} sx={{ mb: 2 }} />
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button onClick={() => setActiveStep(1)}>Terug</Button>
                <Button variant="contained" onClick={handleFinish} disabled={loading}>
                  {loading ? 'Bezig...' : 'Setup voltooien'}
                </Button>
              </Box>
            </Box>
          )}

          {activeStep === 3 && (
            <Box>
              <Alert severity="success" sx={{ mb: 2 }}>Setup voltooid! Je kunt nu apparaten toevoegen.</Alert>
              {apiKey && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  Je API-sleutel: <strong>{apiKey}</strong>
                </Alert>
              )}
              <Button variant="contained" onClick={onComplete}>Naar dashboard</Button>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default SetupWizard;
