'use client';

import { useState } from 'react';
import { LLMProvider } from '@/types/llm';
import { Card } from '@/components/base/Card';
import { Button } from '@/components/base/Button';
import { HiOutlineTrash, HiOutlineEye, HiOutlineCog } from 'react-icons/hi';
import { deleteProvider } from '@/api/llm';
import Link from 'next/link';

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
    <Card 
      title={provider.name}
      description={`Type: ${provider.type}`}
      icon={<HiOutlineCog className="w-6 h-6" />}
    >
      <div className="mt-4 grid grid-cols-2 gap-4">
        <div>
          <p className="text-sm text-gray-500 dark:text-gray-400">Status</p>
          <p className={`font-medium ${provider.status === 'enabled' ? 'text-green-500' : 'text-red-500'}`}>
            {provider.status === 'enabled' ? 'Enabled' : 'Disabled'}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-500 dark:text-gray-400">Models Count</p>
          <p className="font-medium">{provider.models_count}</p>
        </div>
      </div>
      
      <div className="mt-6 flex space-x-2 justify-end">
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
    </Card>
  );
} 