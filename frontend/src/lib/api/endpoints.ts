/**
 * APIエンドポイント定義
 *
 * 全てのエンドポイントを一元管理
 */

/**
 * 認証エンドポイント
 */
export const AuthEndpoints = {
  me: '/api/me',
  login: '/api/login',
  logout: '/api/logout',
  register: '/api/register',
} as const;

/**
 * 家族エンドポイント
 */
export const FamilyEndpoints = {
  me: '/api/families/me',
  list: '/api/families',
  detail: (id: number) => `/api/families/${id}`,
} as const;

/**
 * 赤ちゃんエンドポイント
 */
export const BabyEndpoints = {
  list: (familyId?: number) =>
    familyId ? `/api/babies?family_id=${familyId}` : '/api/babies',
  detail: (id: number) => `/api/babies/${id}`,
  create: '/api/babies',
  born: (id: number) => `/api/babies/${id}/born`,
} as const;

/**
 * ダッシュボードエンドポイント
 */
export const DashboardEndpoints = {
  data: (babyId?: number) =>
    babyId ? `/api/dashboard/data?baby_id=${babyId}` : '/api/dashboard/data',
} as const;

/**
 * 授乳記録エンドポイント
 */
export const FeedingEndpoints = {
  list: (babyId?: number) =>
    babyId ? `/api/feedings?baby_id=${babyId}` : '/api/feedings',
  detail: (id: number) => `/api/feedings/${id}`,
  create: '/api/feedings',
  update: (id: number) => `/api/feedings/${id}`,
  delete: (id: number) => `/api/feedings/${id}`,
} as const;

/**
 * 睡眠記録エンドポイント
 */
export const SleepEndpoints = {
  list: (babyId?: number) =>
    babyId ? `/api/sleeps?baby_id=${babyId}` : '/api/sleeps',
  detail: (id: number) => `/api/sleeps/${id}`,
  create: '/api/sleeps',
  update: (id: number) => `/api/sleeps/${id}`,
  delete: (id: number) => `/api/sleeps/${id}`,
  start: '/api/sleeps/start',
  end: (id: number) => `/api/sleeps/${id}/end`,
} as const;

/**
 * おむつ交換エンドポイント
 */
export const DiaperEndpoints = {
  list: (babyId?: number) =>
    babyId ? `/api/diapers?baby_id=${babyId}` : '/api/diapers',
  detail: (id: number) => `/api/diapers/${id}`,
  create: '/api/diapers',
  update: (id: number) => `/api/diapers/${id}`,
  delete: (id: number) => `/api/diapers/${id}`,
  quick: '/api/diapers/quick',
} as const;

/**
 * 成長記録エンドポイント
 */
export const GrowthEndpoints = {
  list: (babyId?: number) =>
    babyId ? `/api/growths?baby_id=${babyId}` : '/api/growths',
  detail: (id: number) => `/api/growths/${id}`,
  create: '/api/growths',
  update: (id: number) => `/api/growths/${id}`,
  delete: (id: number) => `/api/growths/${id}`,
} as const;

/**
 * 陣痛タイマーエンドポイント
 */
export const ContractionEndpoints = {
  list: (babyId?: number) =>
    babyId ? `/api/contractions/list?baby_id=${babyId}` : '/api/contractions/list',
  detail: (id: number) => `/api/contractions/${id}`,
  create: '/api/contractions',
  update: (id: number) => `/api/contractions/${id}`,
  delete: (id: number) => `/api/contractions/${id}`,
  start: '/api/contractions/start',
  end: (id: number) => `/api/contractions/${id}/end`,
  stats: (babyId?: number) =>
    babyId ? `/api/contractions?baby_id=${babyId}` : '/api/contractions',
} as const;

/**
 * スケジュールエンドポイント
 */
export const ScheduleEndpoints = {
  list: (babyId?: number) =>
    babyId ? `/api/schedules?baby_id=${babyId}` : '/api/schedules',
  detail: (id: number) => `/api/schedules/${id}`,
  create: '/api/schedules',
  update: (id: number) => `/api/schedules/${id}`,
  delete: (id: number) => `/api/schedules/${id}`,
  toggle: (id: number) => `/api/schedules/${id}/toggle`,
} as const;
