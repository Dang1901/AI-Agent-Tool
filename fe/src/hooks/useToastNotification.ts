import { useToast } from '../contexts/ToastContext';

export const useToastNotification = () => {
  const { addToast } = useToast();

  const showSuccess = (title: string, message?: string) => {
    addToast({
      type: 'success',
      title,
      message,
      duration: 4000,
    });
  };

  const showError = (title: string, message?: string) => {
    addToast({
      type: 'error',
      title,
      message,
      duration: 6000,
    });
  };

  const showWarning = (title: string, message?: string) => {
    addToast({
      type: 'warning',
      title,
      message,
      duration: 5000,
    });
  };

  const showInfo = (title: string, message?: string) => {
    addToast({
      type: 'info',
      title,
      message,
      duration: 4000,
    });
  };

  // CUD Operations
  const showCreateSuccess = (resource: string) => {
    showSuccess(
      `${resource} Created`,
      `Successfully created ${resource.toLowerCase()}`
    );
  };

  const showCreateError = (resource: string, error?: string) => {
    showError(
      `Failed to Create ${resource}`,
      error || `Unable to create ${resource.toLowerCase()}`
    );
  };

  const showUpdateSuccess = (resource: string) => {
    showSuccess(
      `${resource} Updated`,
      `Successfully updated ${resource.toLowerCase()}`
    );
  };

  const showUpdateError = (resource: string, error?: string) => {
    showError(
      `Failed to Update ${resource}`,
      error || `Unable to update ${resource.toLowerCase()}`
    );
  };

  const showDeleteSuccess = (resource: string) => {
    showSuccess(
      `${resource} Deleted`,
      `Successfully deleted ${resource.toLowerCase()}`
    );
  };

  const showDeleteError = (resource: string, error?: string) => {
    showError(
      `Failed to Delete ${resource}`,
      error || `Unable to delete ${resource.toLowerCase()}`
    );
  };

  // API Operations
  const showApiSuccess = (operation: string) => {
    showSuccess(
      'Operation Successful',
      operation
    );
  };

  const showApiError = (operation: string, error?: string) => {
    showError(
      'Operation Failed',
      error || operation
    );
  };

  return {
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showCreateSuccess,
    showCreateError,
    showUpdateSuccess,
    showUpdateError,
    showDeleteSuccess,
    showDeleteError,
    showApiSuccess,
    showApiError,
  };
};
