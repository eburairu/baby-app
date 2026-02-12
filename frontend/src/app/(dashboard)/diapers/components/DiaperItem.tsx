/**
 * DiaperItem
 *
 * 個別のおむつ交換記録表示コンポーネント
 */

'use client';

import { format } from 'date-fns';
import { ja } from 'date-fns/locale';
import type { Diaper } from '../hooks/useDiapers';

interface DiaperItemProps {
  diaper: Diaper;
}

/**
 * おむつタイプの表示
 */
const diaperTypeDisplay: Record<string, { emoji: string; label: string; color: string }> = {
  wet: {
    emoji: '💧',
    label: 'おしっこ',
    color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  },
  dirty: {
    emoji: '💩',
    label: 'うんち',
    color: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
  },
  both: {
    emoji: '💧💩',
    label: '両方',
    color: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
  },
};

export function DiaperItem({ diaper }: DiaperItemProps) {
  const display = diaperTypeDisplay[diaper.diaper_type];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        {/* 左側: おむつ情報 */}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span
              className={`px-3 py-1 rounded text-sm font-semibold flex items-center gap-1 ${display.color}`}
            >
              <span className="text-lg">{display.emoji}</span>
              {display.label}
            </span>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {format(new Date(diaper.change_time), 'M月d日(E) HH:mm', {
                locale: ja,
              })}
            </span>
          </div>

          {/* メモ */}
          {diaper.notes && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
              {diaper.notes}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
