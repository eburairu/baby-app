/**
 * useSleeps
 *
 * 睡眠記録データ取得・操作フック
 */

import useSWR from 'swr';
import { useBabyStore } from '@/lib/stores/babyStore';
import { apiGet, apiPost } from '@/lib/api/client';
import { SleepEndpoints } from '@/lib/api/endpoints';

/**
 * 睡眠記録型
 */
export interface Sleep {
  id: number;
  user_id: number;
  start_time: string;
  end_time: string | null;
  notes: string | null;
  duration_minutes: number;
  is_ongoing: boolean;
}

/**
 * 睡眠記録作成データ
 */
export interface SleepCreateData {
  start_time: string;
  end_time?: string | null;
  notes?: string | null;
}

/**
 * 睡眠記録更新データ
 */
export interface SleepUpdateData {
  start_time?: string;
  end_time?: string | null;
  notes?: string | null;
}

/**
 * 睡眠記録リストレスポンス
 */
interface SleepsResponse {
  items: Sleep[];
  baby: {
    id: number;
    name: string;
  } | null;
  viewable_babies: Array<{
    id: number;
    name: string;
  }> | null;
  ongoing_sleep: Sleep | null;
}

/**
 * 睡眠記録フック
 */
export function useSleeps() {
  const { selectedBabyId } = useBabyStore();

  const { data, error, mutate } = useSWR<SleepsResponse>(
    selectedBabyId ? SleepEndpoints.list(selectedBabyId) : null,
    apiGet
  );

  /**
   * 睡眠開始
   */
  const startSleep = async () => {
    const newSleep = await apiPost<Sleep>(SleepEndpoints.start, {
      baby_id: selectedBabyId,
    });

    // 楽観的更新
    mutate();
    return newSleep;
  };

  /**
   * 睡眠終了
   */
  const endSleep = async (id: number) => {
    const updatedSleep = await apiPost<Sleep>(SleepEndpoints.end(id), {});

    // 楽観的更新
    mutate();
    return updatedSleep;
  };

  /**
   * 手動作成
   */
  const createSleep = async (sleepData: SleepCreateData) => {
    const newSleep = await apiPost<Sleep>(SleepEndpoints.create, {
      ...sleepData,
      baby_id: selectedBabyId,
    });

    // 楽観的更新
    mutate();
    return newSleep;
  };

  return {
    sleeps: data?.items || [],
    baby: data?.baby,
    viewable_babies: data?.viewable_babies || [],
    ongoingSleep: data?.ongoing_sleep,
    isLoading: !error && !data,
    error,
    startSleep,
    endSleep,
    createSleep,
    mutate,
  };
}
