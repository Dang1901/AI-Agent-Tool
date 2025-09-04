import { FEATURE_LABELS, FEATURE_ORDER, type FeatureKey, type FeatureRow } from './type';

export const defaultMockPermissions: Partial<
  Record<FeatureKey, { read: boolean; write: boolean }>
> = {
  user: { read: true, write: false },
  role: { read: true, write: false },
  project: { read: true, write: false },
  test_case: { read: true, write: true },
  test_schedule: { read: true, write: false },
  test_history: { read: true, write: false },
  api_doc: { read: true, write: false },
  dashboard: { read: true, write: true },
  report: { read: true, write: false },
};

export const mockApiGetPermissionByUserId = async (
  userId: string
): Promise<Partial<Record<FeatureKey, { read: boolean; write: boolean }>>> => {
  console.log(`Fetching permission for user ${userId}`);
  return new Promise((resolve) =>
    setTimeout(() => resolve(defaultMockPermissions), 500)
  );
};

export const mockApiUpdatePermissionByUserId = async (
  userId: string,
  newPerms: FeatureRow[]
): Promise<boolean> => {
  console.log(`Updating permission for user ${userId}`, newPerms);
  return new Promise((resolve) => setTimeout(() => resolve(true), 500));
};

// Optional: mock data (để dùng khi chưa có API)
export const featureData: FeatureRow[] = FEATURE_ORDER.map((key) => ({
  feature: key,
  name: FEATURE_LABELS[key], // không còn lỗi TypeScript
  read: false,
  write: false,
}));


