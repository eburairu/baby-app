/**
 * DiaperForm
 *
 * おむつ交換記録フォーム（詳細入力）
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

/**
 * バリデーションスキーマ
 */
const diaperSchema = z.object({
  change_time: z.string().min(1, '交換日時を入力してください'),
  diaper_type: z.enum(['wet', 'dirty', 'both']),
  notes: z.string().optional().nullable(),
});

type DiaperFormData = z.infer<typeof diaperSchema>;

interface DiaperFormProps {
  onSubmit: (data: DiaperFormData) => Promise<void>;
  onCancel: () => void;
}

/**
 * おむつタイプの選択肢
 */
const diaperTypeOptions = [
  { value: 'wet', label: '💧 おしっこ' },
  { value: 'dirty', label: '💩 うんち' },
  { value: 'both', label: '💧💩 両方' },
];

export function DiaperForm({ onSubmit, onCancel }: DiaperFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setValue,
    watch,
  } = useForm<DiaperFormData>({
    resolver: zodResolver(diaperSchema),
    defaultValues: {
      change_time: new Date().toISOString().slice(0, 16),
      diaper_type: 'wet',
      notes: '',
    },
  });

  const diaperType = watch('diaper_type');

  const handleFormSubmit = async (data: DiaperFormData) => {
    await onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      {/* 交換日時 */}
      <Input
        label="交換日時"
        type="datetime-local"
        {...register('change_time')}
        error={errors.change_time?.message}
      />

      {/* おむつタイプ */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          おむつタイプ
        </label>
        <Select
          value={diaperType}
          onValueChange={(value) =>
            setValue('diaper_type', value as 'wet' | 'dirty' | 'both')
          }
        >
          <SelectTrigger className="w-full">
            <SelectValue>
              {diaperTypeOptions.find((opt) => opt.value === diaperType)?.label}
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            {diaperTypeOptions.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.diaper_type && (
          <p className="text-red-500 text-sm mt-1">{errors.diaper_type.message}</p>
        )}
      </div>

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
          作成
        </Button>
      </div>
    </form>
  );
}
