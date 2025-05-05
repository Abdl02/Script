import { useState, useEffect } from 'react';
import { api } from '@api/client';
import { TestScenario } from '@types/models';

export const useScenarios = () => {
  const [scenarios, setScenarios] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadScenarios();
  }, []);

  const loadScenarios = async () => {
    try {
      setLoading(true);
      const data = await api.getScenarios();
      setScenarios(data);
      setError(null);
    } catch (err) {
      setError('Failed to load scenarios');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return { scenarios, loading, error, reload: loadScenarios };
};