import { type ReactNode } from 'react';
import { useAuthStore } from '../store/authStore';
import { PermissionDenied } from '../components/StateComponents';

interface RoleGuardProps {
  permission: string;
  children: ReactNode;
}

export function RoleGuard({ permission, children }: RoleGuardProps) {
  const { hasPermission } = useAuthStore();
  if (!hasPermission(permission)) {
    return <PermissionDenied />;
  }
  return <>{children}</>;
}
