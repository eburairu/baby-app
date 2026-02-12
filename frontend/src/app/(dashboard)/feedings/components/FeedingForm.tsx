/**
 * FeedingForm
 *
 * 授乳記録フォーム（新規作成・編集）
 */

'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/Select';
import type { Feeding } from '../hooks/useFeedings';

/**
 * バリデーションスキーマ
 */
const feedingSchema = z.object({
  feeding_time: z.string().min(1, '授乳日時を入力してください'),
  feeding_type: z.enum(['breast', 'bottle', 'both']),
  amount_ml: z.number().min(0, '量は0以上である必要があります').optional().nullable(),
  duration_minutes: z.number().min(0, '時間は0以上である必要があります').optional().nullable(),
  notes: z.string().optional().nullable(),
});

type FeedingFormData = z.infer<typeof feedingSchema>;

interface FeedingFormProps {
  feeding?: Feeding | null;
  onSubmit: (data: FeedingFormData) => Promise<void>;
  onCancel: () => void;
}

/**
 * 授乳タイプの選択肢
 */
const feedingTypeOptions = [
  { value: 'breast', label: '母乳' },
  { value: 'bottle', label: 'ミルク' },
  { value: 'both', label: '混合' },
];

export function FeedingForm({ feeding, onSubmit, onCancel }: FeedingFormProps) {
  const isEdit = Boolean(feeding);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setValue,
    watch,
  } = useForm<FeedingFormData>({
    resolver: zodResolver(feedingSchema),
    defaultValues: feeding
      ? {
          feeding_time: new Date(feeding.feeding_time)
            .toISOString()
            .slice(0, 16),
          feeding_type: feeding.feeding_type,
          amount_ml: feeding.amount_ml,
          duration_minutes: feeding.duration_minutes,
          notes: feeding.notes,
        }
      : {
          feeding_time: new Date().toISOString().slice(0, 16),
          feeding_type: 'breast',
        },
  });

  const feedingType = watch('feeding_type');

  const handleFormSubmit = async (data: FeedingFormData) => {
    await onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      {/* 授乳日時 */}
      <Input
        label="授乳日時"
        type="datetime-local"
        {...register('feeding_time')}
        error={errors.feeding_time?.message}
      />

      {/* 授乳タイプ */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          授乳タイプ
        </label>
        <Select
          value={feedingType}
          onValueChange={(value) =>
            setValue('feeding_type', value as 'breast' | 'bottle' | 'both')
          }
        >
          <SelectTrigger className="w-full">
            <SelectValue>
              {feedingTypeOptions.find((opt) => opt.value === feedingType)?.label}
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            {feedingTypeOptions.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.feeding_type && (
          <p className="text-red-500 text-sm mt-1">{errors.feeding_type.message}</p>
        )}
      </div>

      {/* 量（ミルクまたは混合の場合のみ） */}
      {(feedingType === 'bottle' || feedingType === 'both') && (
        <Input
          label="量 (ml)"
          type="number"
          step="0.1"
          {...register('amount_ml', { valueAsNumber: true })}
          error={errors.amount_ml?.message}
        />
      )}

      {/* 授乳時間（母乳または混合の場合のみ） */}
      {(feedingType === 'breast' || feedingType === 'both') && (
        <Input
          label="授乳時間 (分)"
          type="number"
          {...register('duration_minutes', { valueAsNumber: true })}
          error={errors.duration_minutes?.message}
        />
      )}

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
