/**
 * 赤ちゃん選択フック
 *
 * 赤ちゃんの一覧取得と選択状態を管理
 */

import { useEffect } from 'react';
import useSWR from 'swr';
import { useBabyStore, Baby } from '@/lib/stores/babyStore';
import { apiGet } from '@/lib/api/client';
import { BabyEndpoints } from '@/lib/api/endpoints';

/**
 * 赤ちゃん一覧レスポンス
 */
interface BabiesResponse {
  babies?: Baby[];
  items?: Baby[];
}

/**
 * 赤ちゃん選択フック
 */
export function useBaby(familyId?: number) {
  const { selectedBabyId, babies, setSelectedBabyId, setBabies } = useBabyStore();

  // 赤ちゃん一覧を取得
  const { data, error, mutate } = useSWR<BabiesResponse>(
    BabyEndpoints.list(familyId),
    apiGet,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
    }
  );

  // データをストアに同期
  useEffect(() => {
    if (data) {
      // レスポンス形式に応じて babies を抽出
      const babyList = data.babies || data.items || [];
      setBabies(babyList);
    }
  }, [data, setBabies]);

  /**
   * 赤ちゃんを選択
   */
  const selectBaby = (babyId: number): void => {
    setSelectedBabyId(babyId);
  };

  /**
   * 選択中の赤ちゃん情報を取得
   */
  const selectedBaby = babies.find((b) => b.id === selectedBabyId) || null;

  /**
   * 赤ちゃん一覧を再取得
   */
  const refresh = async (): Promise<void> => {
    await mutate();
  };

  return {
    babies,
    selectedBabyId,
    selectedBaby,
    selectBaby,
    isLoading: !data && !error,
    error,
    refresh,
  };
}
