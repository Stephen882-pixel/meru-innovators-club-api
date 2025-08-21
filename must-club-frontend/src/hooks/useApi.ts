import { useState, useEffect, useCallback } from 'react';
import { AxiosError } from 'axios';
import { handleApiError } from '../services/api';

interface UseApiState<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
}

interface UseApiReturn<T> extends UseApiState<T> {
  execute: (...args: any[]) => Promise<T>;
  reset: () => void;
}

export const useApi = <T>(
  apiFunction: (...args: any[]) => Promise<T>,
  immediate: boolean = false,
  ...args: any[]
): UseApiReturn<T> => {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    isLoading: immediate,
    error: null,
  });

  const execute = useCallback(async (...executeArgs: any[]): Promise<T> => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      const result = await apiFunction(...executeArgs);
      setState(prev => ({ ...prev, data: result, isLoading: false }));
      return result;
    } catch (error: any) {
      const errorMessage = handleApiError(error as AxiosError);
      setState(prev => ({ ...prev, error: errorMessage, isLoading: false }));
      throw error;
    }
  }, [apiFunction]);

  const reset = useCallback(() => {
    setState({
      data: null,
      isLoading: false,
      error: null,
    });
  }, []);

  useEffect(() => {
    if (immediate) {
      execute(...args);
    }
  }, [execute, immediate]);

  return {
    ...state,
    execute,
    reset,
  };
};

export default useApi;