import React from 'react';
import { FormControl, MenuItem, Select } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { changeLanguage, supportedLanguages } from '../i18n';
import { api } from '../api/client';

const LanguageSwitcher = ({ size = 'small', fullWidth = false }) => {
  const { i18n } = useTranslation();

  const handleChange = async (language) => {
    await changeLanguage(language);
    try {
      await api.updateLanguage(language);
    } catch {
      // not logged in yet — localStorage is enough
    }
  };

  return (
    <FormControl size={size} fullWidth={fullWidth} sx={{ minWidth: fullWidth ? undefined : 120 }}>
      <Select
        value={i18n.language?.split('-')[0] || 'en'}
        onChange={(event) => handleChange(event.target.value)}
        variant="outlined"
        sx={{ color: 'inherit', '.MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(148,163,184,0.3)' } }}
      >
        {supportedLanguages.map((lang) => (
          <MenuItem key={lang.code} value={lang.code}>{lang.label}</MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

export default LanguageSwitcher;
