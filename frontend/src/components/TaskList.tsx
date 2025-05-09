'use client';

import { Task } from '@/types/task';

interface TaskListProps {
  tasks: Task[];
}

export function TaskList({ tasks }: TaskListProps) {
  const getStatusColor = (status: Task['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-4">
      {tasks.length === 0 ? (
        <p className="text-gray-500">No tasks found.</p>
      ) : (
        tasks.map(task => (
          <div
            key={task.id}
            className="bg-white shadow rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-lg font-medium text-gray-900">{task.name}</h3>
                <p className="text-sm text-gray-500">{task.description}</p>
              </div>
              <span
                className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(
                  task.status
                )}`}
              >
                {task.status}
              </span>
            </div>

            <div className="mt-2">
              <p className="text-sm text-gray-600">
                <span className="font-medium">Model:</span> {task.model_identifier}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">Created:</span>{' '}
                {new Date(task.created_at).toLocaleString()}
              </p>
            </div>

            {task.result && (
              <div className="mt-2">
                <p className="text-sm font-medium text-gray-700">Result:</p>
                <p className="text-sm text-gray-600 whitespace-pre-wrap">{task.result}</p>
              </div>
            )}

            {task.error && (
              <div className="mt-2">
                <p className="text-sm font-medium text-red-700">Error:</p>
                <p className="text-sm text-red-600">{task.error}</p>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
} 