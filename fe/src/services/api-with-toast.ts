import { envVarApi, releaseApi, auditApi, authApi } from './api';

// Wrapper functions that include toast notifications
export const createEnvVarWithToast = async (data: Parameters<typeof envVarApi.createEnvVar>[0]) => {
  try {
    const result = await envVarApi.createEnvVar(data);
    // Toast will be handled by the component using this function
    return result;
  } catch (error: any) {
    throw error;
  }
};

export const updateEnvVarWithToast = async (id: string, data: Parameters<typeof envVarApi.updateEnvVar>[1]) => {
  try {
    const result = await envVarApi.updateEnvVar(id, data);
    return result;
  } catch (error: any) {
    throw error;
  }
};

export const deleteEnvVarWithToast = async (id: string, deleted_by: string) => {
  try {
    const result = await envVarApi.deleteEnvVar(id, deleted_by);
    return result;
  } catch (error: any) {
    throw error;
  }
};

export const createReleaseWithToast = async (data: Parameters<typeof releaseApi.createRelease>[0]) => {
  try {
    const result = await releaseApi.createRelease(data);
    return result;
  } catch (error: any) {
    throw error;
  }
};

export const approveReleaseWithToast = async (id: string, approver_id: string, comment?: string) => {
  try {
    const result = await releaseApi.approveRelease(id, approver_id, comment);
    return result;
  } catch (error: any) {
    throw error;
  }
};

export const applyReleaseWithToast = async (id: string, applied_by: string) => {
  try {
    const result = await releaseApi.applyRelease(id, applied_by);
    return result;
  } catch (error: any) {
    throw error;
  }
};

// Export all APIs for backward compatibility
export { envVarApi, releaseApi, auditApi, authApi };
