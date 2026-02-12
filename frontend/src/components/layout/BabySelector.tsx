/**
 * BabySelector
 *
 * グローバル赤ちゃん選択コンポーネント
 */

'use client';

import { useBaby } from '@/lib/hooks/useBaby';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/Select';

export function BabySelector() {
  const { babies, selectedBabyId, selectBaby, isLoading } = useBaby();

  if (isLoading || babies.length === 0) {
    return null;
  }

  // 選択中の赤ちゃん名を取得
  const selectedBaby = babies.find((b) => b.id === selectedBabyId);

  return (
    <Select
      value={selectedBabyId?.toString() || ''}
      onValueChange={(value) => selectBaby(Number(value))}
    >
      <SelectTrigger className="w-[180px]">
        <SelectValue>
          {selectedBaby ? selectedBaby.name : '赤ちゃんを選択'}
        </SelectValue>
      </SelectTrigger>
      <SelectContent>
        {babies.map((baby) => (
          <SelectItem key={baby.id} value={baby.id.toString()}>
            {baby.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
