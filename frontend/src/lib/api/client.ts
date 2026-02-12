/**
 * APIクライアント
 *
 * FastAPIバックエンドとの通信を担当
 * - CSRF保護
 * - エラーハンドリング
 * - 認証管理
 */

import Cookies from 'js-cookie';

/**
 * APIエラークラス
 */
export class APIError extends Error {
  constructor(
    public status: number,
    message: string,
    public data?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

/**
 * APIリクエストオプション
 */
interface APIRequestOptions extends RequestInit {
  skipAuth?: boolean;  // 認証チェックをスキップ（ログイン、登録など）
}

/**
 * APIベースURL
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * 統一されたAPI fetchラッパー
 *
 * @param url - エンドポイントURL
 * @param options - リクエストオプション
 * @returns レスポンスデータ
 * @throws {APIError} リクエストが失敗した場合
 */
export async function apiFetch<T = any>(
  url: string,
  options: APIRequestOptions = {}
): Promise<T> {
  const { skipAuth = false, ...fetchOptions } = options;

  // フルURLを構築
  const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`;

  // CSRFトークンを取得
  const csrfToken = Cookies.get('csrf_token');

  // ヘッダーを構築
  const headers: Record<string, string> = {
    'Accept': 'application/json',
    ...(fetchOptions.headers as Record<string, string>),
  };

  // Content-Typeはbodyが存在し、FormDataでない場合のみ設定
  if (fetchOptions.body && !(fetchOptions.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  // CSRFトークンを追加（GET以外）
  if (csrfToken && fetchOptions.method && fetchOptions.method !== 'GET') {
    headers['X-CSRF-Token'] = csrfToken;
  }

  try {
    const response = await fetch(fullUrl, {
      ...fetchOptions,
      headers,
      credentials: 'include',  // Cookieを含める
    });

    // 401 Unauthorized - 認証エラー
    if (response.status === 401 && !skipAuth) {
      // ログインページにリダイレクト
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
      throw new APIError(401, 'Unauthorized');
    }

    // レスポンスボディをパース
    let responseData: any;
    const contentType = response.headers.get('content-type');

    if (contentType && contentType.includes('application/json')) {
      responseData = await response.json();
    } else {
      responseData = await response.text();
    }

    // エラーレスポンス
    if (!response.ok) {
      const errorMessage = responseData?.detail || responseData?.message || 'Unknown error';
      throw new APIError(response.status, errorMessage, responseData);
    }

    return responseData as T;
  } catch (error) {
    // ネットワークエラーなど
    if (error instanceof APIError) {
      throw error;
    }

    console.error('API request failed:', error);
    throw new APIError(0, 'Network error', error);
  }
}

/**
 * GETリクエスト
 */
export async function apiGet<T = any>(url: string, options?: APIRequestOptions): Promise<T> {
  return apiFetch<T>(url, { ...options, method: 'GET' });
}

/**
 * POSTリクエスト
 */
export async function apiPost<T = any>(url: string, data?: any, options?: APIRequestOptions): Promise<T> {
  return apiFetch<T>(url, {
    ...options,
    method: 'POST',
    body: data instanceof FormData ? data : JSON.stringify(data),
  });
}

/**
 * PUTリクエスト
 */
export async function apiPut<T = any>(url: string, data?: any, options?: APIRequestOptions): Promise<T> {
  return apiFetch<T>(url, {
    ...options,
    method: 'PUT',
    body: data instanceof FormData ? data : JSON.stringify(data),
  });
}

/**
 * DELETEリクエスト
 */
export async function apiDelete<T = any>(url: string, options?: APIRequestOptions): Promise<T> {
  return apiFetch<T>(url, { ...options, method: 'DELETE' });
}

/**
 * SWR用のfetcher
 */
export const swrFetcher = <T = any>(url: string): Promise<T> => apiGet<T>(url);
