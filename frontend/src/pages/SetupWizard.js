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
import { useTranslation } from 'react-i18next';
import AppLogo from '../components/AppLogo';
import LanguageSwitcher from '../components/LanguageSwitcher';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';

const SetupWizard = ({ onComplete }) => {
  const { refresh } = useAuth();
  const { t, i18n } = useTranslation();
  const [activeStep, setActiveStep] = useState(0);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [proxywakeUrl, setProxywakeUrl] = useState(window.location.origin);
  const [error, setError] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [loading, setLoading] = useState(false);

  const steps = [
    t('setup.steps.welcome'),
    t('setup.steps.security'),
    t('setup.steps.network'),
    t('setup.steps.done'),
  ];

  const handleFinish = async () => {
    if (password && password !== confirmPassword) {
      setError(t('setup.passwordMismatch'));
      return;
    }
    if (password && password.length < 8) {
      setError(t('errors.PASSWORD_TOO_SHORT'));
      return;
    }
    setLoading(true);
    setError('');
    try {
      const result = await api.setup({
        password: password || undefined,
        proxywake_url: proxywakeUrl,
        theme: 'dark',
        language: i18n.language?.split('-')[0] || 'en',
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
      <Box sx={{ position: 'absolute', top: 16, right: 16 }}>
        <LanguageSwitcher />
      </Box>
      <Card sx={{ width: '100%', maxWidth: 720 }}>
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
            <AppLogo size={48} />
            <Box>
              <Typography variant="h5">{t('setup.welcome')}</Typography>
              <Typography color="text.secondary">{t('setup.intro')}</Typography>
            </Box>
          </Box>

          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => <Step key={label}><StepLabel>{label}</StepLabel></Step>)}
          </Stepper>

          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

          {activeStep === 0 && (
            <Box>
              <Typography paragraph>
                {t('setup.intro')}
              </Typography>
              <Button variant="contained" onClick={() => setActiveStep(1)}>{t('setup.start')}</Button>
            </Box>
          )}

          {activeStep === 1 && (
            <Box>
              <Typography color="text.secondary" sx={{ mb: 2 }}>
                {t('setup.passwordHint')}
              </Typography>
              <TextField fullWidth type="password" label={t('setup.password')} value={password} onChange={(e) => setPassword(e.target.value)} sx={{ mb: 2 }} />
              <TextField fullWidth type="password" label={t('setup.confirmPassword')} value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} sx={{ mb: 2 }} />
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button onClick={() => setActiveStep(0)}>{t('common.cancel')}</Button>
                <Button variant="contained" onClick={() => setActiveStep(2)}>{t('common.ok')}</Button>
              </Box>
            </Box>
          )}

          {activeStep === 2 && (
            <Box>
              <Typography color="text.secondary" sx={{ mb: 2 }}>
                {t('setup.urlHint')}
              </Typography>
              <TextField fullWidth label={t('setup.urlLabel')} value={proxywakeUrl} onChange={(e) => setProxywakeUrl(e.target.value)} sx={{ mb: 2 }} />
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button onClick={() => setActiveStep(1)}>{t('common.cancel')}</Button>
                <Button variant="contained" onClick={handleFinish} disabled={loading}>
                  {loading ? t('setup.finishing') : t('setup.finish')}
                </Button>
              </Box>
            </Box>
          )}

          {activeStep === 3 && (
            <Box>
              <Alert severity="success" sx={{ mb: 2 }}>{t('setup.doneTitle')}</Alert>
              {apiKey && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  {t('setup.apiKeyLabel')} <strong>{apiKey}</strong>
                </Alert>
              )}
              <Button variant="contained" onClick={onComplete}>{t('setup.toDashboard')}</Button>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default SetupWizard;
