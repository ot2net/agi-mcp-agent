'use client';

import { useState } from 'react';
import { LLMModel } from '@/types/llm';
import { Button } from '@/components/base/Button';
import { HiOutlineTrash, HiOutlineEye } from 'react-icons/hi';
import { deleteModel } from '@/api/llm';
import Link from 'next/link';
import { ModelIcon } from '@/components/llm/ModelIcon';

interface ModelCardProps {
  model: LLMModel;
  onDelete: () => void;
}

export function ModelCard({ model, onDelete }: ModelCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (confirm(`Are you sure you want to delete model ${model.model_name}?`)) {
      try {
        setIsDeleting(true);
        await deleteModel(model.id);
        onDelete();
      } catch (error) {
        console.error('Error deleting model:', error);
        alert('Failed to delete model');
      } finally {
        setIsDeleting(false);
      }
    }
  };

  // Get capability information for display
  const getCapabilityInfo = (capability: string) => {
    switch (capability) {
      case 'chat':
        return {
          text: 'Chat',
          color: 'text-blue-500 bg-blue-50 border-blue-200',
        };
      case 'embedding':
        return {
          text: 'Embedding',
          color: 'text-purple-500 bg-purple-50 border-purple-200',
        };
      case 'completion':
        return {
          text: 'Completion',
          color: 'text-green-500 bg-green-50 border-green-200',
        };
      default:
        return {
          text: capability,
          color: 'text-gray-500 bg-gray-50 border-gray-200',
        };
    }
  };

  const capabilityInfo = getCapabilityInfo(model.capability);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow duration-200 overflow-hidden">
      {/* Model header with icon */}
      <div className="p-5 flex items-center space-x-3">
        <ModelIcon type={model.provider_name || 'model'} size="lg" withBackground={true} />
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{model.model_name}</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">Provider: {model.provider_name}</p>
        </div>
      </div>
      
      {/* Model details */}
      <div className="px-5 pb-4 grid grid-cols-2 gap-6">
        <div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Capability</p>
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium ${capabilityInfo.color}`}>
            {capabilityInfo.text}
          </span>
        </div>
        <div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Status</p>
          <p className={`text-sm font-medium ${model.status === 'enabled' ? 'text-green-500' : 'text-red-500'}`}>
            {model.status === 'enabled' ? 'Enabled' : 'Disabled'}
          </p>
        </div>
      </div>
      
      {/* Button actions */}
      <div className="border-t border-gray-200 dark:border-gray-700 p-4 flex justify-end space-x-3">
        <Link href={`/llm/models/${model.id}`}>
          <Button
            variant="outline"
            size="sm"
            icon={<HiOutlineEye className="w-4 h-4" />}
          >
            View
          </Button>
        </Link>
        <Button
          variant="outline"
          size="sm"
          icon={<HiOutlineTrash className="w-4 h-4" />}
          onClick={handleDelete}
          disabled={isDeleting}
          className="text-red-500 border-red-300 hover:bg-red-50"
        >
          {isDeleting ? 'Deleting...' : 'Delete'}
        </Button>
      </div>
    </div>
  );
} 