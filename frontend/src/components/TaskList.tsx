'use client';

import { Task } from '@/types/task';
import { formatDistanceToNow } from 'date-fns';

interface TaskListProps {
  tasks: Task[];
}

export function TaskList({ tasks }: TaskListProps) {
  const getStatusColor = (status: Task['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-50 text-green-700 ring-green-600/20';
      case 'running':
        return 'bg-blue-50 text-blue-700 ring-blue-600/20';
      case 'failed':
        return 'bg-red-50 text-red-700 ring-red-600/20';
      default:
        return 'bg-gray-50 text-gray-700 ring-gray-600/20';
    }
  };

  const getStatusIcon = (status: Task['status']) => {
    switch (status) {
      case 'completed':
        return (
          <svg className="h-1.5 w-1.5 fill-green-500" viewBox="0 0 6 6" aria-hidden="true">
            <circle cx="3" cy="3" r="3" />
          </svg>
        );
      case 'running':
        return (
          <svg className="h-1.5 w-1.5 fill-blue-500 animate-pulse" viewBox="0 0 6 6" aria-hidden="true">
            <circle cx="3" cy="3" r="3" />
          </svg>
        );
      case 'failed':
        return (
          <svg className="h-1.5 w-1.5 fill-red-500" viewBox="0 0 6 6" aria-hidden="true">
            <circle cx="3" cy="3" r="3" />
          </svg>
        );
      default:
        return (
          <svg className="h-1.5 w-1.5 fill-gray-500" viewBox="0 0 6 6" aria-hidden="true">
            <circle cx="3" cy="3" r="3" />
          </svg>
        );
    }
  };

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <svg
          className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
          />
        </svg>
        <h3 className="mt-2 text-sm font-semibold text-gray-900 dark:text-white">No tasks</h3>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Get started by creating a new task.</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden">
      <ul role="list" className="divide-y divide-gray-200 dark:divide-gray-700">
        {tasks.map((task) => (
          <li 
            key={task.id} 
            className="relative flex justify-between gap-x-6 px-4 py-5 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors duration-200"
          >
            <div className="flex min-w-0 gap-x-4">
              <div className="min-w-0 flex-auto">
                <div className="flex items-center gap-x-3">
                  <h2 className="text-sm font-semibold leading-6 text-gray-900 dark:text-white">
                    {task.name}
                  </h2>
                  <div
                    className={`flex-none rounded-full px-2 py-1 text-xs font-medium ring-1 ring-inset ${getStatusColor(
                      task.status
                    )}`}
                  >
                    <div className="flex items-center gap-1">
                      {getStatusIcon(task.status)}
                      <span>{task.status}</span>
                    </div>
                  </div>
                </div>
                <div className="mt-1 flex text-xs leading-5 text-gray-500 dark:text-gray-400">
                  <p className="relative truncate hover:underline">
                    {task.description}
                  </p>
                </div>
              </div>
            </div>
            <div className="flex shrink-0 items-center gap-x-4">
              <div className="hidden sm:flex sm:flex-col sm:items-end">
                <p className="text-sm leading-6 text-gray-900 dark:text-white">
                  {task.model_identifier}
                </p>
                <p className="mt-1 text-xs leading-5 text-gray-500 dark:text-gray-400">
                  Created {formatDistanceToNow(new Date(task.created_at))} ago
                </p>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
} 