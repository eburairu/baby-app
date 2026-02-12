/**
 * 赤ちゃん選択状態管理（Zustand）
 *
 * 現在選択中の赤ちゃんIDを管理し、Cookie と同期
 */

import { create } from 'zustand';
import Cookies from 'js-cookie';

/**
 * 赤ちゃんの基本情報
 */
export interface Baby {
  id: number;
  name: string;
  birthday?: string | null;
}

/**
 * 赤ちゃん選択ストアの状態
 */
interface BabyState {
  selectedBabyId: number | null;
  babies: Baby[];
  setSelectedBabyId: (id: number) => void;
  setBabies: (babies: Baby[]) => void;
  clearSelection: () => void;
}

/**
 * Cookie から選択中の赤ちゃんIDを取得
 */
function getSelectedBabyIdFromCookie(): number | null {
  const cookieValue = Cookies.get('selected_baby_id');
  if (!cookieValue) return null;

  const id = Number(cookieValue);
  return isNaN(id) ? null : id;
}

/**
 * 赤ちゃん選択ストア
 */
export const useBabyStore = create<BabyState>((set) => ({
  selectedBabyId: getSelectedBabyIdFromCookie(),
  babies: [],

  setSelectedBabyId: (id) => {
    // Cookie に保存（7日間有効）
    Cookies.set('selected_baby_id', String(id), {
      expires: 7,
      sameSite: 'lax',
    });
    set({ selectedBabyId: id });
  },

  setBabies: (babies) => {
    set({ babies });

    // 選択中の赤ちゃんがリストにない場合、最初の赤ちゃんを選択
    const currentId = getSelectedBabyIdFromCookie();
    if (babies.length > 0) {
      const hasCurrent = currentId && babies.some((b) => b.id === currentId);
      if (!hasCurrent) {
        const firstBabyId = babies[0].id;
        Cookies.set('selected_baby_id', String(firstBabyId), {
          expires: 7,
          sameSite: 'lax',
        });
        set({ selectedBabyId: firstBabyId });
      }
    }
  },

  clearSelection: () => {
    Cookies.remove('selected_baby_id');
    set({ selectedBabyId: null, babies: [] });
  },
}));
