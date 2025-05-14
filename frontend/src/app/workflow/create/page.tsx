'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import WorkflowEditor from '@/components/workflow/WorkflowEditor';

export default function CreateWorkflowPage() {
  const router = useRouter();

  return (
    <div className="container mx-auto p-0">
      <WorkflowEditor />
    </div>
  );
} 