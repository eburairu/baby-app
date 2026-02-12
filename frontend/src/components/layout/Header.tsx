/**
 * Header
 *
 * PCナビゲーション
 */

'use client';

import Link from 'next/link';
import { useAuth } from '@/lib/hooks/useAuth';
import { BabySelector } from './BabySelector';
import { ThemeToggle } from './ThemeToggle';
import { Button } from '@/components/ui/Button';
import { toast } from '@/components/ui/Toast';

export function Header() {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
      toast.success('ログアウトしました');
    } catch (err) {
      toast.error('ログアウトに失敗しました');
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white dark:bg-gray-900 dark:border-gray-800">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        {/* ロゴ */}
        <Link href="/dashboard" className="flex items-center space-x-2">
          <h1 className="text-xl font-bold text-indigo-600 dark:text-indigo-400">
            Baby App
          </h1>
        </Link>

        {/* ナビゲーション */}
        <nav className="hidden md:flex items-center space-x-6">
          <Link
            href="/dashboard"
            className="text-sm font-medium text-gray-700 hover:text-indigo-600 dark:text-gray-300 dark:hover:text-indigo-400 transition-colors"
          >
            ダッシュボード
          </Link>
          <Link
            href="/feedings"
            className="text-sm font-medium text-gray-700 hover:text-indigo-600 dark:text-gray-300 dark:hover:text-indigo-400 transition-colors"
          >
            授乳
          </Link>
          <Link
            href="/sleeps"
            className="text-sm font-medium text-gray-700 hover:text-indigo-600 dark:text-gray-300 dark:hover:text-indigo-400 transition-colors"
          >
            睡眠
          </Link>
          <Link
            href="/diapers"
            className="text-sm font-medium text-gray-700 hover:text-indigo-600 dark:text-gray-300 dark:hover:text-indigo-400 transition-colors"
          >
            おむつ
          </Link>
          <Link
            href="/growths"
            className="text-sm font-medium text-gray-700 hover:text-indigo-600 dark:text-gray-300 dark:hover:text-indigo-400 transition-colors"
          >
            成長
          </Link>
        </nav>

        {/* 右側のコントロール */}
        <div className="flex items-center space-x-4">
          <BabySelector />
          <ThemeToggle />
          {user && (
            <>
              <span className="hidden md:block text-sm text-gray-700 dark:text-gray-300">
                {user.username}
              </span>
              <Button variant="secondary" size="sm" onClick={handleLogout}>
                ログアウト
              </Button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
