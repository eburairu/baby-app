/**
 * Diaper Records Page
 *
 * おむつ交換記録ページ
 */

'use client';

import { useState } from 'react';
import { Loader2, Plus, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { toast } from '@/components/ui/Toast';
import { useDiapers } from './hooks/useDiapers';
import { QuickButtons } from './components/QuickButtons';
import { DiaperList } from './components/DiaperList';
import { DiaperForm } from './components/DiaperForm';

export default function DiapersPage() {
  const { diapers, baby, isLoading, quickRecord, createDiaper } = useDiapers();

  const [showForm, setShowForm] = useState(false);

  // クイック記録
  const handleQuickRecord = async (type: 'wet' | 'dirty' | 'both') => {
    try {
      await quickRecord(type);
      const labels = {
        wet: 'おしっこ',
        dirty: 'うんち',
        both: '両方',
      };
      toast.success('記録しました', `${labels[type]}を記録しました`);
    } catch (error: any) {
      toast.error('記録に失敗しました', error.message);
    }
  };

  // 詳細記録
  const handleCreate = async (data: any) => {
    try {
      await createDiaper(data);
      toast.success('作成しました', 'おむつ交換記録を登録しました');
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
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            おむつ交換記録
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            {baby ? `${baby.name}のおむつ交換記録` : 'おむつ交換記録を管理します'}
          </p>
        </div>
      </div>

      {/* クイック記録ボタン */}
      <QuickButtons onQuickRecord={handleQuickRecord} />

      {/* 詳細入力フォーム */}
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
              詳細を入力して記録
            </>
          )}
        </Button>

        {/* 詳細入力フォーム（アコーディオン） */}
        {showForm && (
          <div className="mt-4 pt-4 border-t dark:border-gray-700">
            <DiaperForm
              onSubmit={handleCreate}
              onCancel={() => setShowForm(false)}
            />
          </div>
        )}
      </div>

      {/* おむつ交換記録一覧 */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          記録一覧 ({diapers.length}件)
        </h3>
        <DiaperList diapers={diapers} />
      </div>
    </div>
  );
}
