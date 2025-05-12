'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { HiOutlinePlus, HiOutlineChip, HiOutlineCog, HiArrowRight } from 'react-icons/hi';
import { Button } from '@/components/base/Button';
import { getProviders, getModels } from '@/api/llm';
import { LLMProvider, LLMModel } from '@/types/llm';
import { ProviderCard } from '@/components/llm/ProviderCard';
import { ModelCard } from '@/components/llm/ModelCard';
import { ModelIcon } from '@/components/llm/ModelIcon';

export default function LLMPage() {
  const [providers, setProviders] = useState<LLMProvider[]>([]);
  const [models, setModels] = useState<LLMModel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'providers' | 'models'>('providers');

  const fetchData = async () => {
    try {
      setIsLoading(true);
      const [providersData, modelsData] = await Promise.all([
        getProviders(),
        getModels(),
      ]);
      setProviders(providersData);
      setModels(modelsData);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to fetch data. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Simple setup guide for new users
  const showSetupGuide = providers.length === 0 && models.length === 0;

  // Handlers for deletion
  const handleProviderDelete = () => {
    fetchData(); // Refresh data after deletion
  };

  const handleModelDelete = () => {
    fetchData(); // Refresh data after deletion
  };

  // Available model icons to show in the setup guide
  const availableProviders = ['openai', 'anthropic', 'google', 'deepseek', 'qwen', 'mistral'];

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="flex flex-col space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">LLM Management</h1>
          {!showSetupGuide && (
            <div className="flex items-center space-x-3">
              <Link href="/llm/providers/create">
                <Button 
                  size="sm"
                  className="flex items-center"
                >
                  <HiOutlinePlus className="mr-1" />
                  Add Provider
                </Button>
              </Link>
              <Link href="/llm/models/create">
                <Button
                  size="sm"
                  className="flex items-center"
                  disabled={providers.length === 0}
                >
                  <HiOutlinePlus className="mr-1" />
                  Add Model
                </Button>
              </Link>
            </div>
          )}
        </div>

        {showSetupGuide ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-8">
            <h2 className="text-xl font-semibold mb-4">Set up your LLM Integration</h2>
            <p className="mb-8 text-gray-600 dark:text-gray-400 max-w-3xl">
              Configure your LLM providers and models to use with the AI agents. Just add your API key and you're ready to go.
            </p>
            
            <div className="flex flex-wrap justify-center gap-8 mb-10">
              {availableProviders.map(provider => (
                <div key={provider} className="text-center">
                  <ModelIcon key={provider} type={provider} size="xl" withBackground={true} />
                  <p className="mt-2 text-sm text-gray-600 capitalize">{provider}</p>
                </div>
              ))}
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
              <div className="bg-gray-50 dark:bg-gray-900 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
                <div className="flex items-center mb-4">
                  <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center mr-3">
                    <span className="text-blue-600 dark:text-blue-400 font-bold">1</span>
                  </div>
                  <h3 className="text-lg font-medium">Add a Provider</h3>
                </div>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                  Start by adding an LLM provider like OpenAI, Anthropic, or Mistral AI with your API key.
                </p>
                <Link href="/llm/providers/create">
                  <Button className="w-full flex items-center justify-center">
                    Add Provider <HiArrowRight className="ml-2" />
                  </Button>
                </Link>
              </div>
              
              <div className="bg-gray-50 dark:bg-gray-900 p-6 rounded-lg border border-gray-200 dark:border-gray-700 opacity-75">
                <div className="flex items-center mb-4">
                  <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center mr-3">
                    <span className="text-blue-600 dark:text-blue-400 font-bold">2</span>
                  </div>
                  <h3 className="text-lg font-medium">Add Models</h3>
                </div>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                  Once you've added a provider, you can configure the specific models you want to use.
                </p>
                <Button
                  disabled
                  className="w-full flex items-center justify-center cursor-not-allowed"
                >
                  Add Models <HiArrowRight className="ml-2" />
                </Button>
              </div>
            </div>
          </div>
        ) : (
          <>
            <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
              <nav className="-mb-px flex space-x-8">
                <button
                  onClick={() => setActiveTab('providers')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'providers'
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  Providers ({providers.length})
                </button>
                <button
                  onClick={() => setActiveTab('models')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'models'
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  Models ({models.length})
                </button>
              </nav>
            </div>

            {isLoading ? (
              <div className="text-center py-12">
                <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-500 border-r-transparent" role="status">
                  <span className="sr-only">Loading...</span>
                </div>
                <p className="mt-4 text-gray-600">Loading...</p>
              </div>
            ) : error ? (
              <div className="bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 p-4 rounded-md">
                <p className="text-red-800 dark:text-red-200">{error}</p>
              </div>
            ) : (
              <div className="space-y-6">
                {activeTab === 'providers' && (
                  <>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {providers.length > 0 ? (
                        providers.map((provider) => (
                          <ProviderCard 
                            key={provider.id} 
                            provider={provider} 
                            onDelete={handleProviderDelete}
                          />
                        ))
                      ) : (
                        <div className="col-span-3 text-center py-16 border border-dashed border-gray-300 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-900">
                          <HiOutlineCog className="mx-auto h-16 w-16 text-gray-400" />
                          <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-white">No providers</h3>
                          <p className="mt-2 text-gray-500 dark:text-gray-400 max-w-sm mx-auto">
                            Get started by adding a new LLM provider.
                          </p>
                          <div className="mt-6">
                            <Link href="/llm/providers/create">
                              <Button
                                size="default"
                                className="flex items-center mx-auto"
                              >
                                <HiOutlinePlus className="mr-1" />
                                Add Provider
                              </Button>
                            </Link>
                          </div>
                        </div>
                      )}
                    </div>
                  </>
                )}

                {activeTab === 'models' && (
                  <>
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
                            {providers.length > 0 
                              ? "Add your first model to get started."
                              : "You need to add a provider before adding models."}
                          </p>
                          <div className="mt-6">
                            {providers.length > 0 ? (
                              <Link href="/llm/models/create">
                                <Button
                                  size="default"
                                  className="flex items-center mx-auto"
                                >
                                  <HiOutlinePlus className="mr-1" />
                                  Add Model
                                </Button>
                              </Link>
                            ) : (
                              <Link href="/llm/providers/create">
                                <Button
                                  size="default"
                                  className="flex items-center mx-auto"
                                >
                                  <HiOutlinePlus className="mr-1" />
                                  Add Provider First
                                </Button>
                              </Link>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
} 