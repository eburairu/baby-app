/**
 * useContractions
 *
 * 陣痛記録データフェッチ・CRUD操作フック
 */

'use client';

import useSWR from 'swr';
import { apiFetch } from '@/lib/api/client';
import { useBabyStore } from '@/lib/stores/babyStore';

export interface Contraction {
  id: number;
  user_id: number;
  start_time: string;
  end_time: string | null;
  duration_seconds: number | null;
  interval_seconds: number | null;
  notes: string | null;
  is_ongoing: boolean;
  duration_display: string;
  interval_display: string;
}

interface Statistics {
  count: number;
  avg_duration_seconds: number;
  avg_interval_seconds: number;
  last_interval_seconds: number | null;
  period_hours: number;
}

interface ContractionsResponse {
  items: Contraction[];
  ongoing: Contraction | null;
  stats: Statistics;
  baby: {
    id: number;
    name: string;
  };
  viewable_babies: Array<{ id: number; name: string }>;
}

interface ContractionListResponse {
  items: Contraction[];
  stats: Statistics;
}

export function useContractions() {
  const { selectedBabyId } = useBabyStore();

  const { data, error, mutate } = useSWR<ContractionsResponse>(
    selectedBabyId ? `/api/contractions?baby_id=${selectedBabyId}` : null,
    apiFetch
  );

  // 5秒自動更新用のリストデータ
  const { data: listData } = useSWR<ContractionListResponse>(
    selectedBabyId ? `/api/contractions/list?baby_id=${selectedBabyId}` : null,
    apiFetch,
    {
      refreshInterval: 5000, // 5秒ごとに更新
      revalidateOnFocus: false,
    }
  );

  const startContraction = async () => {
    const newContraction = await apiFetch<Contraction>('/api/contractions/start', {
      method: 'POST',
    });
    mutate();
    return newContraction;
  };

  const endContraction = async (id: number) => {
    const updatedContraction = await apiFetch<Contraction>(
      `/api/contractions/${id}/end`,
      {
        method: 'POST',
      }
    );
    mutate();
    return updatedContraction;
  };

  const createContraction = async (contraction: {
    start_time: string;
    notes?: string;
  }) => {
    const newContraction = await apiFetch<Contraction>('/api/contractions', {
      method: 'POST',
      body: JSON.stringify(contraction),
    });
    mutate();
    return newContraction;
  };

  const updateContraction = async (
    id: number,
    contraction: {
      start_time: string;
      end_time?: string | null;
      notes?: string;
    }
  ) => {
    const updated = await apiFetch<Contraction>(`/api/contractions/${id}`, {
      method: 'PUT',
      body: JSON.stringify(contraction),
    });
    mutate();
    return updated;
  };

  const deleteContraction = async (id: number) => {
    await apiFetch(`/api/contractions/${id}`, { method: 'DELETE' });
    mutate();
  };

  return {
    contractions: listData?.items || data?.items || [],
    ongoing: data?.ongoing || null,
    stats: listData?.stats || data?.stats || {
      count: 0,
      avg_duration_seconds: 0,
      avg_interval_seconds: 0,
      last_interval_seconds: null,
      period_hours: 1,
    },
    baby: data?.baby || null,
    isLoading: !error && !data,
    error,
    startContraction,
    endContraction,
    createContraction,
    updateContraction,
    deleteContraction,
    mutate,
  };
}
