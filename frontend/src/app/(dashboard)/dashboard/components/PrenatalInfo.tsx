/**
 * PrenatalInfo
 *
 * プレママ期情報表示
 */

'use client';

import type { DashboardData } from '../hooks/useDashboard';

interface PrenatalInfoProps {
  data: DashboardData;
}

export function PrenatalInfo({ data }: PrenatalInfoProps) {
  const { prenatal_info } = data;

  if (!prenatal_info) {
    return null;
  }

  return (
    <div className="bg-gradient-to-r from-pink-500 to-purple-600 rounded-lg shadow p-6 text-white">
      <h3 className="text-lg font-semibold mb-4">🤰 プレママ期</h3>
      <div className="grid grid-cols-3 gap-4">
        <div className="text-center">
          <p className="text-3xl font-bold">{prenatal_info.weeks}</p>
          <p className="text-sm opacity-90">週</p>
        </div>
        <div className="text-center">
          <p className="text-3xl font-bold">{prenatal_info.days}</p>
          <p className="text-sm opacity-90">日</p>
        </div>
        <div className="text-center">
          <p className="text-3xl font-bold">{prenatal_info.days_remaining}</p>
          <p className="text-sm opacity-90">日後</p>
        </div>
      </div>
      <p className="text-center mt-4 text-sm opacity-90">
        出産予定日まであと{prenatal_info.days_remaining}日
      </p>
    </div>
  );
}
