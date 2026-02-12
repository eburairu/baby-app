/**
 * Sleep Records Page
 *
 * 睡眠記録ページ
 */

'use client';

import { useState } from 'react';
import { Loader2, Plus, PlayCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { toast } from '@/components/ui/Toast';
import { useSleeps } from './hooks/useSleeps';
import { SleepTimer } from './components/SleepTimer';
import { SleepList } from './components/SleepList';
import { SleepForm } from './components/SleepForm';

export default function SleepsPage() {
  const {
    sleeps,
    baby,
    ongoingSleep,
    isLoading,
    startSleep,
    endSleep,
    createSleep,
  } = useSleeps();

  const [showForm, setShowForm] = useState(false);

  // 睡眠開始
  const handleStart = async () => {
    try {
      await startSleep();
      toast.success('開始しました', '睡眠記録を開始しました');
    } catch (error: any) {
      toast.error('開始に失敗しました', error.message);
    }
  };

  // 睡眠終了
  const handleEnd = async (id: number) => {
    try {
      await endSleep(id);
      toast.success('終了しました', '睡眠記録を終了しました');
    } catch (error: any) {
      toast.error('終了に失敗しました', error.message);
    }
  };

  // 手動作成
  const handleCreate = async (data: any) => {
    try {
      await createSleep(data);
      toast.success('作成しました', '睡眠記録を登録しました');
      setShowForm(false);
    } catch (error: any) {
      toast.error('作成に失敗しました', error.message);
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
              睡眠記録
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              {baby ? `${baby.name}の睡眠記録` : '睡眠記録を管理します'}
            </p>
          </div>
          {!ongoingSleep && (
            <Button variant="primary" onClick={handleStart}>
              <PlayCircle className="h-5 w-5 mr-2" />
              睡眠開始
            </Button>
          )}
        </div>
      </div>

      {/* タイマー表示（進行中の場合） */}
      {ongoingSleep && <SleepTimer sleep={ongoingSleep} onEnd={handleEnd} />}

      {/* 手動追加ボタン */}
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6">
        <Button
          variant="secondary"
          onClick={() => setShowForm(!showForm)}
          className="w-full"
        >
          {showForm ? (
            <>
              <ChevronUp className="h-5 w-5 mr-2" />
              閉じる
            </>
          ) : (
            <>
              <Plus className="h-5 w-5 mr-2" />
              手動で記録を追加
            </>
          )}
        </Button>

        {/* 手動追加フォーム（アコーディオン） */}
        {showForm && (
          <div className="mt-4 pt-4 border-t dark:border-gray-700">
            <SleepForm
              onSubmit={handleCreate}
              onCancel={() => setShowForm(false)}
            />
          </div>
        )}
      </div>

      {/* 睡眠記録一覧 */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          記録一覧 ({sleeps.length}件)
        </h3>
        <SleepList sleeps={sleeps} />
      </div>
    </div>
  );
}
