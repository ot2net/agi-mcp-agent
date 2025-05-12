'use client';

import { useState } from 'react';
import { LLMProvider } from '@/types/llm';
import { Card } from '@/components/base/Card';
import { Button } from '@/components/base/Button';
import { HiOutlineTrash, HiOutlineEye } from 'react-icons/hi';
import { deleteProvider } from '@/api/llm';
import Link from 'next/link';
import { ModelIcon } from '@/components/llm/ModelIcon';

interface ProviderCardProps {
  provider: LLMProvider;
  onDelete: () => void;
}

export function ProviderCard({ provider, onDelete }: ProviderCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (confirm(`Are you sure you want to delete provider ${provider.name}?`)) {
      try {
        setIsDeleting(true);
        await deleteProvider(provider.id);
        onDelete();
      } catch (error) {
        console.error('Error deleting provider:', error);
        alert('Failed to delete provider');
      } finally {
        setIsDeleting(false);
      }
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow duration-200 overflow-hidden">
      {/* Provider header with icon */}
      <div className="p-5 flex items-center space-x-3">
        <ModelIcon type={provider.type} size="lg" withBackground={true} />
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{provider.name}</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">Type: {provider.type}</p>
        </div>
      </div>
      
      {/* Provider details */}
      <div className="px-5 pb-4 grid grid-cols-2 gap-6">
        <div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Status</p>
          <p className={`text-sm font-medium ${provider.status === 'enabled' ? 'text-green-500' : 'text-red-500'}`}>
            {provider.status === 'enabled' ? 'Enabled' : 'Disabled'}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Models Count</p>
          <p className="text-sm font-medium">{provider.models_count || 0}</p>
        </div>
      </div>
      
      {/* Button actions */}
      <div className="border-t border-gray-200 dark:border-gray-700 p-4 flex justify-end space-x-3">
        <Link href={`/llm/providers/${provider.id}`}>
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