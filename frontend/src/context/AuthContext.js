import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { api } from '../api/client';
import { changeLanguage } from '../i18n';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);
  const [passwordRequired, setPasswordRequired] = useState(false);
  const [onboardingCompleted, setOnboardingCompleted] = useState(false);

  const refresh = useCallback(async () => {
    const status = await api.authStatus();
    setAuthenticated(status.authenticated);
    setPasswordRequired(status.password_required);
    setOnboardingCompleted(status.onboarding_completed);
    if (status.language) {
      await changeLanguage(status.language);
    }
    setLoading(false);
    return status;
  }, []);

  useEffect(() => {
    refresh().catch(() => setLoading(false));
  }, [refresh]);

  const login = useCallback(async (password) => {
    await api.login(password);
    setAuthenticated(true);
  }, []);

  const logout = useCallback(async () => {
    await api.logout();
    setAuthenticated(false);
  }, []);

  const value = useMemo(
    () => ({ loading, authenticated, passwordRequired, onboardingCompleted, login, logout, refresh }),
    [loading, authenticated, passwordRequired, onboardingCompleted, login, logout, refresh],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);
