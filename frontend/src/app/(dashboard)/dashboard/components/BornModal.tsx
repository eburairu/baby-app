/**
 * BornModal
 *
 * 出生記録モーダル
 */

'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/Dialog';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { toast } from '@/components/ui/Toast';
import { apiPost } from '@/lib/api/client';
import { BabyEndpoints } from '@/lib/api/endpoints';

/**
 * バリデーションスキーマ
 */
const bornSchema = z.object({
  birthday: z.string().min(1, '誕生日を入力してください'),
});

type BornFormData = z.infer<typeof bornSchema>;

interface BornModalProps {
  babyId: number;
  babyName: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function BornModal({
  babyId,
  babyName,
  open,
  onOpenChange,
  onSuccess,
}: BornModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<BornFormData>({
    resolver: zodResolver(bornSchema),
  });

  const onSubmit = async (data: BornFormData) => {
    setIsSubmitting(true);

    try {
      await apiPost(BabyEndpoints.born(babyId), {
        birthday: data.birthday,
      });

      toast.success('出生記録を登録しました', `${babyName}の誕生日を記録しました`);
      reset();
      onOpenChange(false);
      onSuccess();
    } catch (error: any) {
      toast.error('登録に失敗しました', error.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>🎉 {babyName}の誕生日を記録</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="誕生日"
            type="date"
            {...register('birthday')}
            error={errors.birthday?.message}
          />

          <DialogFooter>
            <Button
              type="button"
              variant="secondary"
              onClick={() => onOpenChange(false)}
              disabled={isSubmitting}
            >
              キャンセル
            </Button>
            <Button type="submit" variant="primary" isLoading={isSubmitting}>
              登録
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
