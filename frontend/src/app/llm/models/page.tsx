'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { HiOutlinePlus, HiOutlineChip, HiArrowLeft } from 'react-icons/hi';
import { Button } from '@/components/base/Button';
import { getModels } from '@/api/llm';
import { LLMModel } from '@/types/llm';
import { ModelCard } from '@/components/llm/ModelCard';

export default function ModelsPage() {
  const [models, setModels] = useState<LLMModel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      const data = await getModels();
      setModels(data);
    } catch (err) {
      console.error('Error fetching models:', err);
      setError('Failed to fetch models. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Handlers for deletion
  const handleModelDelete = () => {
    fetchData(); // Refresh data after deletion
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="flex flex-col space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link 
              href="/llm" 
              className="flex items-center text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
            >
              <HiArrowLeft className="mr-2" />
              <span>Back</span>
            </Link>
            <h1 className="text-2xl font-bold">Models</h1>
          </div>
          <Link href="/llm/models/create">
            <Button size="sm" className="flex items-center">
              <HiOutlinePlus className="mr-1" />
              Add Model
            </Button>
          </Link>
        </div>

        {isLoading ? (
          <div className="text-center py-12">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-500 border-r-transparent" role="status">
              <span className="sr-only">Loading...</span>
            </div>
            <p className="mt-4 text-gray-600">Loading models...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 p-4 rounded-md">
            <p className="text-red-800 dark:text-red-200">{error}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {models.length > 0 ? (
              models.map((model) => (
                <ModelCard 
                  key={model.id} 
                  model={model} 
                  onDelete={handleModelDelete}
                />
              ))
            ) : (
              <div className="col-span-3 text-center py-16 border border-dashed border-gray-300 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-900">
                <HiOutlineChip className="mx-auto h-16 w-16 text-gray-400" />
                <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-white">No models</h3>
                <p className="mt-2 text-gray-500 dark:text-gray-400 max-w-sm mx-auto">
                  Add your first model to get started.
                </p>
                <div className="mt-6">
                  <Link href="/llm/models/create">
                    <Button
                      size="default"
                      className="flex items-center mx-auto"
                    >
                      <HiOutlinePlus className="mr-1" />
                      Add Model
                    </Button>
                  </Link>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
} 