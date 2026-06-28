import React, { createContext, useContext, useState, useEffect } from 'react';
import { getAuthBase } from '../api/config';

interface User {
  id: string;
  username: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string, refresh_token: string) => void;
  logout: () => void;
  isAuthenticated: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const decodeToken = (token: string): { sub: string; role?: string } | null => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      window
        .atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    console.error("Failed to decode token", e);
    return null;
  }
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const login = (newToken: string, _refreshToken?: string) => {
    setToken(newToken);
    localStorage.setItem('access_token', newToken);
    const decoded = decodeToken(newToken);
    if (decoded) {
      setUser({ id: decoded.sub, username: decoded.sub, role: decoded.role || 'user' });
    } else {
      setUser({ id: "1", username: "admin", role: "admin" });
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    const authBase = getAuthBase();
    fetch(`${authBase}/logout`, {
      method: 'POST',
      credentials: 'include',
    }).catch((error) => {
      console.error("Error logging out from server:", error);
    });
  };

  useEffect(() => {
    const checkAuth = async () => {
      const storedAccessToken = localStorage.getItem('access_token');

      try {
        const authBase = getAuthBase();
        const response = await fetch(`${authBase}/refresh`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({}),
        });

        if (response.ok) {
          const data = await response.json();
          const { access_token } = data;
          
          setToken(access_token);
          localStorage.setItem('access_token', access_token);
          
          const decoded = decodeToken(access_token);
          if (decoded) {
            setUser({ id: decoded.sub, username: decoded.sub, role: decoded.role || 'user' });
          } else {
            setUser({ id: "1", username: "admin", role: "admin" });
          }
        } else {
          if (storedAccessToken) {
            const decoded = decodeToken(storedAccessToken);
            const isExpired = decoded && (decoded as any).exp ? (decoded as any).exp * 1000 < Date.now() : true;
            if (!isExpired) {
              setToken(storedAccessToken);
              if (decoded) {
                setUser({ id: decoded.sub, username: decoded.sub, role: decoded.role || 'user' });
              }
            } else {
              logout();
            }
          } else {
            logout();
          }
        }
      } catch (error) {
        console.error("Error during silent token refresh on mount:", error);
        if (storedAccessToken) {
          const decoded = decodeToken(storedAccessToken);
          const isExpired = decoded && (decoded as any).exp ? (decoded as any).exp * 1000 < Date.now() : true;
          if (!isExpired) {
            setToken(storedAccessToken);
            if (decoded) {
              setUser({ id: decoded.sub, username: decoded.sub, role: decoded.role || 'user' });
            }
          } else {
            logout();
          }
        } else {
          logout();
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  useEffect(() => {
    const handleAuthLogout = () => {
      logout();
    };

    const handleAuthRefresh = (e: Event) => {
      const customEvent = e as CustomEvent;
      if (customEvent.detail && customEvent.detail.access_token) {
        const newToken = customEvent.detail.access_token;
        setToken(newToken);
        const decoded = decodeToken(newToken);
        if (decoded) {
          setUser({ id: decoded.sub, username: decoded.sub, role: decoded.role || 'user' });
        }
      }
    };

    window.addEventListener('auth-logout', handleAuthLogout);
    window.addEventListener('auth-refresh', handleAuthRefresh);

    return () => {
      window.removeEventListener('auth-logout', handleAuthLogout);
      window.removeEventListener('auth-refresh', handleAuthRefresh);
    };
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: !!token, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
