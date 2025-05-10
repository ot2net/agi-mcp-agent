'use client';

import { Environment } from '@/types/environment';
import { formatDistanceToNow } from 'date-fns';
import { HiOutlineServer, HiOutlineTrash } from 'react-icons/hi';
import { Button } from '@/components/base/Button';

interface EnvironmentListProps {
  environments: Environment[];
  selectedEnvironment: Environment | null;
  onSelect: (env: Environment) => void;
  onDelete: (env: Environment) => void;
}

const ENV_TYPE_COLORS: Record<string, string> = {
  api: 'bg-blue-50 text-blue-700 ring-blue-600/20',
  filesystem: 'bg-green-50 text-green-700 ring-green-600/20',
  memory: 'bg-purple-50 text-purple-700 ring-purple-600/20',
  web: 'bg-yellow-50 text-yellow-700 ring-yellow-600/20',
  database: 'bg-indigo-50 text-indigo-700 ring-indigo-600/20',
  mcp: 'bg-red-50 text-red-700 ring-red-600/20',
};

const ENV_TYPE_ICONS: Record<string, React.ReactNode> = {
  api: <HiOutlineServer className="w-4 h-4" />,
  filesystem: <HiOutlineServer className="w-4 h-4" />,
  memory: <HiOutlineServer className="w-4 h-4" />,
  web: <HiOutlineServer className="w-4 h-4" />,
  database: <HiOutlineServer className="w-4 h-4" />,
  mcp: <HiOutlineServer className="w-4 h-4" />,
};

export function EnvironmentList({ environments, selectedEnvironment, onSelect, onDelete }: EnvironmentListProps) {
  if (environments.length === 0) {
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
        <h3 className="mt-2 text-sm font-semibold text-gray-900 dark:text-white">No environments</h3>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Get started by creating a new environment.</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden">
      <ul role="list" className="divide-y divide-gray-200 dark:divide-gray-700">
        {environments.map((env) => (
          <li 
            key={env.id} 
            className="relative flex justify-between gap-x-6 px-4 py-5 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors duration-200"
          >
            <div className="flex min-w-0 gap-x-4">
              <div className="min-w-0 flex-auto">
                <div className="flex items-center gap-x-3">
                  <h2 className="text-sm font-semibold leading-6 text-gray-900 dark:text-white">
                    {env.name}
                  </h2>
                  <div
                    className={`flex-none rounded-full px-2 py-1 text-xs font-medium ring-1 ring-inset ${ENV_TYPE_COLORS[env.type] || 'bg-gray-50 text-gray-700 ring-gray-600/20'}`}
                  >
                    <div className="flex items-center gap-1">
                      {ENV_TYPE_ICONS[env.type] || <HiOutlineServer className="w-4 h-4" />}
                      <span>{env.type}</span>
                    </div>
                  </div>
                </div>
                <div className="mt-1 flex text-xs leading-5 text-gray-500 dark:text-gray-400">
                  <p className="relative truncate hover:underline">
                    {env.status}
                  </p>
                </div>
              </div>
            </div>
            <div className="flex shrink-0 items-center gap-x-4">
              <Button
                variant="ghost"
                size="sm"
                className="text-red-500 hover:text-red-700"
                onClick={() => onDelete(env)}
                icon={<HiOutlineTrash className="w-4 h-4" />}
              />
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
} 