'use client';

import { useState, useEffect } from 'react';
import { TaskForm } from '@/components/TaskForm';
import { TaskList } from '@/components/TaskList';
import { LoadingState } from '@/components/LoadingState';
import { Task } from '@/types/task';
import { Card } from '@/components/base/Card';
import { Button } from '@/components/base/Button';
import { HiOutlinePlus, HiOutlineServer, HiOutlineRefresh } from 'react-icons/hi';

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
    <div className="container mx-auto px-4 py-8 space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Tasks</h1>
        <Button
          variant="outline"
          onClick={fetchTasks}
          className="animate-fade-in"
          icon={<HiOutlineRefresh className="w-5 h-5" />}
        >
          Refresh
        </Button>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <Card
            title="Create New Task"
            description="Configure and create a new AI task"
            icon={<HiOutlinePlus className="w-6 h-6" />}
            showDivider
          >
            <TaskForm onSubmit={handleCreateTask} />
          </Card>
        </div>
        <div>
          <Card
            title="Task List"
            description="View and manage your AI tasks"
            icon={<HiOutlineServer className="w-6 h-6" />}
            showDivider
          >
            {error && (
              <div className="mb-4 rounded-lg bg-red-50 dark:bg-red-900/10 p-4 border border-red-200 dark:border-red-800">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-red-800 dark:text-red-200">{error}</p>
                  </div>
                </div>
              </div>
            )}
            <div className="animate-fade-in">
              {isLoading ? <LoadingState /> : <TaskList tasks={tasks} />}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
} 