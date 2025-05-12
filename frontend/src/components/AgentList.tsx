'use client';

import { useState } from 'react';
import { Agent } from '@/types/agent';
import { HiOutlineStatusOnline, HiOutlineStatusOffline, 
         HiOutlineExclamation, HiOutlineTrash, HiOutlineTag } from 'react-icons/hi';

interface AgentListProps {
  agents: Agent[];
  onDelete?: (agentId: number) => Promise<void>;
}

export function AgentList({ agents, onDelete }: AgentListProps) {
  const [expandedAgentId, setExpandedAgentId] = useState<number | null>(null);

  if (!agents.length) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500 dark:text-gray-400">No agents found.</p>
      </div>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return <HiOutlineStatusOnline className="w-5 h-5 text-green-500" />;
      case 'inactive':
        return <HiOutlineStatusOffline className="w-5 h-5 text-gray-400" />;
      case 'error':
        return <HiOutlineExclamation className="w-5 h-5 text-red-500" />;
      default:
        return <HiOutlineTag className="w-5 h-5 text-blue-500" />;
    }
  };

  const toggleExpand = (agentId: number) => {
    setExpandedAgentId(expandedAgentId === agentId ? null : agentId);
  };

  const handleDelete = async (agentId: number, event: React.MouseEvent) => {
    event.stopPropagation();
    if (onDelete) {
      try {
        await onDelete(agentId);
      } catch (error) {
        console.error('Error deleting agent:', error);
      }
    }
  };

  // Format date for display
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="overflow-hidden rounded-lg border border-gray-200 dark:border-gray-800">
      <ul className="divide-y divide-gray-200 dark:divide-gray-800">
        {agents.map(agent => (
          <li 
            key={agent.id} 
            className="cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-900/50 transition-colors"
            onClick={() => agent.id && toggleExpand(agent.id)}
          >
            <div className="flex items-center justify-between px-4 py-3">
              <div className="flex items-center">
                {getStatusIcon(agent.status)}
                <div className="ml-3">
                  <p className="font-medium">{agent.name}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{agent.type}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {onDelete && agent.id && (
                  <button
                    onClick={(e) => handleDelete(agent.id!, e)}
                    className="p-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-800"
                  >
                    <HiOutlineTrash className="w-5 h-5 text-red-500" />
                  </button>
                )}
              </div>
            </div>
            {expandedAgentId === agent.id && (
              <div className="px-4 py-3 bg-gray-50 dark:bg-gray-900/30">
                <dl className="grid grid-cols-1 gap-x-4 gap-y-3 sm:grid-cols-2">
                  <div className="sm:col-span-1">
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Status</dt>
                    <dd className="mt-1 flex items-center text-sm">
                      {getStatusIcon(agent.status)}
                      <span className="ml-1 capitalize">{agent.status}</span>
                    </dd>
                  </div>
                  <div className="sm:col-span-1">
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Created</dt>
                    <dd className="mt-1 text-sm">{formatDate(agent.created_at)}</dd>
                  </div>
                  <div className="sm:col-span-1">
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Updated</dt>
                    <dd className="mt-1 text-sm">{formatDate(agent.updated_at)}</dd>
                  </div>
                  <div className="sm:col-span-2">
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Capabilities</dt>
                    <dd className="mt-1 text-sm font-mono bg-gray-100 dark:bg-gray-800 p-2 rounded overflow-auto max-h-48">
                      <pre>{JSON.stringify(agent.capabilities, null, 2)}</pre>
                    </dd>
                  </div>
                  {agent.metadata && Object.keys(agent.metadata).length > 0 && (
                    <div className="sm:col-span-2">
                      <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Metadata</dt>
                      <dd className="mt-1 text-sm font-mono bg-gray-100 dark:bg-gray-800 p-2 rounded overflow-auto max-h-48">
                        <pre>{JSON.stringify(agent.metadata, null, 2)}</pre>
                      </dd>
                    </div>
                  )}
                </dl>
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
} 