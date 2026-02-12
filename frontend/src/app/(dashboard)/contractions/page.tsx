/**
 * Contractions Page
 *
 * 陣痛タイマーページ
 */

'use client';

import { useState } from 'react';
import { Loader2, Plus, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { toast } from '@/components/ui/Toast';
import { useContractions } from './hooks/useContractions';
import { ContractionTimer } from './components/ContractionTimer';
import { ContractionStats } from './components/ContractionStats';
import { ContractionList } from './components/ContractionList';
import { ContractionForm } from './components/ContractionForm';

export default function ContractionsPage() {
  const {
    contractions,
    ongoing,
    stats,
    baby,
    isLoading,
    startContraction,
    endContraction,
    createContraction,
    updateContraction,
    deleteContraction,
  } = useContractions();

  const [showForm, setShowForm] = useState(false);

  // 陣痛開始
  const handleStart = async () => {
    try {
      await startContraction();
      toast.success('開始しました', '陣痛タイマーを開始しました');
    } catch (error: any) {
      toast.error('開始に失敗しました', error.message);
    }
  };

  // 陣痛終了
  const handleEnd = async (id: number) => {
    try {
      await endContraction(id);
      toast.success('終了しました', '陣痛を記録しました');
    } catch (error: any) {
      toast.error('終了に失敗しました', error.message);
    }
  };

  // 手動作成
  const handleCreate = async (data: any) => {
    try {
      await createContraction(data);
      toast.success('作成しました', '陣痛記録を登録しました');
      setShowForm(false);
    } catch (error: any) {
      toast.error('作成に失敗しました', error.message);
    }
  };

  // 更新
  const handleUpdate = async (id: number, data: any) => {
    try {
      await updateContraction(id, data);
      toast.success('更新しました', '陣痛記録を更新しました');
    } catch (error: any) {
      toast.error('更新に失敗しました', error.message);
    }
  };

  // 削除
  const handleDelete = async (id: number) => {
    try {
      await deleteContraction(id);
      toast.success('削除しました', '陣痛記録を削除しました');
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
              陣痛タイマー
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              {baby ? `${baby.name}の陣痛記録` : '陣痛を記録します'}
            </p>
          </div>
          <Button
            variant="secondary"
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
                手動で追加
              </>
            )}
          </Button>
        </div>
      </div>

      {/* 手動追加フォーム（アコーディオン） */}
      {showForm && (
        <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            陣痛記録を手動で追加
          </h3>
          <ContractionForm
            onSubmit={handleCreate}
            onCancel={() => setShowForm(false)}
          />
        </div>
      )}

      {/* タイマー */}
      <ContractionTimer
        ongoing={ongoing}
        onStart={handleStart}
        onEnd={handleEnd}
      />

      {/* 統計 */}
      {contractions.length > 0 && <ContractionStats stats={stats} />}

      {/* 記録一覧 */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          記録一覧 ({contractions.length}件)
          <span className="ml-2 text-sm text-gray-500 dark:text-gray-400 font-normal">
            5秒ごとに自動更新
          </span>
        </h3>
        <ContractionList
          contractions={contractions}
          onUpdate={handleUpdate}
          onDelete={handleDelete}
        />
      </div>
    </div>
  );
}
