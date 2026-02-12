'use client';

import { useRouter } from 'next/navigation';
import useSWR from 'swr';
import { Loader2 } from 'lucide-react';

const fetcher = (url: string) => fetch(url).then((res) => {
    if (res.status === 401) throw new Error('Unauthorized');
    return res.json();
});

export default function DashboardPage() {
    const router = useRouter();
    const { data: user, error, mutate } = useSWR('/api/me', fetcher);

    if (error) {
        router.push('/login');
        return null;
    }

    if (!user) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <Loader2 className="animate-spin h-8 w-8 text-indigo-600" />
            </div>
        );
    }

    const handleLogout = async () => {
        await fetch('/api/logout');
        mutate(null); // Clear user data
        router.push('/login');
    };

    return (
        <div className="min-h-screen bg-gray-100">
            <nav className="bg-white shadow">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        <div className="flex">
                            <div className="flex-shrink-0 flex items-center">
                                <h1 className="text-xl font-bold text-indigo-600">Baby App</h1>
                            </div>
                        </div>
                        <div className="flex items-center">
                            <span className="text-gray-700 mr-4">
                                こんにちは, {user.username} さん
                            </span>
                            <button
                                onClick={handleLogout}
                                className="bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 px-4 py-2 rounded-md text-sm font-medium"
                            >
                                ログアウト
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <div className="px-4 py-6 sm:px-0">
                    <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 flex items-center justify-center">
                        <p className="text-gray-500 text-xl">
                            ダッシュボードコンテンツ (未実装)
                        </p>
                    </div>
                </div>
            </main>
        </div>
    );
}
