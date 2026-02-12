/**
 * GrowthList
 *
 * 成長記録一覧表示コンポーネント
 */

'use client';

import { GrowthItem } from './GrowthItem';
import type { Growth } from '../hooks/useGrowths';

interface GrowthListProps {
  growths: Growth[];
  onUpdate: (id: number, data: any) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}

export function GrowthList({ growths, onUpdate, onDelete }: GrowthListProps) {
  if (growths.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8">
        <p className="text-center text-gray-500 dark:text-gray-400">
          成長記録がありません
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {growths.map((growth) => (
        <GrowthItem
          key={growth.id}
          growth={growth}
          onUpdate={onUpdate}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
