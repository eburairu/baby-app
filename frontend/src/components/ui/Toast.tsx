/**
 * Toastコンポーネント
 *
 * トースト通知を提供（Sonner使用）
 */

'use client';

import { Toaster as Sonner, toast as sonnerToast } from 'sonner';

/**
 * Toast Provider
 *
 * アプリケーションのルートレイアウトに配置
 */
export function ToastProvider() {
  return (
    <Sonner
      position="top-right"
      expand={false}
      richColors
      closeButton
      toastOptions={{
        classNames: {
          toast: 'rounded-lg shadow-lg',
          title: 'text-sm font-semibold',
          description: 'text-sm',
          actionButton: 'bg-indigo-600 text-white',
          cancelButton: 'bg-gray-200 text-gray-900',
          closeButton: 'bg-white border border-gray-200',
        },
      }}
    />
  );
}

/**
 * トースト表示ヘルパー
 */
export const toast = {
  success: (message: string, description?: string) => {
    sonnerToast.success(message, { description });
  },
  error: (message: string, description?: string) => {
    sonnerToast.error(message, { description });
  },
  info: (message: string, description?: string) => {
    sonnerToast.info(message, { description });
  },
  warning: (message: string, description?: string) => {
    sonnerToast.warning(message, { description });
  },
  loading: (message: string, description?: string) => {
    return sonnerToast.loading(message, { description });
  },
  promise: <T,>(
    promise: Promise<T>,
    {
      loading,
      success,
      error,
    }: {
      loading: string;
      success: string | ((data: T) => string);
      error: string | ((err: any) => string);
    }
  ) => {
    return sonnerToast.promise(promise, { loading, success, error });
  },
};
