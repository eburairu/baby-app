/**
 * GrowthItem
 *
 * 個別の成長記録表示コンポーネント
 */

'use client';

import { useState } from 'react';
import { format } from 'date-fns';
import { ja } from 'date-fns/locale';
import { Pencil, Trash2, Scale, Ruler } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/Dialog';
import type { Growth } from '../hooks/useGrowths';
import { GrowthForm } from './GrowthForm';

interface GrowthItemProps {
  growth: Growth;
  onUpdate: (id: number, data: any) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}

export function GrowthItem({ growth, onUpdate, onDelete }: GrowthItemProps) {
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleUpdate = async (data: any) => {
    await onUpdate(growth.id, data);
    setEditModalOpen(false);
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await onDelete(growth.id);
      setDeleteModalOpen(false);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <>
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 hover:shadow-md transition-shadow">
        <div className="flex items-start justify-between">
          {/* 左側: 成長情報 */}
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-sm font-semibold text-gray-900 dark:text-white">
                {format(new Date(growth.measurement_date), 'yyyy年M月d日(E)', {
                  locale: ja,
                })}
              </span>
            </div>

            {/* 測定値 */}
            <div className="grid grid-cols-3 gap-4">
              {growth.weight_kg !== null && (
                <div>
                  <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 mb-1">
                    <Scale className="h-3 w-3" />
                    <span>体重</span>
                  </div>
                  <div className="text-lg font-bold text-green-600 dark:text-green-400">
                    {growth.weight_kg}kg
                  </div>
                </div>
              )}

              {growth.height_cm !== null && (
                <div>
                  <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 mb-1">
                    <Ruler className="h-3 w-3" />
                    <span>身長</span>
                  </div>
                  <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
                    {growth.height_cm}cm
                  </div>
                </div>
              )}

              {growth.head_circumference_cm !== null && (
                <div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                    頭囲
                  </div>
                  <div className="text-lg font-bold text-orange-600 dark:text-orange-400">
                    {growth.head_circumference_cm}cm
                  </div>
                </div>
              )}
            </div>

            {/* メモ */}
            {growth.notes && (
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-3">
                {growth.notes}
              </p>
            )}
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
            <DialogTitle>成長記録を編集</DialogTitle>
          </DialogHeader>
          <GrowthForm
            growth={growth}
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
            この成長記録を削除してもよろしいですか？
            <br />
            <span className="text-sm text-gray-500">
              {format(new Date(growth.measurement_date), 'yyyy年M月d日(E)', {
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
