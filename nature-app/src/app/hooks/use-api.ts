"use client";

import { useEffect } from 'react';
import { useAuth } from '../contexts/auth-context';
import { apiClient } from '../lib/api-client';

export function useAPI() {
  const { token, isAuthenticated } = useAuth();

  useEffect(() => {
    apiClient.setToken(token);
  }, [token]);

  return {
    apiClient,
    isAuthenticated,
    token,
  };
}