/**
 * 認証状態管理（Zustand）
 *
 * ユーザーのログイン状態を管理
 */

import { create } from 'zustand';

/**
 * ユーザー情報
 */
export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
}

/**
 * 認証ストアの状態
 */
interface AuthState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  setUser: (user: User | null) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  logout: () => void;
}

/**
 * 認証ストア
 */
export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
  error: null,

  setUser: (user) => set({ user, isLoading: false, error: null }),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error, isLoading: false }),

  logout: () => set({ user: null, isLoading: false, error: null }),
}));
