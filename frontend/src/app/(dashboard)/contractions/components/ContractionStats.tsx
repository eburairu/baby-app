/**
 * ContractionStats
 *
 * 陣痛統計表示コンポーネント
 */

'use client';

import { Clock, Timer, Activity } from 'lucide-react';

interface Statistics {
  count: number;
  avg_duration_seconds: number;
  avg_interval_seconds: number;
  last_interval_seconds: number | null;
  period_hours: number;
}

interface ContractionStatsProps {
  stats: Statistics;
}

/**
 * 秒を「分:秒」形式に変換
 */
function formatSeconds(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

export function ContractionStats({ stats }: ContractionStatsProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        直近{stats.period_hours}時間の統計
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* 回数 */}
        <div className="flex items-start gap-3">
          <div className="p-2 bg-indigo-100 dark:bg-indigo-900 rounded-lg">
            <Activity className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
          </div>
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">回数</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {stats.count}回
            </p>
          </div>
        </div>

        {/* 平均持続時間 */}
        <div className="flex items-start gap-3">
          <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
            <Timer className="h-5 w-5 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">平均持続</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {formatSeconds(stats.avg_duration_seconds)}
            </p>
          </div>
        </div>

        {/* 平均間隔 */}
        <div className="flex items-start gap-3">
          <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
            <Clock className="h-5 w-5 text-green-600 dark:text-green-400" />
          </div>
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">平均間隔</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {stats.avg_interval_seconds > 0
                ? formatSeconds(stats.avg_interval_seconds)
                : '-'}
            </p>
          </div>
        </div>
      </div>

      {/* 5-1-1ルールのヒント */}
      {stats.count >= 3 && stats.avg_interval_seconds > 0 && (
        <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
          <p className="text-sm text-yellow-800 dark:text-yellow-200">
            💡 <strong>5-1-1ルール</strong>: 陣痛が5分間隔で1分以上続き、これが1時間続いたら病院へ連絡しましょう
          </p>
        </div>
      )}
    </div>
  );
}
