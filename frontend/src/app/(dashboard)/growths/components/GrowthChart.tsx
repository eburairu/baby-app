/**
 * GrowthChart
 *
 * 成長グラフ表示コンポーネント（Recharts使用）
 */

'use client';

import { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format } from 'date-fns';
import { ja } from 'date-fns/locale';
import type { Growth } from '../hooks/useGrowths';

interface GrowthChartProps {
  growths: Growth[];
}

export function GrowthChart({ growths }: GrowthChartProps) {
  const [selectedMetric, setSelectedMetric] = useState<'weight' | 'height' | 'head'>('weight');

  // データを日付順にソート
  const sortedGrowths = [...growths].sort(
    (a, b) => new Date(a.measurement_date).getTime() - new Date(b.measurement_date).getTime()
  );

  // グラフ用のデータを準備
  const chartData = sortedGrowths.map((growth) => ({
    date: format(new Date(growth.measurement_date), 'M/d', { locale: ja }),
    fullDate: growth.measurement_date,
    weight: growth.weight_kg,
    height: growth.height_cm,
    head: growth.head_circumference_cm,
  }));

  // メトリクスの設定
  const metrics = [
    { key: 'weight', label: '体重', unit: 'kg', color: '#10b981' },
    { key: 'height', label: '身長', unit: 'cm', color: '#3b82f6' },
    { key: 'head', label: '頭囲', unit: 'cm', color: '#f59e0b' },
  ];

  const currentMetric = metrics.find((m) => m.key === selectedMetric)!;

  if (sortedGrowths.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8">
        <p className="text-center text-gray-500 dark:text-gray-400">
          グラフを表示するデータがありません
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          成長グラフ
        </h3>

        {/* メトリクス選択 */}
        <div className="flex gap-2">
          {metrics.map((metric) => (
            <button
              key={metric.key}
              onClick={() => setSelectedMetric(metric.key as any)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                selectedMetric === metric.key
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
              }`}
            >
              {metric.label}
            </button>
          ))}
        </div>
      </div>

      {/* グラフ */}
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            stroke="#888888"
            tick={{ fill: '#888888' }}
          />
          <YAxis
            stroke="#888888"
            tick={{ fill: '#888888' }}
            label={{
              value: currentMetric.unit,
              angle: -90,
              position: 'insideLeft',
              style: { fill: '#888888' },
            }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #ddd',
              borderRadius: '8px',
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey={selectedMetric}
            name={`${currentMetric.label} (${currentMetric.unit})`}
            stroke={currentMetric.color}
            strokeWidth={2}
            dot={{ fill: currentMetric.color, r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
