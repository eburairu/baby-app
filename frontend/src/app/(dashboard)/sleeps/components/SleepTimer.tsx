/**
 * SleepTimer
 *
 * 睡眠タイマー表示コンポーネント（1秒更新）
 */

'use client';

import { useState } from 'react';
import { Moon, StopCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useSleepTimer } from '../hooks/useSleepTimer';
import type { Sleep } from '../hooks/useSleeps';

interface SleepTimerProps {
  sleep: Sleep;
  onEnd: (id: number) => Promise<void>;
}

export function SleepTimer({ sleep, onEnd }: SleepTimerProps) {
  const elapsed = useSleepTimer(sleep.start_time);
  const [isEnding, setIsEnding] = useState(false);

  const handleEnd = async () => {
    setIsEnding(true);
    try {
      await onEnd(sleep.id);
    } finally {
      setIsEnding(false);
    }
  };

  return (
    <div className="bg-gradient-to-r from-purple-500 to-indigo-600 rounded-lg shadow-lg p-6 text-white">
      <div className="flex items-center justify-between">
        {/* 左側: タイマー表示 */}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <Moon className="h-6 w-6" />
            <h3 className="text-lg font-semibold">睡眠中</h3>
          </div>

          {/* 経過時間 */}
          <div className="text-5xl font-bold font-mono">
            {String(elapsed.hours).padStart(2, '0')}:
            {String(elapsed.minutes).padStart(2, '0')}:
            {String(elapsed.seconds).padStart(2, '0')}
          </div>

          <p className="text-sm text-purple-100 mt-2">
            {new Date(sleep.start_time).toLocaleString('ja-JP', {
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            })}{' '}
            から
          </p>
        </div>

        {/* 右側: 終了ボタン */}
        <div>
          <Button
            variant="danger"
            size="lg"
            onClick={handleEnd}
            isLoading={isEnding}
            className="bg-white text-purple-600 hover:bg-purple-50"
          >
            <StopCircle className="h-5 w-5 mr-2" />
            睡眠終了
          </Button>
        </div>
      </div>
    </div>
  );
}
