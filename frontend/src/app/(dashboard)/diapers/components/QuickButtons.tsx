/**
 * QuickButtons
 *
 * ワンタップおむつ交換記録ボタン
 */

'use client';

import { useState } from 'react';
import { Droplet } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface QuickButtonsProps {
  onQuickRecord: (type: 'wet' | 'dirty' | 'both') => Promise<void>;
}

export function QuickButtons({ onQuickRecord }: QuickButtonsProps) {
  const [loading, setLoading] = useState<'wet' | 'dirty' | 'both' | null>(null);

  const handleClick = async (type: 'wet' | 'dirty' | 'both') => {
    setLoading(type);
    try {
      await onQuickRecord(type);
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        クイック記録
      </h3>
      <div className="grid grid-cols-3 gap-3">
        {/* おしっこ */}
        <Button
          variant="primary"
          onClick={() => handleClick('wet')}
          isLoading={loading === 'wet'}
          className="bg-blue-500 hover:bg-blue-600 flex flex-col items-center gap-2 py-6"
        >
          <span className="text-3xl">💧</span>
          <span className="text-sm font-semibold">おしっこ</span>
        </Button>

        {/* うんち */}
        <Button
          variant="primary"
          onClick={() => handleClick('dirty')}
          isLoading={loading === 'dirty'}
          className="bg-amber-600 hover:bg-amber-700 flex flex-col items-center gap-2 py-6"
        >
          <span className="text-3xl">💩</span>
          <span className="text-sm font-semibold">うんち</span>
        </Button>

        {/* 両方 */}
        <Button
          variant="primary"
          onClick={() => handleClick('both')}
          isLoading={loading === 'both'}
          className="bg-purple-600 hover:bg-purple-700 flex flex-col items-center gap-2 py-6"
        >
          <span className="text-3xl">💧💩</span>
          <span className="text-sm font-semibold">両方</span>
        </Button>
      </div>
    </div>
  );
}
