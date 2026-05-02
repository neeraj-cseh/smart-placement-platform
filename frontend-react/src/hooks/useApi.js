import { useState, useCallback, useEffect } from 'react';
import { api } from '../api/client';

export function useApi(endpoint, autoFetch = true) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(autoFetch);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async (params) => {
    setLoading(true);
    setError(null);
    try {
      const url = params ? `${endpoint}?${new URLSearchParams(params)}` : endpoint;
      const result = await api.get(url);
      setData(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [endpoint]);

  const mutate = useCallback(async (method, body) => {
    setLoading(true);
    setError(null);
    try {
      const result = await api[method](endpoint, body);
      setData(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [endpoint]);

  useEffect(() => {
    if (!autoFetch) return;
    fetchData().catch(() => {});
  }, [autoFetch, fetchData]);

  return { data, loading, error, refetch: fetchData, mutate, setData };
}
