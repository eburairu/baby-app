/**
 * DiaperList
 *
 * おむつ交換記録一覧表示コンポーネント
 */

'use client';

import { DiaperItem } from './DiaperItem';
import type { Diaper } from '../hooks/useDiapers';

interface DiaperListProps {
  diapers: Diaper[];
}

export function DiaperList({ diapers }: DiaperListProps) {
  if (diapers.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8">
        <p className="text-center text-gray-500 dark:text-gray-400">
          おむつ交換記録がありません
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {diapers.map((diaper) => (
        <DiaperItem key={diaper.id} diaper={diaper} />
      ))}
    </div>
  );
}
