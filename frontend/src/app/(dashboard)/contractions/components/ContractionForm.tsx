/**
 * ContractionForm
 *
 * 陣痛記録フォーム（新規作成・編集）
 */

'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import type { Contraction } from '../hooks/useContractions';

/**
 * バリデーションスキーマ
 */
const contractionSchema = z.object({
  start_time: z.string().min(1, '開始日時を入力してください'),
  end_time: z.string().optional().nullable(),
  notes: z.string().optional().nullable(),
});

type ContractionFormData = z.infer<typeof contractionSchema>;

interface ContractionFormProps {
  contraction?: Contraction | null;
  onSubmit: (data: ContractionFormData) => Promise<void>;
  onCancel: () => void;
}

export function ContractionForm({ contraction, onSubmit, onCancel }: ContractionFormProps) {
  const isEdit = Boolean(contraction);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ContractionFormData>({
    resolver: zodResolver(contractionSchema),
    defaultValues: contraction
      ? {
          start_time: contraction.start_time,
          end_time: contraction.end_time || '',
          notes: contraction.notes || '',
        }
      : {
          start_time: new Date().toISOString().slice(0, 16),
          end_time: '',
          notes: '',
        },
  });

  const handleFormSubmit = async (data: ContractionFormData) => {
    await onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      {/* 開始日時 */}
      <Input
        label="開始日時"
        type="datetime-local"
        {...register('start_time')}
        error={errors.start_time?.message}
      />

      {/* 終了日時 */}
      <Input
        label="終了日時（任意）"
        type="datetime-local"
        {...register('end_time')}
        error={errors.end_time?.message}
      />

      {/* メモ */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          メモ
        </label>
        <textarea
          {...register('notes')}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
          placeholder="痛みの強さ、その他気になることなど"
        />
        {errors.notes && (
          <p className="text-red-500 text-sm mt-1">{errors.notes.message}</p>
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
