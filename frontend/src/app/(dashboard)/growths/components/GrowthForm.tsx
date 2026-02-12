/**
 * GrowthForm
 *
 * 成長記録フォーム（新規作成・編集）
 */

'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import type { Growth } from '../hooks/useGrowths';

/**
 * バリデーションスキーマ
 */
const growthSchema = z.object({
  measurement_date: z.string().min(1, '測定日を入力してください'),
  weight_kg: z.number().min(0, '体重は0以上である必要があります').optional().nullable(),
  height_cm: z.number().min(0, '身長は0以上である必要があります').optional().nullable(),
  head_circumference_cm: z.number().min(0, '頭囲は0以上である必要があります').optional().nullable(),
  notes: z.string().optional().nullable(),
});

type GrowthFormData = z.infer<typeof growthSchema>;

interface GrowthFormProps {
  growth?: Growth | null;
  onSubmit: (data: GrowthFormData) => Promise<void>;
  onCancel: () => void;
}

export function GrowthForm({ growth, onSubmit, onCancel }: GrowthFormProps) {
  const isEdit = Boolean(growth);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<GrowthFormData>({
    resolver: zodResolver(growthSchema),
    defaultValues: growth
      ? {
          measurement_date: growth.measurement_date,
          weight_kg: growth.weight_kg,
          height_cm: growth.height_cm,
          head_circumference_cm: growth.head_circumference_cm,
          notes: growth.notes,
        }
      : {
          measurement_date: new Date().toISOString().slice(0, 10),
          weight_kg: null,
          height_cm: null,
          head_circumference_cm: null,
          notes: '',
        },
  });

  const handleFormSubmit = async (data: GrowthFormData) => {
    await onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      {/* 測定日 */}
      <Input
        label="測定日"
        type="date"
        {...register('measurement_date')}
        error={errors.measurement_date?.message}
      />

      {/* 体重 */}
      <Input
        label="体重 (kg)"
        type="number"
        step="0.01"
        {...register('weight_kg', { valueAsNumber: true })}
        error={errors.weight_kg?.message}
      />

      {/* 身長 */}
      <Input
        label="身長 (cm)"
        type="number"
        step="0.1"
        {...register('height_cm', { valueAsNumber: true })}
        error={errors.height_cm?.message}
      />

      {/* 頭囲 */}
      <Input
        label="頭囲 (cm)"
        type="number"
        step="0.1"
        {...register('head_circumference_cm', { valueAsNumber: true })}
        error={errors.head_circumference_cm?.message}
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
