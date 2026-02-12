/**
 * useDiapers
 *
 * おむつ交換記録データ取得・操作フック
 */

import useSWR from 'swr';
import { useBabyStore } from '@/lib/stores/babyStore';
import { apiGet, apiPost } from '@/lib/api/client';
import { DiaperEndpoints } from '@/lib/api/endpoints';

/**
 * おむつ交換記録型
 */
export interface Diaper {
  id: number;
  user_id: number;
  change_time: string;
  diaper_type: 'wet' | 'dirty' | 'both';
  notes: string | null;
}

/**
 * おむつ交換記録作成データ
 */
export interface DiaperCreateData {
  change_time: string;
  diaper_type: 'wet' | 'dirty' | 'both';
  notes?: string | null;
}

/**
 * おむつ交換記録リストレスポンス
 */
interface DiapersResponse {
  items: Diaper[];
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
 * おむつ交換記録フック
 */
export function useDiapers() {
  const { selectedBabyId } = useBabyStore();

  const { data, error, mutate } = useSWR<DiapersResponse>(
    selectedBabyId ? DiaperEndpoints.list(selectedBabyId) : null,
    apiGet
  );

  /**
   * クイック記録（ワンタップ）
   */
  const quickRecord = async (diaperType: 'wet' | 'dirty' | 'both') => {
    const newDiaper = await apiPost<Diaper>(DiaperEndpoints.quick, {
      diaper_type: diaperType,
      baby_id: selectedBabyId,
    });

    // 楽観的更新
    mutate();
    return newDiaper;
  };

  /**
   * 詳細記録
   */
  const createDiaper = async (diaperData: DiaperCreateData) => {
    const newDiaper = await apiPost<Diaper>(DiaperEndpoints.create, {
      ...diaperData,
      baby_id: selectedBabyId,
    });

    // 楽観的更新
    mutate();
    return newDiaper;
  };

  return {
    diapers: data?.items || [],
    baby: data?.baby,
    viewable_babies: data?.viewable_babies || [],
    isLoading: !error && !data,
    error,
    quickRecord,
    createDiaper,
    mutate,
  };
}
