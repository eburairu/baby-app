/**
 * ContractionTimer
 *
 * 陣痛タイマーメインコンポーネント（開始/終了ボタン + リアルタイムタイマー）
 */

'use client';

import { useState } from 'react';
import { Play, Square, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useContractionTimer } from '../hooks/useContractionTimer';
import type { Contraction } from '../hooks/useContractions';

interface ContractionTimerProps {
  ongoing: Contraction | null;
  onStart: () => Promise<void>;
  onEnd: (id: number) => Promise<void>;
}

export function ContractionTimer({ ongoing, onStart, onEnd }: ContractionTimerProps) {
  const [isStarting, setIsStarting] = useState(false);
  const [isEnding, setIsEnding] = useState(false);

  const timer = useContractionTimer(ongoing?.start_time || null, ongoing?.is_ongoing || false);

  const handleStart = async () => {
    setIsStarting(true);
    try {
      await onStart();
    } finally {
      setIsStarting(false);
    }
  };

  const handleEnd = async () => {
    if (!ongoing) return;
    setIsEnding(true);
    try {
      await onEnd(ongoing.id);
    } finally {
      setIsEnding(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          陣痛タイマー
        </h2>

        {ongoing ? (
          <>
            {/* タイマー表示 */}
            <div className="my-8">
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">経過時間</p>
              <p className="text-6xl font-bold text-indigo-600 dark:text-indigo-400 font-mono">
                {timer.elapsed}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                {new Date(ongoing.start_time).toLocaleString('ja-JP')} から
              </p>
            </div>

            {/* 終了ボタン */}
            <Button
              variant="danger"
              size="lg"
              onClick={handleEnd}
              isLoading={isEnding}
              className="w-full md:w-auto min-w-[200px]"
            >
              {isEnding ? (
                <>
                  <Loader2 className="animate-spin h-6 w-6 mr-2" />
                  終了中...
                </>
              ) : (
                <>
                  <Square className="h-6 w-6 mr-2" />
                  陣痛終了
                </>
              )}
            </Button>
          </>
        ) : (
          <>
            {/* 待機状態 */}
            <div className="my-8">
              <p className="text-gray-500 dark:text-gray-400 mb-6">
                陣痛が始まったらボタンを押してください
              </p>
              <div className="text-6xl font-bold text-gray-300 dark:text-gray-600 font-mono">
                0:00
              </div>
            </div>

            {/* 開始ボタン */}
            <Button
              variant="primary"
              size="lg"
              onClick={handleStart}
              isLoading={isStarting}
              className="w-full md:w-auto min-w-[200px]"
            >
              {isStarting ? (
                <>
                  <Loader2 className="animate-spin h-6 w-6 mr-2" />
                  開始中...
                </>
              ) : (
                <>
                  <Play className="h-6 w-6 mr-2" />
                  陣痛開始
                </>
              )}
            </Button>
          </>
        )}

        {/* ヒント */}
        <div className="mt-6 text-sm text-gray-500 dark:text-gray-400">
          <p>💡 陣痛が来たら「陣痛開始」、痛みが引いたら「陣痛終了」を押してください</p>
        </div>
      </div>
    </div>
  );
}
