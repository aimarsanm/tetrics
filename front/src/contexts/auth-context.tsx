'use client';

import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { login as doLogin, logout as doLogout, getUser, type UserInfo } from '@/lib/auth';

interface AuthContextValue {
  user: UserInfo | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();
  const wasAuthenticated = useRef(false);

  useEffect(() => {
    const stored = getUser();
    setUser(stored);
    setIsLoading(false);

    const handleLogout = () => setUser(null);
    window.addEventListener('tetrics-logout', handleLogout);
    return () => window.removeEventListener('tetrics-logout', handleLogout);
  }, []);

  // Redirect to /login when user becomes unauthenticated (e.g. token expired)
  useEffect(() => {
    if (user) {
      wasAuthenticated.current = true;
    } else if (!isLoading && wasAuthenticated.current && pathname !== '/login') {
      router.replace('/login');
    }
  }, [user, isLoading, pathname, router]);

  const login = useCallback(async (username: string, password: string) => {
    const userInfo = await doLogin(username, password);
    setUser(userInfo);
  }, []);

  const logout = useCallback(() => {
    doLogout();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
}
