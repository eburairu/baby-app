/**
 * useDashboard
 *
 * ダッシュボードデータ取得フック（30秒自動更新）
 */

import useSWR from 'swr';
import { useBabyStore } from '@/lib/stores/babyStore';
import { apiGet } from '@/lib/api/client';
import { DashboardEndpoints } from '@/lib/api/endpoints';

/**
 * ダッシュボードデータ型
 */
export interface DashboardData {
  baby: {
    id: number;
    name: string;
    birthday?: string | null;
    due_date?: string | null;
  } | null;
  feeding_stats: {
    count: number;
    avg_amount_ml?: number;
    period_days?: number;
    last_24h_count?: number;
    last_24h_total_ml?: number;
    avg_interval_hours?: number;
    last_feeding_time?: string;
  } | null;
  sleep_stats: {
    count: number;
    total_hours?: number;
    avg_hours?: number;
    period_days?: number;
    last_24h_total_minutes?: number;
    last_24h_count?: number;
    avg_duration_minutes?: number;
    currently_sleeping?: boolean;
    sleep_start_time?: string;
  } | null;
  diaper_stats: {
    count: number;
    period_days?: number;
    last_24h_count?: number;
    last_24h_pee?: number;
    last_24h_poop?: number;
    last_diaper_time?: string;
  } | null;
  latest_growth: {
    weight_kg?: number;
    height_cm?: number;
    head_cm?: number;
    measured_at?: string;
  } | null;
  recent_records: {
    feedings?: any[];
    sleeps?: any[];
    diapers?: any[];
  } | null;
  prenatal_info: {
    days_remaining: number;
    weeks: number;
    days: number;
  } | null;
  perms: {
    basic_info: boolean;
    feeding: boolean;
    sleep: boolean;
    diaper: boolean;
    growth: boolean;
    schedule: boolean;
    contraction: boolean;
  };
}

/**
 * ダッシュボードフック
 */
export function useDashboard() {
  const { selectedBabyId } = useBabyStore();

  const { data, error, mutate } = useSWR<DashboardData>(
    selectedBabyId ? DashboardEndpoints.data(selectedBabyId) : null,
    apiGet,
    {
      refreshInterval: 30000, // 30秒ごと自動更新
      revalidateOnFocus: true,
      revalidateOnReconnect: true,
    }
  );

  return {
    data,
    isLoading: !error && !data,
    error,
    mutate,
  };
}
