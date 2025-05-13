'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import WorkflowEditor from '@/components/workflow/WorkflowEditor';
import { Card } from '@/components/base/Card';

export default function CreateWorkflowPage() {
  const router = useRouter();

  return (
    <div className="container mx-auto p-4">
      <Card className="mb-4 p-4">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Create Workflow</h1>
        <p className="text-gray-600 dark:text-gray-300 mt-2">
          Use the visual editor to create a new workflow connecting environments, agents, and tasks
        </p>
      </Card>
      
      <WorkflowEditor />
    </div>
  );
} 