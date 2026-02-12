/**
 * ScheduleItem
 *
 * 個別のスケジュール表示コンポーネント（完了トグル機能付き）
 */

'use client';

import { useState } from 'react';
import { format, isPast } from 'date-fns';
import { ja } from 'date-fns/locale';
import { Pencil, Trash2, Calendar, CheckCircle2, Circle } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/Dialog';
import type { Schedule } from '../hooks/useSchedules';
import { ScheduleForm } from './ScheduleForm';

interface ScheduleItemProps {
  schedule: Schedule;
  onUpdate: (id: number, data: any) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
  onToggle: (id: number) => Promise<void>;
}

export function ScheduleItem({ schedule, onUpdate, onDelete, onToggle }: ScheduleItemProps) {
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isToggling, setIsToggling] = useState(false);

  const scheduledDate = new Date(schedule.scheduled_time);
  const isOverdue = isPast(scheduledDate) && !schedule.is_completed;

  const handleUpdate = async (data: any) => {
    await onUpdate(schedule.id, data);
    setEditModalOpen(false);
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await onDelete(schedule.id);
      setDeleteModalOpen(false);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleToggle = async () => {
    setIsToggling(true);
    try {
      await onToggle(schedule.id);
    } finally {
      setIsToggling(false);
    }
  };

  return (
    <>
      <div
        className={`rounded-lg shadow p-4 hover:shadow-md transition-shadow ${
          schedule.is_completed
            ? 'bg-gray-50 dark:bg-gray-800 opacity-75'
            : isOverdue
            ? 'bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500'
            : 'bg-white dark:bg-gray-800'
        }`}
      >
        <div className="flex items-start gap-3">
          {/* 完了トグルボタン */}
          <button
            onClick={handleToggle}
            disabled={isToggling}
            className="flex-shrink-0 mt-1 focus:outline-none"
          >
            {schedule.is_completed ? (
              <CheckCircle2 className="h-6 w-6 text-green-600 dark:text-green-400" />
            ) : (
              <Circle className="h-6 w-6 text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400" />
            )}
          </button>

          {/* スケジュール情報 */}
          <div className="flex-1">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3
                  className={`text-lg font-semibold ${
                    schedule.is_completed
                      ? 'line-through text-gray-500 dark:text-gray-400'
                      : 'text-gray-900 dark:text-white'
                  }`}
                >
                  {schedule.title}
                </h3>

                <div className="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400 mt-1">
                  <Calendar className="h-4 w-4" />
                  <span>
                    {format(scheduledDate, 'yyyy年M月d日(E) HH:mm', {
                      locale: ja,
                    })}
                  </span>
                  {isOverdue && (
                    <span className="ml-2 px-2 py-0.5 bg-red-600 text-white text-xs font-bold rounded">
                      期限切れ
                    </span>
                  )}
                </div>

                {schedule.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                    {schedule.description}
                  </p>
                )}
              </div>

              {/* アクションボタン */}
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
        </div>
      </div>

      {/* 編集モーダル */}
      <Dialog open={editModalOpen} onOpenChange={setEditModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>スケジュールを編集</DialogTitle>
          </DialogHeader>
          <ScheduleForm
            schedule={schedule}
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
            このスケジュールを削除してもよろしいですか？
            <br />
            <span className="text-sm text-gray-500">{schedule.title}</span>
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
