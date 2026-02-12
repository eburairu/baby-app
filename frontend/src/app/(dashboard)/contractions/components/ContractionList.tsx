/**
 * ContractionList
 *
 * 陣痛記録一覧表示コンポーネント
 */

'use client';

import { ContractionItem } from './ContractionItem';
import type { Contraction } from '../hooks/useContractions';

interface ContractionListProps {
  contractions: Contraction[];
  onUpdate: (id: number, data: any) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}

export function ContractionList({ contractions, onUpdate, onDelete }: ContractionListProps) {
  if (contractions.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8">
        <p className="text-center text-gray-500 dark:text-gray-400">
          陣痛記録がありません
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {contractions.map((contraction) => (
        <ContractionItem
          key={contraction.id}
          contraction={contraction}
          onUpdate={onUpdate}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
