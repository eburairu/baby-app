/**
 * ScheduleList
 *
 * スケジュール一覧表示コンポーネント
 */

'use client';

import { ScheduleItem } from './ScheduleItem';
import type { Schedule } from '../hooks/useSchedules';

interface ScheduleListProps {
  schedules: Schedule[];
  onUpdate: (id: number, data: any) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
  onToggle: (id: number) => Promise<void>;
}

export function ScheduleList({ schedules, onUpdate, onDelete, onToggle }: ScheduleListProps) {
  if (schedules.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8">
        <p className="text-center text-gray-500 dark:text-gray-400">
          スケジュールがありません
        </p>
      </div>
    );
  }

  // 完了/未完了で分類
  const pendingSchedules = schedules.filter((s) => !s.is_completed);
  const completedSchedules = schedules.filter((s) => s.is_completed);

  return (
    <div className="space-y-6">
      {/* 未完了のスケジュール */}
      {pendingSchedules.length > 0 && (
        <div>
          <h3 className="text-md font-semibold text-gray-700 dark:text-gray-300 mb-3">
            予定 ({pendingSchedules.length}件)
          </h3>
          <div className="space-y-3">
            {pendingSchedules.map((schedule) => (
              <ScheduleItem
                key={schedule.id}
                schedule={schedule}
                onUpdate={onUpdate}
                onDelete={onDelete}
                onToggle={onToggle}
              />
            ))}
          </div>
        </div>
      )}

      {/* 完了したスケジュール */}
      {completedSchedules.length > 0 && (
        <div>
          <h3 className="text-md font-semibold text-gray-700 dark:text-gray-300 mb-3">
            完了 ({completedSchedules.length}件)
          </h3>
          <div className="space-y-3">
            {completedSchedules.map((schedule) => (
              <ScheduleItem
                key={schedule.id}
                schedule={schedule}
                onUpdate={onUpdate}
                onDelete={onDelete}
                onToggle={onToggle}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
