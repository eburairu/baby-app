/**
 * RecentRecords
 *
 * 最新記録表示（授乳、睡眠、おむつ）
 */

'use client';

import { formatDistanceToNow } from 'date-fns';
import { ja } from 'date-fns/locale';
import type { DashboardData } from '../hooks/useDashboard';

interface RecentRecordsProps {
  data: DashboardData;
}

export function RecentRecords({ data }: RecentRecordsProps) {
  const { recent_records, perms } = data;

  if (!recent_records) {
    return null;
  }

  const hasRecords =
    (recent_records.feedings && recent_records.feedings.length > 0) ||
    (recent_records.sleeps && recent_records.sleeps.length > 0) ||
    (recent_records.diapers && recent_records.diapers.length > 0);

  if (!hasRecords) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          最新の記録
        </h3>
        <p className="text-gray-500 dark:text-gray-400 text-center py-8">
          まだ記録がありません
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        最新の記録
      </h3>

      <div className="space-y-4">
        {/* 授乳記録 */}
        {perms.feeding && recent_records.feedings && recent_records.feedings.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              授乳
            </h4>
            <div className="space-y-2">
              {recent_records.feedings.slice(0, 3).map((feeding: any, idx: number) => (
                <div
                  key={idx}
                  className="flex justify-between items-center py-2 px-3 bg-gray-50 dark:bg-gray-700 rounded"
                >
                  <div>
                    <span className="text-sm text-gray-900 dark:text-white">
                      {feeding.feeding_type === 'breast' ? '母乳' :
                       feeding.feeding_type === 'formula' ? 'ミルク' : '混合'}
                    </span>
                    {feeding.amount_ml && (
                      <span className="text-sm text-gray-600 dark:text-gray-400 ml-2">
                        {feeding.amount_ml}ml
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {formatDistanceToNow(new Date(feeding.feeding_time), {
                      addSuffix: true,
                      locale: ja,
                    })}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 睡眠記録 */}
        {perms.sleep && recent_records.sleeps && recent_records.sleeps.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              睡眠
            </h4>
            <div className="space-y-2">
              {recent_records.sleeps.slice(0, 3).map((sleep: any, idx: number) => (
                <div
                  key={idx}
                  className="flex justify-between items-center py-2 px-3 bg-gray-50 dark:bg-gray-700 rounded"
                >
                  <div>
                    <span className="text-sm text-gray-900 dark:text-white">
                      {sleep.duration_minutes ? `${sleep.duration_minutes}分` : '睡眠中'}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {formatDistanceToNow(new Date(sleep.sleep_start), {
                      addSuffix: true,
                      locale: ja,
                    })}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* おむつ記録 */}
        {perms.diaper && recent_records.diapers && recent_records.diapers.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              おむつ
            </h4>
            <div className="space-y-2">
              {recent_records.diapers.slice(0, 3).map((diaper: any, idx: number) => (
                <div
                  key={idx}
                  className="flex justify-between items-center py-2 px-3 bg-gray-50 dark:bg-gray-700 rounded"
                >
                  <div>
                    <span className="text-sm text-gray-900 dark:text-white">
                      {diaper.type === 'pee' ? '💧 おしっこ' :
                       diaper.type === 'poop' ? '💩 うんち' : '💧💩 両方'}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {formatDistanceToNow(new Date(diaper.changed_at), {
                      addSuffix: true,
                      locale: ja,
                    })}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
