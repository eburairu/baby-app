'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Cookies from 'js-cookie';
import useSWR from 'swr';
import { Loader2 } from 'lucide-react';

const fetcher = (url: string) => fetch(url).then((res) => {
    if (res.status === 401) throw new Error('Unauthorized');
    return res.json();
});

export default function LoginPage() {
    const router = useRouter();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    // Check if already logged in
    const { data: user, error: userError } = useSWR('/api/me', fetcher, {
        shouldRetryOnError: false,
    });

    useEffect(() => {
        if (user && !userError) {
            router.push('/dashboard');
        }
    }, [user, userError, router]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            // Ensure CSRF token is set (by fetching /api/me or any endpoint that sets it)
            // If /api/me fails (401), it might still set the cookie? 
            // Actually, middleware sets cookie on any response.
            // If user is not logged in, /api/me returns 401 but CSRF cookie should be there.

            let csrfToken = Cookies.get('csrf_token');
            if (!csrfToken) {
                // Fetch health to set cookie if missing
                await fetch('/api/health');
                csrfToken = Cookies.get('csrf_token');
            }

            const res = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': csrfToken || '',
                },
                body: JSON.stringify({ username, password }),
            });

            if (!res.ok) {
                if (res.status === 401) {
                    throw new Error('ユーザー名またはパスワードが正しくありません');
                }
                const data = await res.json();
                throw new Error(data.detail || 'Login failed');
            }

            // Login successful
            // Force re-fetch user state or just redirect
            // mutate('/api/me'); // context?
            router.push('/dashboard'); // creating dashboard page next
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8">
                <div>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        Baby App にログイン
                    </h2>
                    <p className="mt-2 text-center text-sm text-gray-600">
                        または{' '}
                        <Link href="/register" className="font-medium text-indigo-600 hover:text-indigo-500">
                            新しいアカウントを作成
                        </Link>
                    </p>
                </div>
                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    <div className="rounded-md shadow-sm -space-y-px">
                        <div>
                            <label htmlFor="username" className="sr-only">
                                ユーザー名
                            </label>
                            <input
                                id="username"
                                name="username"
                                type="text"
                                required
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                placeholder="ユーザー名"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                            />
                        </div>
                        <div>
                            <label htmlFor="password" className="sr-only">
                                パスワード
                            </label>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                required
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                                placeholder="パスワード"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>
                    </div>

                    {error && (
                        <div className="text-red-500 text-sm text-center">{error}</div>
                    )}

                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                        >
                            {loading ? <Loader2 className="animate-spin h-5 w-5" /> : 'ログイン'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
