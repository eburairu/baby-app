/**
 * Dashboard Page
 *
 * ダッシュボードメインページ
 */

'use client';

import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useDashboard } from './hooks/useDashboard';
import { StatsCards } from './components/StatsCards';
import { RecentRecords } from './components/RecentRecords';
import { PrenatalInfo } from './components/PrenatalInfo';
import { QuickActions } from './components/QuickActions';
import { BornModal } from './components/BornModal';

export default function DashboardPage() {
  const { data, isLoading, error, mutate } = useDashboard();
  const [bornModalOpen, setBornModalOpen] = useState(false);

  // ローディング中
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="animate-spin h-8 w-8 text-indigo-600" />
      </div>
    );
  }

  // エラーまたはデータなし
  if (error || !data) {
    return (
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-8">
        <p className="text-center text-gray-500 dark:text-gray-400 mb-4">
          データを読み込めませんでした
        </p>
        <div className="flex justify-center">
          <button
            onClick={() => mutate()}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 text-sm"
          >
            再読み込み
          </button>
        </div>
      </div>
    );
  }

  const { baby, prenatal_info } = data;

  // プレママ期かつ出生記録モーダルを表示するボタン
  const showBornButton = baby && !baby.birthday && baby.due_date;

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              {baby ? `${baby.name}のダッシュボード` : 'ダッシュボード'}
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              最新の記録と統計を確認できます
            </p>
          </div>
          {showBornButton && (
            <Button
              variant="primary"
              onClick={() => setBornModalOpen(true)}
            >
              🎉 誕生日を記録
            </Button>
          )}
        </div>
      </div>

      {/* プレママ期情報 */}
      {prenatal_info && <PrenatalInfo data={data} />}

      {/* 統計カード */}
      <StatsCards data={data} />

      {/* クイックアクション */}
      <QuickActions data={data} />

      {/* 最新記録 */}
      <RecentRecords data={data} />

      {/* 出生記録モーダル */}
      {baby && showBornButton && (
        <BornModal
          babyId={baby.id}
          babyName={baby.name}
          open={bornModalOpen}
          onOpenChange={setBornModalOpen}
          onSuccess={() => mutate()}
        />
      )}
    </div>
  );
}
