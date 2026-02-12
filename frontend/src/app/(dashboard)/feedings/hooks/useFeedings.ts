/**
 * useFeedings
 *
 * 授乳記録データ取得・操作フック
 */

import useSWR from 'swr';
import { useBabyStore } from '@/lib/stores/babyStore';
import { apiGet, apiPost, apiPut, apiDelete } from '@/lib/api/client';
import { FeedingEndpoints } from '@/lib/api/endpoints';

/**
 * 授乳記録型
 */
export interface Feeding {
  id: number;
  user_id: number;
  feeding_time: string;
  feeding_type: 'breast' | 'bottle' | 'both';
  amount_ml?: number;
  duration_minutes?: number;
  notes?: string;
}

/**
 * 授乳記録作成データ
 */
export interface FeedingCreateData {
  feeding_time: string;
  feeding_type: 'breast' | 'bottle' | 'both';
  amount_ml?: number;
  duration_minutes?: number;
  notes?: string;
}

/**
 * 授乳記録更新データ
 */
export interface FeedingUpdateData {
  feeding_time?: string;
  feeding_type?: 'breast' | 'bottle' | 'both';
  amount_ml?: number;
  duration_minutes?: number;
  notes?: string;
}

/**
 * 授乳記録リストレスポンス
 */
interface FeedingsResponse {
  items: Feeding[];
  baby: {
    id: number;
    name: string;
  } | null;
  viewable_babies: Array<{
    id: number;
    name: string;
  }> | null;
}

/**
 * 授乳記録フック
 */
export function useFeedings() {
  const { selectedBabyId } = useBabyStore();

  const { data, error, mutate } = useSWR<FeedingsResponse>(
    selectedBabyId ? FeedingEndpoints.list(selectedBabyId) : null,
    apiGet
  );

  /**
   * 新規作成
   */
  const createFeeding = async (feedingData: FeedingCreateData) => {
    const newFeeding = await apiPost<Feeding>(FeedingEndpoints.create, {
      ...feedingData,
      baby_id: selectedBabyId,
    });

    // 楽観的更新
    mutate();
    return newFeeding;
  };

  /**
   * 更新
   */
  const updateFeeding = async (id: number, feedingData: FeedingUpdateData) => {
    const updatedFeeding = await apiPut<Feeding>(
      FeedingEndpoints.update(id),
      feedingData
    );

    // 楽観的更新
    mutate();
    return updatedFeeding;
  };

  /**
   * 削除
   */
  const deleteFeeding = async (id: number) => {
    await apiDelete(FeedingEndpoints.delete(id));

    // 楽観的更新
    mutate();
  };

  return {
    feedings: data?.items || [],
    baby: data?.baby,
    viewable_babies: data?.viewable_babies || [],
    isLoading: !error && !data,
    error,
    createFeeding,
    updateFeeding,
    deleteFeeding,
    mutate,
  };
}
