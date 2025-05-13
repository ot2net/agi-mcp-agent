'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getWorkflow } from '@/api/workflow';
import { Workflow } from '@/types/workflow';
import WorkflowEditor from '@/components/workflow/WorkflowEditor';
import { Card } from '@/components/base/Card';

export default function EditWorkflowPage() {
  const router = useRouter();
  const params = useParams();
  const workflowId = params?.id as string;
  
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load workflow data
  useEffect(() => {
    const loadWorkflow = async () => {
      if (!workflowId) return;
      
      try {
        setLoading(true);
        const data = await getWorkflow(workflowId);
        if (data) {
          setWorkflow(data);
        } else {
          setError('Workflow not found');
        }
      } catch (error) {
        console.error('Failed to load workflow:', error);
        setError('Failed to load workflow');
      } finally {
        setLoading(false);
      }
    };

    loadWorkflow();
  }, [workflowId]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-4">
        <Card className="p-8 text-center">
          <h2 className="text-xl font-bold text-red-600 mb-4">{error}</h2>
          <p className="mb-4">Unable to load the workflow. Please return to the workflow list and try again.</p>
          <button
            onClick={() => router.push('/workflow')}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Return to Workflow List
          </button>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <Card className="mb-4 p-4">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Edit Workflow: {workflow?.name}
        </h1>
        <p className="text-gray-600 dark:text-gray-300 mt-2">
          Modify the workflow definition, adjust steps and connections
        </p>
      </Card>
      
      {workflow && <WorkflowEditor workflowId={workflowId} initialWorkflow={workflow} />}
    </div>
  );
} 