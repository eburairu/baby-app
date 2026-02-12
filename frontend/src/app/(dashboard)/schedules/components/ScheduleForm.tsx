/**
 * ScheduleForm
 *
 * スケジュールフォーム（新規作成・編集）
 */

'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import type { Schedule } from '../hooks/useSchedules';

/**
 * バリデーションスキーマ
 */
const scheduleSchema = z.object({
  title: z.string().min(1, 'タイトルを入力してください').max(200, 'タイトルは200文字以内で入力してください'),
  description: z.string().optional().nullable(),
  scheduled_time: z.string().min(1, '予定日時を入力してください'),
});

type ScheduleFormData = z.infer<typeof scheduleSchema>;

interface ScheduleFormProps {
  schedule?: Schedule | null;
  onSubmit: (data: ScheduleFormData) => Promise<void>;
  onCancel: () => void;
}

export function ScheduleForm({ schedule, onSubmit, onCancel }: ScheduleFormProps) {
  const isEdit = Boolean(schedule);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ScheduleFormData>({
    resolver: zodResolver(scheduleSchema),
    defaultValues: schedule
      ? {
          title: schedule.title,
          description: schedule.description || '',
          scheduled_time: schedule.scheduled_time,
        }
      : {
          title: '',
          description: '',
          scheduled_time: new Date().toISOString().slice(0, 16),
        },
  });

  const handleFormSubmit = async (data: ScheduleFormData) => {
    await onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      {/* タイトル */}
      <Input
        label="タイトル"
        type="text"
        {...register('title')}
        error={errors.title?.message}
        placeholder="例: 予防接種、健診、通院など"
      />

      {/* 予定日時 */}
      <Input
        label="予定日時"
        type="datetime-local"
        {...register('scheduled_time')}
        error={errors.scheduled_time?.message}
      />

      {/* 説明 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          説明
        </label>
        <textarea
          {...register('description')}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
          placeholder="詳細や持ち物など"
        />
        {errors.description && (
          <p className="text-red-500 text-sm mt-1">{errors.description.message}</p>
        )}
      </div>

      {/* ボタン */}
      <div className="flex gap-3 pt-4">
        <Button type="button" variant="secondary" onClick={onCancel}>
          キャンセル
        </Button>
        <Button type="submit" variant="primary" isLoading={isSubmitting}>
          {isEdit ? '更新' : '作成'}
        </Button>
      </div>
    </form>
  );
}
