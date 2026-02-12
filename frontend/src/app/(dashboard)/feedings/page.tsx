/**
 * Feeding Records Page
 *
 * 授乳記録ページ
 */

'use client';

import { useState } from 'react';
import { Loader2, Plus, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { toast } from '@/components/ui/Toast';
import { useFeedings } from './hooks/useFeedings';
import { FeedingList } from './components/FeedingList';
import { FeedingForm } from './components/FeedingForm';

export default function FeedingsPage() {
  const {
    feedings,
    baby,
    isLoading,
    createFeeding,
    updateFeeding,
    deleteFeeding,
  } = useFeedings();

  const [showForm, setShowForm] = useState(false);

  // 新規作成
  const handleCreate = async (data: any) => {
    try {
      await createFeeding(data);
      toast.success('作成しました', '授乳記録を登録しました');
      setShowForm(false);
    } catch (error: any) {
      toast.error('作成に失敗しました', error.message);
    }
  };

  // 更新
  const handleUpdate = async (id: number, data: any) => {
    try {
      await updateFeeding(id, data);
      toast.success('更新しました', '授乳記録を更新しました');
    } catch (error: any) {
      toast.error('更新に失敗しました', error.message);
    }
  };

  // 削除
  const handleDelete = async (id: number) => {
    try {
      await deleteFeeding(id);
      toast.success('削除しました', '授乳記録を削除しました');
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
              授乳記録
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              {baby ? `${baby.name}の授乳記録` : '授乳記録を管理します'}
            </p>
          </div>
          <Button variant="primary" onClick={() => setShowForm(!showForm)}>
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
            新しい授乳記録を作成
          </h3>
          <FeedingForm
            onSubmit={handleCreate}
            onCancel={() => setShowForm(false)}
          />
        </div>
      )}

      {/* 授乳記録一覧 */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          記録一覧 ({feedings.length}件)
        </h3>
        <FeedingList
          feedings={feedings}
          onUpdate={handleUpdate}
          onDelete={handleDelete}
        />
      </div>
    </div>
  );
}
