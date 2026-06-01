import React, { createContext, useContext, useState, useEffect } from 'react';

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
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    // On mount, check if we have a refresh token in secure storage/localStorage
    // If we do, we could attempt a silent refresh here.
    const storedToken = localStorage.getItem('access_token');
    if (storedToken) {
      setToken(storedToken);
      // Optional: decode token or fetch user info here to set the user state
      setUser({ id: "1", username: "admin", role: "admin" });
    }
  }, []);

  const login = (newToken: string, refreshToken: string) => {
    setToken(newToken);
    localStorage.setItem('access_token', newToken);
    localStorage.setItem('refresh_token', refreshToken);
    // Ideally we'd fetch the user profile here and set it
    setUser({ id: "1", username: "admin", role: "admin" });
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: !!token }}>
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
