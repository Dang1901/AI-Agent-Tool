// types.ts
// FeatureKey định nghĩa các quyền
export type FeatureKey =
  | 'user'
  | 'role'
  | 'project'
  | 'test_case'
  | 'test_schedule'
  | 'test_history'
  | 'api_doc'
  | 'dashboard'
  | 'report';

// Kiểu dữ liệu của mỗi hàng
export type FeatureRow = {
  feature: FeatureKey;
  name: string;
  read: boolean;
  write: boolean;
};

// Định nghĩa thứ tự
export const FEATURE_ORDER: FeatureKey[] = [
  'user',
  'role',
  'project',
  'test_case',
  'test_schedule',
  'test_history',
  'api_doc',
  'dashboard',
  'report',
];

// Gán nhãn hiển thị
export const FEATURE_LABELS: Record<FeatureKey, string> = {
  user: 'User',
  role: 'Role',
  project: 'Project',
  test_case: 'Test Case',
  test_schedule: 'Test Schedule',
  test_history: 'Test History',
  api_doc: 'API Doc',
  dashboard: 'Dashboard',
  report: 'Report',
};



export function buildRowsFromMap(
  perms: Partial<Record<FeatureKey, { read: boolean; write: boolean }>>
): FeatureRow[] {
  return FEATURE_ORDER.map((k) => ({
    feature: k,
    name: FEATURE_LABELS[k],
    read: perms[k]?.read ?? false,
    write: perms[k]?.write ?? false,
  }));
}
