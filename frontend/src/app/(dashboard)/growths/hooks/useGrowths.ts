/**
 * useGrowths
 *
 * 成長記録データ取得・操作フック
 */

import useSWR from 'swr';
import { useBabyStore } from '@/lib/stores/babyStore';
import { apiGet, apiPost, apiPut, apiDelete } from '@/lib/api/client';
import { GrowthEndpoints } from '@/lib/api/endpoints';

/**
 * 成長記録型
 */
export interface Growth {
  id: number;
  user_id: number;
  measurement_date: string;
  weight_kg: number | null;
  height_cm: number | null;
  head_circumference_cm: number | null;
  notes: string | null;
}

/**
 * 成長記録作成データ
 */
export interface GrowthCreateData {
  measurement_date: string;
  weight_kg?: number | null;
  height_cm?: number | null;
  head_circumference_cm?: number | null;
  notes?: string | null;
}

/**
 * 成長記録更新データ
 */
export interface GrowthUpdateData {
  measurement_date?: string;
  weight_kg?: number | null;
  height_cm?: number | null;
  head_circumference_cm?: number | null;
  notes?: string | null;
}

/**
 * 成長記録リストレスポンス
 */
interface GrowthsResponse {
  items: Growth[];
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
 * 成長記録フック
 */
export function useGrowths() {
  const { selectedBabyId } = useBabyStore();

  const { data, error, mutate } = useSWR<GrowthsResponse>(
    selectedBabyId ? GrowthEndpoints.list(selectedBabyId) : null,
    apiGet
  );

  /**
   * 新規作成
   */
  const createGrowth = async (growthData: GrowthCreateData) => {
    const newGrowth = await apiPost<Growth>(GrowthEndpoints.create, {
      ...growthData,
      baby_id: selectedBabyId,
    });

    // 楽観的更新
    mutate();
    return newGrowth;
  };

  /**
   * 更新
   */
  const updateGrowth = async (id: number, growthData: GrowthUpdateData) => {
    const updatedGrowth = await apiPut<Growth>(
      GrowthEndpoints.update(id),
      growthData
    );

    // 楽観的更新
    mutate();
    return updatedGrowth;
  };

  /**
   * 削除
   */
  const deleteGrowth = async (id: number) => {
    await apiDelete(GrowthEndpoints.delete(id));

    // 楽観的更新
    mutate();
  };

  return {
    growths: data?.items || [],
    baby: data?.baby,
    viewable_babies: data?.viewable_babies || [],
    isLoading: !error && !data,
    error,
    createGrowth,
    updateGrowth,
    deleteGrowth,
    mutate,
  };
}
