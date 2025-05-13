'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { HiOutlinePlus, HiOutlinePencil, HiOutlineTrash, HiOutlinePlay } from 'react-icons/hi';
import { getWorkflows, deleteWorkflow, executeWorkflow } from '@/api/workflow';
import { Workflow } from '@/types/workflow';
import { Button } from '@/components/base/Button';
import { Card } from '@/components/base/Card';

export default function WorkflowListPage() {
  const router = useRouter();
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [executingWorkflow, setExecutingWorkflow] = useState<string | null>(null);

  // Load workflow list
  useEffect(() => {
    const loadWorkflows = async () => {
      try {
        setLoading(true);
        const data = await getWorkflows();
        setWorkflows(data);
      } catch (error) {
        console.error('Failed to load workflows:', error);
      } finally {
        setLoading(false);
      }
    };

    loadWorkflows();
  }, []);

  // Delete workflow
  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this workflow?')) {
      return;
    }

    try {
      await deleteWorkflow(id);
      setWorkflows(workflows.filter(wf => wf.id !== id));
    } catch (error) {
      console.error('Failed to delete workflow:', error);
      alert('Failed to delete, please try again');
    }
  };

  // Execute workflow
  const handleExecute = async (id: string) => {
    try {
      setExecutingWorkflow(id);
      const result = await executeWorkflow(id);
      
      if (result.success) {
        alert(`Workflow executed successfully, Execution ID: ${result.data.execution_id}`);
      } else {
        alert(`Workflow execution failed: ${result.error}`);
      }
    } catch (error) {
      console.error('Failed to execute workflow:', error);
      alert('Execution failed, please try again');
    } finally {
      setExecutingWorkflow(null);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Workflow Management</h1>
        <Button 
          onClick={() => router.push('/workflow/create')}
          className="flex items-center"
        >
          <HiOutlinePlus className="mr-2" />
          Create Workflow
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : workflows.length === 0 ? (
        <Card className="text-center py-16">
          <h3 className="text-xl font-medium text-gray-500 dark:text-gray-400 mb-4">
            No Workflows
          </h3>
          <p className="text-gray-500 dark:text-gray-400 mb-6">
            Click the "Create Workflow" button to create your first workflow
          </p>
          <Button 
            onClick={() => router.push('/workflow/create')}
            className="inline-flex items-center"
          >
            <HiOutlinePlus className="mr-2" />
            Create Workflow
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {workflows.map((workflow) => (
            <Card key={workflow.id} className="flex flex-col h-full">
              <div className="flex-1 p-6">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  {workflow.name}
                </h3>
                <p className="text-gray-600 dark:text-gray-300 text-sm mb-4 line-clamp-3">
                  {workflow.description || 'No description'}
                </p>
                <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                  <span>
                    Created: {new Date(workflow.created_at || Date.now()).toLocaleDateString()}
                  </span>
                  <span className="mx-2">•</span>
                  <span>{Object.keys(workflow.steps || {}).length} steps</span>
                </div>
              </div>
              <div className="border-t border-gray-200 dark:border-gray-700 px-6 py-4 flex justify-between">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => router.push(`/workflow/edit/${workflow.id}`)}
                  className="text-blue-600 dark:text-blue-400"
                >
                  <HiOutlinePencil className="mr-1" /> Edit
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDelete(workflow.id)}
                  className="text-red-600 dark:text-red-400"
                >
                  <HiOutlineTrash className="mr-1" /> Delete
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleExecute(workflow.id)}
                  disabled={executingWorkflow === workflow.id}
                  className="text-green-600 dark:text-green-400"
                >
                  {executingWorkflow === workflow.id ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-green-500 mr-1"></div>
                      Running
                    </>
                  ) : (
                    <>
                      <HiOutlinePlay className="mr-1" /> Execute
                    </>
                  )}
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
} 