/**
 * FeedingList
 *
 * 授乳記録一覧表示コンポーネント
 */

'use client';

import { FeedingItem } from './FeedingItem';
import type { Feeding } from '../hooks/useFeedings';

interface FeedingListProps {
  feedings: Feeding[];
  onUpdate: (id: number, data: any) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}

export function FeedingList({ feedings, onUpdate, onDelete }: FeedingListProps) {
  if (feedings.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8">
        <p className="text-center text-gray-500 dark:text-gray-400">
          授乳記録がありません
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {feedings.map((feeding) => (
        <FeedingItem
          key={feeding.id}
          feeding={feeding}
          onUpdate={onUpdate}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
