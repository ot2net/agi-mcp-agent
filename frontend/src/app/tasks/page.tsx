'use client';

import { useState, useEffect } from 'react';
import { TaskForm } from '@/components/TaskForm';
import { TaskList } from '@/components/TaskList';
import { LoadingState } from '@/components/LoadingState';
import { Task } from '@/types/task';
import { Card } from '@/components/base/Card';
import { Button } from '@/components/base/Button';

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(true);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const response = await fetch('/api/tasks');
      if (!response.ok) {
        throw new Error('Failed to fetch tasks');
      }
      const data = await response.json();
      setTasks(data);
      setError(null);
    } catch (err) {
      setError('Failed to load tasks. Please try again later.');
      console.error('Error fetching tasks:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateTask = async (taskData: Omit<Task, 'id' | 'status' | 'created_at' | 'completed_at'>) => {
    try {
      const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(taskData),
      });

      if (!response.ok) {
        throw new Error('Failed to create task');
      }

      const newTask = await response.json();
      setTasks(prevTasks => [...prevTasks, newTask]);
      setError(null);
    } catch (err) {
      console.error('Error creating task:', err);
      setError('Failed to create task. Please try again.');
    }
  };

  return (
    <div className="flex flex-col gap-8 max-w-5xl mx-auto">
      {/* 页面主标题和副标题 */}
      <div className="mb-2">
        <h2 className="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:truncate sm:text-3xl sm:tracking-tight">
          Create New Task
        </h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Configure and create a new AI task
        </p>
      </div>
      <div className="flex flex-col md:flex-row gap-8">
        {/* 左侧：表单卡片 */}
        <div className="flex-1 min-w-0">
          <Card>
            <TaskForm onSubmit={handleCreateTask} />
          </Card>
        </div>
        {/* 右侧：任务列表卡片 */}
        <div className="flex-1 min-w-0">
          <Card>
            {error && (
              <div className="mb-4 rounded-md bg-red-50 p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-red-800">{error}</p>
                  </div>
                </div>
              </div>
            )}
            {isLoading ? <LoadingState /> : <TaskList tasks={tasks} />}
          </Card>
        </div>
      </div>
      {/* 底部操作栏，可扩展 */}
      <div className="flex justify-end gap-2">
        <Button variant="secondary" onClick={() => fetchTasks()}>
          Refresh
        </Button>
      </div>
    </div>
  );
} 