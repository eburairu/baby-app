/**
 * SleepItem
 *
 * 個別の睡眠記録表示コンポーネント
 */

'use client';

import { format } from 'date-fns';
import { ja } from 'date-fns/locale';
import { Moon, Clock } from 'lucide-react';
import type { Sleep } from '../hooks/useSleeps';

interface SleepItemProps {
  sleep: Sleep;
}

export function SleepItem({ sleep }: SleepItemProps) {
  // 持続時間の表示
  const durationDisplay = () => {
    if (sleep.is_ongoing) {
      return <span className="text-green-600 dark:text-green-400">睡眠中</span>;
    }

    const hours = Math.floor(sleep.duration_minutes / 60);
    const minutes = sleep.duration_minutes % 60;

    if (hours > 0) {
      return `${hours}時間${minutes}分`;
    }
    return `${minutes}分`;
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        {/* 左側: 睡眠情報 */}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <Moon className="h-5 w-5 text-purple-600 dark:text-purple-400" />
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {format(new Date(sleep.start_time), 'M月d日(E) HH:mm', {
                locale: ja,
              })}
              {sleep.end_time && (
                <>
                  {' '}
                  〜{' '}
                  {format(new Date(sleep.end_time), 'HH:mm', {
                    locale: ja,
                  })}
                </>
              )}
            </span>
          </div>

          {/* 持続時間 */}
          <div className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-white">
            <Clock className="h-5 w-5" />
            <span>{durationDisplay()}</span>
          </div>

          {/* メモ */}
          {sleep.notes && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
              {sleep.notes}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
