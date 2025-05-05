import { useState, useEffect } from 'react';
import { api } from 'api/client';
import { Field } from 'types/models';

export const useEndpointFields = (endpointType: string) => {
  const [fields, setFields] = useState<Field[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadFields();
  }, [endpointType]);

  const loadFields = async () => {
    try {
      setLoading(true);
      const data = await api.getEndpointFields(endpointType);
      setFields(data);
      setError(null);
    } catch (err) {
      setError('Failed to load fields');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return { fields, loading, error, reload: loadFields };
};