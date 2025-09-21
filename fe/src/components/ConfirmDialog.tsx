import React from 'react';
import {
  Dialog,
  Button,
  Flex,
  Text,
  Box
} from '@radix-ui/themes';
import { ExclamationTriangleIcon } from '@radix-ui/react-icons';
import './ConfirmDialog.css';

interface ConfirmDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'info';
  onConfirm: () => void;
  onCancel?: () => void;
  loading?: boolean;
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  open,
  onOpenChange,
  title,
  description,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'danger',
  onConfirm,
  onCancel,
  loading = false
}) => {
  const handleConfirm = () => {
    onConfirm();
    onOpenChange(false);
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    }
    onOpenChange(false);
  };

  const getVariantStyles = () => {
    switch (variant) {
      case 'danger':
        return {
          iconColor: '#F44336',
          confirmButtonVariant: 'solid' as const,
          confirmButtonColor: 'red' as const,
          borderColor: '#F44336'
        };
      case 'warning':
        return {
          iconColor: '#FF9800',
          confirmButtonVariant: 'solid' as const,
          confirmButtonColor: 'orange' as const,
          borderColor: '#FF9800'
        };
      case 'info':
        return {
          iconColor: '#2196F3',
          confirmButtonVariant: 'solid' as const,
          confirmButtonColor: 'blue' as const,
          borderColor: '#2196F3'
        };
      default:
        return {
          iconColor: '#F44336',
          confirmButtonVariant: 'solid' as const,
          confirmButtonColor: 'red' as const,
          borderColor: '#F44336'
        };
    }
  };

  const styles = getVariantStyles();

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Content className="confirm-dialog-content">
        <div className="confirm-dialog-title">
          <Flex align="center" gap="3">
            <Box
              className="confirm-dialog-icon"
              style={{ color: styles.iconColor }}
            >
              <ExclamationTriangleIcon width="24" height="24" />
            </Box>
            <Text size="4" weight="bold">
              {title}
            </Text>
          </Flex>
        </div>

        <div className="confirm-dialog-description">
          <Text size="3" color="gray">
            {description}
          </Text>
        </div>

        <Flex gap="3" justify="end" className="confirm-dialog-actions">
          <Dialog.Close>
            <Button
              variant="soft"
              color="gray"
              onClick={handleCancel}
              disabled={loading}
            >
              {cancelText}
            </Button>
          </Dialog.Close>
          <Button
            variant={styles.confirmButtonVariant}
            color={styles.confirmButtonColor}
            onClick={handleConfirm}
            disabled={loading}
          >
            {loading ? 'Processing...' : confirmText}
          </Button>
        </Flex>
      </Dialog.Content>
    </Dialog.Root>
  );
};

// Specialized components for common use cases
export const DeleteConfirmDialog: React.FC<Omit<ConfirmDialogProps, 'variant' | 'confirmText'>> = (props) => (
  <ConfirmDialog
    {...props}
    variant="danger"
    confirmText="Delete"
  />
);

export const WarningConfirmDialog: React.FC<Omit<ConfirmDialogProps, 'variant' | 'confirmText'>> = (props) => (
  <ConfirmDialog
    {...props}
    variant="warning"
    confirmText="Proceed"
  />
);

export const InfoConfirmDialog: React.FC<Omit<ConfirmDialogProps, 'variant' | 'confirmText'>> = (props) => (
  <ConfirmDialog
    {...props}
    variant="info"
    confirmText="Continue"
  />
);
