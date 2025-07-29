"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useSession } from 'next-auth/react';

interface AuthContextType {
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const { data: session, status, update } = useSession();
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    if (session?.accessToken) {
      // The JWT token is now stored in session.accessToken from our callbacks
      setToken(session.accessToken as string);
    } else {
      setToken(null);
    }
  }, [session]);

  const refreshToken = async () => {
    await update();
  };

  const value = {
    token,
    isAuthenticated: !!token,
    isLoading: status === 'loading',
    refreshToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}