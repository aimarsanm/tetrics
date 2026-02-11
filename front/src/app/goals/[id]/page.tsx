'use client';

import { Dashboard } from '@/components/dashboard/dashboard';
import { useParams } from 'next/navigation';

export default function GoalDetailPage() {
  const params = useParams();
  const goalId = typeof params?.id === 'string' ? params.id : undefined;
  return <Dashboard goalId={goalId} />;
}
