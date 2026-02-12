/**
 * ContractionItem
 *
 * 個別の陣痛記録表示コンポーネント
 */

'use client';

import { useState } from 'react';
import { format } from 'date-fns';
import { ja } from 'date-fns/locale';
import { Pencil, Trash2, Timer, Clock } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/Dialog';
import type { Contraction } from '../hooks/useContractions';
import { ContractionForm } from './ContractionForm';

interface ContractionItemProps {
  contraction: Contraction;
  onUpdate: (id: number, data: any) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}

export function ContractionItem({ contraction, onUpdate, onDelete }: ContractionItemProps) {
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleUpdate = async (data: any) => {
    await onUpdate(contraction.id, data);
    setEditModalOpen(false);
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await onDelete(contraction.id);
      setDeleteModalOpen(false);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <>
      <div
        className={`rounded-lg shadow p-4 hover:shadow-md transition-shadow ${
          contraction.is_ongoing
            ? 'bg-indigo-50 dark:bg-indigo-900/20 border-2 border-indigo-500'
            : 'bg-white dark:bg-gray-800'
        }`}
      >
        <div className="flex items-start justify-between">
          {/* 左側: 陣痛情報 */}
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-sm font-semibold text-gray-900 dark:text-white">
                {format(new Date(contraction.start_time), 'yyyy年M月d日(E) HH:mm', {
                  locale: ja,
                })}
              </span>
              {contraction.is_ongoing && (
                <span className="px-2 py-1 bg-indigo-600 text-white text-xs font-bold rounded-full animate-pulse">
                  進行中
                </span>
              )}
            </div>

            {/* 測定値 */}
            <div className="grid grid-cols-2 gap-4">
              {/* 持続時間 */}
              <div>
                <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 mb-1">
                  <Timer className="h-3 w-3" />
                  <span>持続時間</span>
                </div>
                <div className="text-lg font-bold text-blue-600 dark:text-blue-400 font-mono">
                  {contraction.duration_display}
                </div>
              </div>

              {/* 間隔 */}
              {contraction.interval_display !== '-' && (
                <div>
                  <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 mb-1">
                    <Clock className="h-3 w-3" />
                    <span>前回からの間隔</span>
                  </div>
                  <div className="text-lg font-bold text-green-600 dark:text-green-400 font-mono">
                    {contraction.interval_display}
                  </div>
                </div>
              )}
            </div>

            {/* メモ */}
            {contraction.notes && (
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-3">
                {contraction.notes}
              </p>
            )}
          </div>

          {/* 右側: アクションボタン */}
          {!contraction.is_ongoing && (
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
          )}
        </div>
      </div>

      {/* 編集モーダル */}
      <Dialog open={editModalOpen} onOpenChange={setEditModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>陣痛記録を編集</DialogTitle>
          </DialogHeader>
          <ContractionForm
            contraction={contraction}
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
            この陣痛記録を削除してもよろしいですか？
            <br />
            <span className="text-sm text-gray-500">
              {format(new Date(contraction.start_time), 'yyyy年M月d日(E) HH:mm', {
                locale: ja,
              })}
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
