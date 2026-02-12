/**
 * Schedules Page
 *
 * スケジュール管理ページ
 */

'use client';

import { useState } from 'react';
import { Loader2, Plus, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { toast } from '@/components/ui/Toast';
import { useSchedules } from './hooks/useSchedules';
import { ScheduleList } from './components/ScheduleList';
import { ScheduleForm } from './components/ScheduleForm';

export default function SchedulesPage() {
  const {
    schedules,
    baby,
    isLoading,
    createSchedule,
    updateSchedule,
    toggleSchedule,
    deleteSchedule,
  } = useSchedules();

  const [showForm, setShowForm] = useState(false);

  // 新規作成
  const handleCreate = async (data: any) => {
    try {
      await createSchedule(data);
      toast.success('作成しました', 'スケジュールを登録しました');
      setShowForm(false);
    } catch (error: any) {
      toast.error('作成に失敗しました', error.message);
    }
  };

  // 更新
  const handleUpdate = async (id: number, data: any) => {
    try {
      await updateSchedule(id, data);
      toast.success('更新しました', 'スケジュールを更新しました');
    } catch (error: any) {
      toast.error('更新に失敗しました', error.message);
    }
  };

  // 完了トグル
  const handleToggle = async (id: number) => {
    try {
      await toggleSchedule(id);
    } catch (error: any) {
      toast.error('更新に失敗しました', error.message);
    }
  };

  // 削除
  const handleDelete = async (id: number) => {
    try {
      await deleteSchedule(id);
      toast.success('削除しました', 'スケジュールを削除しました');
    } catch (error: any) {
      toast.error('削除に失敗しました', error.message);
    }
  };

  // ローディング中
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="animate-spin h-8 w-8 text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              スケジュール
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              {baby ? `${baby.name}のスケジュール` : 'スケジュールを管理します'}
            </p>
          </div>
          <Button
            variant="primary"
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? (
              <>
                <ChevronUp className="h-5 w-5 mr-2" />
                閉じる
              </>
            ) : (
              <>
                <Plus className="h-5 w-5 mr-2" />
                新規作成
              </>
            )}
          </Button>
        </div>
      </div>

      {/* 新規作成フォーム（アコーディオン） */}
      {showForm && (
        <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            新しいスケジュールを作成
          </h3>
          <ScheduleForm
            onSubmit={handleCreate}
            onCancel={() => setShowForm(false)}
          />
        </div>
      )}

      {/* スケジュール一覧 */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          一覧 ({schedules.length}件)
        </h3>
        <ScheduleList
          schedules={schedules}
          onUpdate={handleUpdate}
          onDelete={handleDelete}
          onToggle={handleToggle}
        />
      </div>
    </div>
  );
}
