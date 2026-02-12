/**
 * QuickActions
 *
 * クイックアクションボタン
 */

'use client';

import Link from 'next/link';
import { Baby, Moon, Droplet, Scale, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import type { DashboardData } from '../hooks/useDashboard';

interface QuickActionsProps {
  data: DashboardData;
}

export function QuickActions({ data }: QuickActionsProps) {
  const { perms } = data;

  const actions = [
    {
      href: '/feedings',
      icon: Baby,
      label: '授乳記録',
      color: 'bg-indigo-600 hover:bg-indigo-700',
      enabled: perms.feeding,
    },
    {
      href: '/sleeps',
      icon: Moon,
      label: '睡眠記録',
      color: 'bg-purple-600 hover:bg-purple-700',
      enabled: perms.sleep,
    },
    {
      href: '/diapers',
      icon: Droplet,
      label: 'おむつ記録',
      color: 'bg-blue-600 hover:bg-blue-700',
      enabled: perms.diaper,
    },
    {
      href: '/growths',
      icon: Scale,
      label: '成長記録',
      color: 'bg-green-600 hover:bg-green-700',
      enabled: perms.growth,
    },
    {
      href: '/schedules',
      icon: Calendar,
      label: 'スケジュール',
      color: 'bg-orange-600 hover:bg-orange-700',
      enabled: perms.schedule,
    },
  ];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        クイックアクション
      </h3>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
        {actions
          .filter((action) => action.enabled)
          .map((action) => {
            const Icon = action.icon;
            return (
              <Link key={action.href} href={action.href}>
                <Button
                  variant="primary"
                  className={`w-full ${action.color} flex flex-col items-center gap-2 py-4`}
                >
                  <Icon className="h-6 w-6" />
                  <span className="text-sm">{action.label}</span>
                </Button>
              </Link>
            );
          })}
      </div>
    </div>
  );
}
