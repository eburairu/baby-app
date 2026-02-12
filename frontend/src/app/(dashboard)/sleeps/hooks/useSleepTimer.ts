/**
 * useSleepTimer
 *
 * 睡眠タイマーフック（1秒更新）
 */

import { useEffect, useState } from 'react';

/**
 * 経過時間を計算
 */
function calculateElapsedTime(startTime: string): {
  hours: number;
  minutes: number;
  seconds: number;
} {
  const start = new Date(startTime).getTime();
  const now = Date.now();
  const elapsed = Math.max(0, Math.floor((now - start) / 1000)); // 秒単位

  const hours = Math.floor(elapsed / 3600);
  const minutes = Math.floor((elapsed % 3600) / 60);
  const seconds = elapsed % 60;

  return { hours, minutes, seconds };
}

/**
 * 睡眠タイマーフック
 */
export function useSleepTimer(startTime: string | null) {
  const [elapsed, setElapsed] = useState<{
    hours: number;
    minutes: number;
    seconds: number;
  }>({ hours: 0, minutes: 0, seconds: 0 });

  useEffect(() => {
    if (!startTime) {
      setElapsed({ hours: 0, minutes: 0, seconds: 0 });
      return;
    }

    // 初期値を設定
    setElapsed(calculateElapsedTime(startTime));

    // 1秒ごとに更新
    const interval = setInterval(() => {
      setElapsed(calculateElapsedTime(startTime));
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime]);

  return elapsed;
}
