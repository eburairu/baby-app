/**
 * SleepList
 *
 * 睡眠記録一覧表示コンポーネント
 */

'use client';

import { SleepItem } from './SleepItem';
import type { Sleep } from '../hooks/useSleeps';

interface SleepListProps {
  sleeps: Sleep[];
}

export function SleepList({ sleeps }: SleepListProps) {
  if (sleeps.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8">
        <p className="text-center text-gray-500 dark:text-gray-400">
          睡眠記録がありません
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {sleeps.map((sleep) => (
        <SleepItem key={sleep.id} sleep={sleep} />
      ))}
    </div>
  );
}
