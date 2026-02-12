/**
 * StatsCards
 *
 * 統計カード表示（授乳、睡眠、おむつ、成長）
 */

'use client';

import { Baby, Moon, Droplet, Scale } from 'lucide-react';
import type { DashboardData } from '../hooks/useDashboard';

interface StatsCardsProps {
  data: DashboardData;
}

export function StatsCards({ data }: StatsCardsProps) {
  const { feeding_stats, sleep_stats, diaper_stats, latest_growth, perms } = data;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* 授乳統計 */}
      {perms.feeding && feeding_stats && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">授乳回数</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                {feeding_stats.last_24h_count || feeding_stats.count || 0}回
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                過去{feeding_stats.period_days || 7}日間
              </p>
            </div>
            <div className="p-3 bg-indigo-100 dark:bg-indigo-900 rounded-full">
              <Baby className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
            </div>
          </div>
          {(feeding_stats.last_24h_total_ml || feeding_stats.avg_amount_ml) && (
            <div className="mt-3 pt-3 border-t dark:border-gray-700">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {feeding_stats.last_24h_total_ml ? (
                  <>総量: <span className="font-semibold">{feeding_stats.last_24h_total_ml}ml</span></>
                ) : (
                  <>平均: <span className="font-semibold">{feeding_stats.avg_amount_ml}ml</span></>
                )}
              </p>
            </div>
          )}
        </div>
      )}

      {/* 睡眠統計 */}
      {perms.sleep && sleep_stats && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">睡眠時間</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                {sleep_stats.total_hours !== undefined
                  ? `${sleep_stats.total_hours.toFixed(1)}時間`
                  : sleep_stats.last_24h_total_minutes
                  ? `${Math.floor(sleep_stats.last_24h_total_minutes / 60)}時間${sleep_stats.last_24h_total_minutes % 60}分`
                  : '0時間'}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                過去{sleep_stats.period_days || 7}日間
              </p>
            </div>
            <div className="p-3 bg-purple-100 dark:bg-purple-900 rounded-full">
              <Moon className="h-6 w-6 text-purple-600 dark:text-purple-400" />
            </div>
          </div>
          {sleep_stats.currently_sleeping && (
            <div className="mt-3 pt-3 border-t dark:border-gray-700">
              <p className="text-sm text-green-600 dark:text-green-400 font-semibold">
                💤 睡眠中
              </p>
            </div>
          )}
        </div>
      )}

      {/* おむつ統計 */}
      {perms.diaper && diaper_stats && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">おむつ交換</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                {diaper_stats.last_24h_count || diaper_stats.count || 0}回
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                過去{diaper_stats.period_days || 7}日間
              </p>
            </div>
            <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-full">
              <Droplet className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
          {(diaper_stats.last_24h_pee || diaper_stats.last_24h_poop) && (
            <div className="mt-3 pt-3 border-t dark:border-gray-700">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">
                  💧 {diaper_stats.last_24h_pee || 0}回
                </span>
                <span className="text-gray-600 dark:text-gray-400">
                  💩 {diaper_stats.last_24h_poop || 0}回
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 成長記録 */}
      {perms.growth && latest_growth && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">最新の体重</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                {latest_growth.weight_kg ? `${latest_growth.weight_kg}kg` : '-'}
              </p>
              {latest_growth.height_cm && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  身長: {latest_growth.height_cm}cm
                </p>
              )}
            </div>
            <div className="p-3 bg-green-100 dark:bg-green-900 rounded-full">
              <Scale className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
