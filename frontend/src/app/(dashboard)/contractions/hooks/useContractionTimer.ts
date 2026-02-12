/**
 * useContractionTimer
 *
 * 陣痛タイマーのリアルタイム経過時間計算フック
 */

'use client';

import { useState, useEffect } from 'react';

interface TimerState {
  elapsed: string;
  elapsedSeconds: number;
}

/**
 * 陣痛の経過時間を計算
 */
function calculateElapsedTime(startTime: string): TimerState {
  const start = new Date(startTime).getTime();
  const now = new Date().getTime();
  const diffSeconds = Math.floor((now - start) / 1000);

  const minutes = Math.floor(diffSeconds / 60);
  const seconds = diffSeconds % 60;

  return {
    elapsed: `${minutes}:${seconds.toString().padStart(2, '0')}`,
    elapsedSeconds: diffSeconds,
  };
}

/**
 * 進行中の陣痛タイマーをリアルタイムで更新するフック
 *
 * @param startTime 陣痛開始時刻（ISO形式）
 * @param isOngoing 継続中かどうか
 * @returns 経過時間（"分:秒" 形式）と秒数
 */
export function useContractionTimer(startTime: string | null, isOngoing: boolean) {
  const [timer, setTimer] = useState<TimerState>({ elapsed: '0:00', elapsedSeconds: 0 });

  useEffect(() => {
    if (!startTime || !isOngoing) {
      setTimer({ elapsed: '0:00', elapsedSeconds: 0 });
      return;
    }

    // 初回計算
    setTimer(calculateElapsedTime(startTime));

    // 1秒ごとに更新
    const interval = setInterval(() => {
      setTimer(calculateElapsedTime(startTime));
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime, isOngoing]);

  return timer;
}
