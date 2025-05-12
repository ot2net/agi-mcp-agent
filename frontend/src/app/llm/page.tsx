'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { HiOutlinePlus, HiOutlineChip, HiOutlineCog } from 'react-icons/hi';
import { Button } from '@/components/base/Button';
import { Card } from '@/components/base/Card';
import { getProviders, getModels } from '@/api/llm';
import { LLMProvider, LLMModel } from '@/types/llm';

export default function LLMPage() {
  const [providers, setProviders] = useState<LLMProvider[]>([]);
  const [models, setModels] = useState<LLMModel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const [providersData, modelsData] = await Promise.all([
          getProviders(),
          getModels()
        ]);
        setProviders(providersData);
        setModels(modelsData);
        setError(null);
      } catch (error) {
        console.error('Error fetching LLM data:', error);
        setError('Failed to load data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">LLM Model Management</h1>
        <div className="flex space-x-4">
          <Link href="/llm/providers/create">
            <Button
              size="sm"
              icon={<HiOutlinePlus className="w-4 h-4" />}
              variant="outline"
            >
              Add Provider
            </Button>
          </Link>
          <Link href="/llm/models/create">
            <Button
              size="sm"
              icon={<HiOutlinePlus className="w-4 h-4" />}
            >
              Add Model
            </Button>
          </Link>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800">
          <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      ) : (
        <div className="space-y-8">
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold flex items-center">
                <HiOutlineCog className="w-5 h-5 mr-2" />
                Providers
              </h2>
              <Link href="/llm/providers">
                <Button
                  size="sm"
                  variant="outline"
                >
                  View All ({providers.length})
                </Button>
              </Link>
            </div>

            {providers.length === 0 ? (
              <Card>
                <div className="text-center py-8">
                  <p className="text-gray-500 dark:text-gray-400 mb-4">No providers available</p>
                  <Link href="/llm/providers/create">
                    <Button icon={<HiOutlinePlus className="w-4 h-4" />}>
                      Add Provider
                    </Button>
                  </Link>
                </div>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {providers.slice(0, 3).map(provider => (
                  <Card
                    key={provider.id}
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
                    
                    <div className="mt-6 flex justify-end">
                      <Link href={`/llm/providers/${provider.id}`}>
                        <Button
                          variant="outline"
                          size="sm"
                        >
                          View Details
                        </Button>
                      </Link>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>

          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold flex items-center">
                <HiOutlineChip className="w-5 h-5 mr-2" />
                Models
              </h2>
              <Link href="/llm/models">
                <Button
                  size="sm"
                  variant="outline"
                >
                  View All ({models.length})
                </Button>
              </Link>
            </div>

            {models.length === 0 ? (
              <Card>
                <div className="text-center py-8">
                  <p className="text-gray-500 dark:text-gray-400 mb-4">No models available</p>
                  <Link href="/llm/models/create">
                    <Button icon={<HiOutlinePlus className="w-4 h-4" />}>
                      Add Model
                    </Button>
                  </Link>
                </div>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {models.slice(0, 3).map(model => (
                  <Card
                    key={model.id}
                    title={model.model_name}
                    description={`Provider: ${model.provider_name}`}
                    icon={<HiOutlineChip className="w-6 h-6" />}
                  >
                    <div className="mt-4 grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Capability</p>
                        <p className="font-medium">{model.capability}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Status</p>
                        <p className={`font-medium ${model.status === 'enabled' ? 'text-green-500' : 'text-red-500'}`}>
                          {model.status === 'enabled' ? 'Enabled' : 'Disabled'}
                        </p>
                      </div>
                    </div>
                    
                    <div className="mt-6 flex justify-end">
                      <Link href={`/llm/models/${model.id}`}>
                        <Button
                          variant="outline"
                          size="sm"
                        >
                          View Details
                        </Button>
                      </Link>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
} 