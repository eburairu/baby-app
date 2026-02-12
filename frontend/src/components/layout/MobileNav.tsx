/**
 * MobileNav
 *
 * モバイルボトムナビゲーション
 */

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Baby, Moon, Scale, Calendar } from 'lucide-react';
import { clsx } from 'clsx';

export function MobileNav() {
  const pathname = usePathname();

  const navItems = [
    { href: '/dashboard', label: 'ホーム', icon: Home },
    { href: '/feedings', label: '授乳', icon: Baby },
    { href: '/sleeps', label: '睡眠', icon: Moon },
    { href: '/growths', label: '成長', icon: Scale },
    { href: '/schedules', label: '予定', icon: Calendar },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-white dark:bg-gray-900 border-t dark:border-gray-800">
      <div className="grid grid-cols-5 h-16">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                'flex flex-col items-center justify-center space-y-1 transition-colors',
                isActive
                  ? 'text-indigo-600 dark:text-indigo-400'
                  : 'text-gray-600 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400'
              )}
            >
              <Icon className="h-5 w-5" />
              <span className="text-xs">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
