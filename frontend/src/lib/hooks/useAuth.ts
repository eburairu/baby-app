/**
 * 認証フック
 *
 * ユーザー認証状態を管理し、ログイン・ログアウト機能を提供
 */

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import useSWR from 'swr';
import { useAuthStore, User } from '@/lib/stores/authStore';
import { apiGet, apiPost, APIError } from '@/lib/api/client';
import { AuthEndpoints } from '@/lib/api/endpoints';

/**
 * ログイン認証情報
 */
export interface LoginCredentials {
  username: string;
  password: string;
}

/**
 * 登録情報
 */
export interface RegisterData {
  username: string;
  email: string;
  password: string;
  invite_code: string;
}

/**
 * 認証フック
 */
export function useAuth() {
  const router = useRouter();
  const { user, setUser, setLoading, setError, logout: clearAuth } = useAuthStore();

  // 現在のユーザー情報を取得
  const { data, error, mutate } = useSWR<User | null>(
    AuthEndpoints.me,
    async (url) => {
      try {
        // skipAuth: true でリダイレクトを抑制し、レイアウトに委ねる
        return await apiGet<User>(url, { skipAuth: true });
      } catch (err) {
        if (err instanceof APIError && err.status === 401) {
          // 未認証の場合は null を返す（isLoading を false にするため）
          return null;
        }
        throw err;
      }
    },
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      shouldRetryOnError: false,
    }
  );

  // ユーザー情報をストアに同期
  useEffect(() => {
    if (data) {
      setUser(data);
    } else if (data === null) {
      // 未認証（401）の場合はストアもクリア
      setUser(null);
    } else if (error) {
      setError(error.message);
    }
  }, [data, error, setUser, setError]);

  /**
   * ログイン
   */
  const login = async (credentials: LoginCredentials): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      // FormData として送信（FastAPI の OAuth2 仕様に準拠）
      const formData = new FormData();
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);

      const response = await apiPost<User>(AuthEndpoints.login, formData, {
        skipAuth: true,
      });

      setUser(response);
      await mutate(response, false);
      router.push('/dashboard');
    } catch (err) {
      const errorMessage =
        err instanceof APIError ? err.message : 'ログインに失敗しました';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * ログアウト
   */
  const logout = async (): Promise<void> => {
    try {
      await apiPost(AuthEndpoints.logout);
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      clearAuth();
      await mutate(undefined, false);
      router.push('/login');
    }
  };

  /**
   * 新規登録
   */
  const register = async (data: RegisterData): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiPost<User>(AuthEndpoints.register, data, {
        skipAuth: true,
      });

      setUser(response);
      await mutate(response, false);
      router.push('/dashboard');
    } catch (err) {
      const errorMessage =
        err instanceof APIError ? err.message : '登録に失敗しました';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * 認証状態を再検証
   */
  const refresh = async (): Promise<void> => {
    await mutate();
  };

  return {
    user,
    // data === undefined はまだフェッチ中。null は未認証（401）。
    isLoading: data === undefined && error === undefined,
    error: useAuthStore.getState().error,
    login,
    logout,
    register,
    refresh,
    isAuthenticated: !!user,
  };
}
