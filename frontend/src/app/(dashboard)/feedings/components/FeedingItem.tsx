/**
 * FeedingItem
 *
 * 個別の授乳記録表示コンポーネント
 */

'use client';

import { useState } from 'react';
import { format } from 'date-fns';
import { ja } from 'date-fns/locale';
import { Pencil, Trash2, Baby, Clock, Droplet } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/Dialog';
import type { Feeding } from '../hooks/useFeedings';
import { FeedingForm } from './FeedingForm';

interface FeedingItemProps {
  feeding: Feeding;
  onUpdate: (id: number, data: any) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}

/**
 * 授乳タイプの日本語表示
 */
const feedingTypeLabels: Record<string, string> = {
  breast: '母乳',
  bottle: 'ミルク',
  both: '混合',
};

/**
 * 授乳タイプの色クラス
 */
const feedingTypeColors: Record<string, string> = {
  breast: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200',
  bottle: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  both: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
};

export function FeedingItem({ feeding, onUpdate, onDelete }: FeedingItemProps) {
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleUpdate = async (data: any) => {
    await onUpdate(feeding.id, data);
    setEditModalOpen(false);
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await onDelete(feeding.id);
      setDeleteModalOpen(false);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <>
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 hover:shadow-md transition-shadow">
        <div className="flex items-start justify-between">
          {/* 左側: 授乳情報 */}
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span
                className={`px-2 py-1 rounded text-sm font-semibold ${
                  feedingTypeColors[feeding.feeding_type]
                }`}
              >
                {feedingTypeLabels[feeding.feeding_type]}
              </span>
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {format(new Date(feeding.feeding_time), 'M月d日(E) HH:mm', {
                  locale: ja,
                })}
              </span>
            </div>

            {/* 詳細情報 */}
            <div className="space-y-1">
              {feeding.amount_ml && (
                <div className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                  <Droplet className="h-4 w-4" />
                  <span>{feeding.amount_ml}ml</span>
                </div>
              )}
              {feeding.duration_minutes && (
                <div className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                  <Clock className="h-4 w-4" />
                  <span>{feeding.duration_minutes}分</span>
                </div>
              )}
              {feeding.notes && (
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                  {feeding.notes}
                </p>
              )}
            </div>
          </div>

          {/* 右側: アクションボタン */}
          <div className="flex gap-2 ml-4">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setEditModalOpen(true)}
            >
              <Pencil className="h-4 w-4" />
            </Button>
            <Button
              variant="danger"
              size="sm"
              onClick={() => setDeleteModalOpen(true)}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* 編集モーダル */}
      <Dialog open={editModalOpen} onOpenChange={setEditModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>授乳記録を編集</DialogTitle>
          </DialogHeader>
          <FeedingForm
            feeding={feeding}
            onSubmit={handleUpdate}
            onCancel={() => setEditModalOpen(false)}
          />
        </DialogContent>
      </Dialog>

      {/* 削除確認モーダル */}
      <Dialog open={deleteModalOpen} onOpenChange={setDeleteModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>削除の確認</DialogTitle>
          </DialogHeader>
          <p className="text-gray-700 dark:text-gray-300 mb-4">
            この授乳記録を削除してもよろしいですか？
            <br />
            <span className="text-sm text-gray-500">
              {format(new Date(feeding.feeding_time), 'M月d日(E) HH:mm', {
                locale: ja,
              })}{' '}
              - {feedingTypeLabels[feeding.feeding_type]}
            </span>
          </p>
          <div className="flex gap-3">
            <Button
              variant="secondary"
              onClick={() => setDeleteModalOpen(false)}
              disabled={isDeleting}
            >
              キャンセル
            </Button>
            <Button
              variant="danger"
              onClick={handleDelete}
              isLoading={isDeleting}
            >
              削除
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
