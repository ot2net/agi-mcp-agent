'use client';

import { CreateProviderForm } from '@/components/llm/CreateProviderForm';
import Link from 'next/link';
import { HiArrowLeft } from 'react-icons/hi';

export default function CreateProviderPage() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-6">
        <Link 
          href="/llm" 
          className="flex items-center text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
        >
          <HiArrowLeft className="mr-2" />
          <span>Back to Providers</span>
        </Link>
      </div>
      
      <h1 className="text-2xl font-bold mb-6">Add New Provider</h1>
      
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <CreateProviderForm />
      </div>
    </div>
  );
} 