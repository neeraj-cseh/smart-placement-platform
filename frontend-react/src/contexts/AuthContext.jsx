import { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { api, getAccessToken } from '../api/client';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(() => !!getAccessToken());
  const initialized = useRef(false);

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    const token = getAccessToken();
    if (!token) {
      setLoading(false);
      return;
    }

    api.get('/auth/session/')
      .then((data) => setUser(data))
      .catch(() => {
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = async (email, password) => {
    const data = await api.post('/auth/login/', { email, password });
    localStorage.setItem('access', data.access);
    localStorage.setItem('refresh', data.refresh);
    setUser(data.user);
    return data;
  };

  const register = async (userData) => {
    const data = await api.post('/auth/register/', userData);
    localStorage.setItem('access', data.access);
    localStorage.setItem('refresh', data.refresh);
    setUser(data.user);
    return data;
  };

  const logout = async () => {
    const refresh = localStorage.getItem('refresh');
    try {
      await api.post('/auth/logout/', { refresh });
    } catch {
      // Ignore errors on logout
    }
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    setUser(null);
  };

  const refetch = useCallback(async () => {
    try {
      const data = await api.get('/auth/session/');
      setUser(data);
    } catch {
      setUser(null);
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refetch }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
