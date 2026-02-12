/**
 * useSchedules
 *
 * スケジュールデータフェッチ・CRUD操作フック
 */

'use client';

import useSWR from 'swr';
import { apiFetch } from '@/lib/api/client';
import { useBabyStore } from '@/lib/stores/babyStore';

export interface Schedule {
  id: number;
  user_id: number;
  title: string;
  description: string | null;
  scheduled_time: string;
  is_completed: boolean;
  created_at: string;
}

interface SchedulesResponse {
  items: Schedule[];
  baby: {
    id: number;
    name: string;
  };
  viewable_babies: Array<{ id: number; name: string }>;
}

export function useSchedules() {
  const { selectedBabyId } = useBabyStore();

  const { data, error, mutate } = useSWR<SchedulesResponse>(
    selectedBabyId ? `/api/schedules?baby_id=${selectedBabyId}` : null,
    apiFetch
  );

  const createSchedule = async (schedule: {
    title: string;
    description?: string;
    scheduled_time: string;
  }) => {
    const newSchedule = await apiFetch<Schedule>('/api/schedules', {
      method: 'POST',
      body: JSON.stringify(schedule),
    });
    mutate();
    return newSchedule;
  };

  const updateSchedule = async (
    id: number,
    schedule: {
      title?: string;
      description?: string;
      scheduled_time?: string;
      is_completed?: boolean;
    }
  ) => {
    const updated = await apiFetch<Schedule>(`/api/schedules/${id}`, {
      method: 'PUT',
      body: JSON.stringify(schedule),
    });
    mutate();
    return updated;
  };

  const toggleSchedule = async (id: number) => {
    const updated = await apiFetch<Schedule>(`/api/schedules/${id}/toggle`, {
      method: 'POST',
    });
    mutate();
    return updated;
  };

  const deleteSchedule = async (id: number) => {
    await apiFetch(`/api/schedules/${id}`, { method: 'DELETE' });
    mutate();
  };

  return {
    schedules: data?.items || [],
    baby: data?.baby || null,
    isLoading: !error && !data,
    error,
    createSchedule,
    updateSchedule,
    toggleSchedule,
    deleteSchedule,
    mutate,
  };
}
