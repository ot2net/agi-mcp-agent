'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/base/Button';
import { Input } from '@/components/base/Input';
import { Select } from '@/components/base/Select';
import { FormField } from '@/components/base/FormField';
import { LLMModelCreate, LLMProvider } from '@/types/llm';
import { createModel, getProviders } from '@/api/llm';
import { ModelIcon } from '@/components/llm/ModelIcon';

export function CreateModelForm() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [providers, setProviders] = useState<LLMProvider[]>([]);
  const [isLoadingProviders, setIsLoadingProviders] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<LLMModelCreate>({
    provider_id: 0,
    model_name: '',
    capability: 'embedding',
    params: {
      temperature: 0.7,
      max_tokens: 1000
    },
  });

  useEffect(() => {
    const fetchProviders = async () => {
      try {
        const data = await getProviders();
        setProviders(data);
        
        // Set default provider if available
        if (data.length > 0) {
          setFormData(prevData => ({
            ...prevData,
            provider_id: data[0].id,
          }));
        }
      } catch (error) {
        console.error('Error fetching providers:', error);
        setError('Failed to load providers. Please try again later.');
      } finally {
        setIsLoadingProviders(false);
      }
    };

    fetchProviders();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;

    if (name === 'provider_id') {
      setFormData(prevData => ({
        ...prevData,
        provider_id: parseInt(value, 10),
      }));
    } else {
      setFormData(prevData => ({
        ...prevData,
        [name]: value,
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    // Automatically set appropriate default parameters based on capability
    let updatedParams = {...formData.params};
    
    if (formData.capability === 'chat') {
      updatedParams = {
        temperature: 0.7,
        max_tokens: 1000,
        top_p: 0.95,
        frequency_penalty: 0,
        presence_penalty: 0
      };
    } else if (formData.capability === 'embedding') {
      updatedParams = {
        dimensions: 1536
      };
    } else if (formData.capability === 'completion') {
      updatedParams = {
        temperature: 0.7,
        max_tokens: 1000,
        top_p: 0.95
      };
    }
    
    const finalFormData = {
      ...formData,
      params: updatedParams
    };
    
    try {
      setIsLoading(true);
      await createModel(finalFormData);
      router.push('/llm/models');
      router.refresh();
    } catch (error) {
      console.error('Error creating model:', error);
      setError('Failed to create model. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const presetModels = {
    openai: ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-vision-preview', 'text-embedding-ada-002'],
    anthropic: ['claude-2', 'claude-instant-1', 'claude-3-sonnet', 'claude-3-opus'],
    mistral: ['mistral-tiny', 'mistral-small', 'mistral-medium', 'mistral-large'],
    cohere: ['command', 'command-light', 'command-r', 'embed-english-v3.0'],
    google: ['gemini-pro', 'gemini-pro-vision', 'gemini-ultra', 'text-embedding-gecko'],
    deepseek: ['deepseek-chat', 'deepseek-coder'],
  };

  const getModelSuggestions = () => {
    const provider = providers.find(p => p.id === formData.provider_id);
    if (!provider) return [];
    
    const providerType = provider.type.toLowerCase() as keyof typeof presetModels;
    return presetModels[providerType] || [];
  };

  // Get the current selected provider's type
  const getSelectedProviderType = () => {
    const provider = providers.find(p => p.id === formData.provider_id);
    return provider?.type || '';
  };

  // Auto-select popular models when provider changes
  useEffect(() => {
    const provider = providers.find(p => p.id === formData.provider_id);
    if (!provider) return;
    
    const providerType = provider.type.toLowerCase() as keyof typeof presetModels;
    const models = presetModels[providerType] || [];
    
    // For embedding capability, auto-select embedding model when available
    if (formData.capability === 'embedding') {
      if (providerType === 'openai') {
        setFormData(prev => ({
          ...prev,
          model_name: 'text-embedding-ada-002'
        }));
      } else if (providerType === 'cohere') {
        setFormData(prev => ({
          ...prev,
          model_name: 'embed-english-v3.0'
        }));
      } else if (providerType === 'google') {
        setFormData(prev => ({
          ...prev,
          model_name: 'text-embedding-gecko'
        }));
      }
    } 
    // For chat capability, auto-select first chat model when available
    else if (formData.capability === 'chat' && models.length > 0) {
      setFormData(prev => ({
        ...prev,
        model_name: models[0]
      }));
    }
  }, [formData.provider_id, formData.capability, providers]);

  if (isLoadingProviders) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-500 border-r-transparent" role="status">
          <span className="sr-only">Loading...</span>
        </div>
        <p className="ml-3 text-gray-600">Loading providers...</p>
      </div>
    );
  }

  if (providers.length === 0) {
    return (
      <div className="text-center py-8 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="mx-auto w-16 h-16 flex items-center justify-center rounded-full bg-blue-50 dark:bg-blue-900/20 mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 className="text-xl font-semibold mb-2">No Providers Available</h3>
        <p className="mb-6 text-gray-500 dark:text-gray-400 max-w-sm mx-auto">
          You need to add a provider before you can create a model.
        </p>
        <Button 
          onClick={() => router.push('/llm/providers/create')}
          className="px-6"
        >
          Add Provider
        </Button>
      </div>
    );
  }

  // Custom Provider Select with Icons
  const ProviderSelect = () => {
    const selectedProviderType = getSelectedProviderType();
    
    return (
      <div className="relative">
        <select
          id="provider_id"
          name="provider_id"
          required
          value={formData.provider_id.toString()}
          onChange={handleChange}
          className="block w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 pl-12 pr-4 py-3 text-lg text-left shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          {providers.map((provider) => (
            <option key={provider.id} value={provider.id.toString()}>
              {provider.name} ({provider.type})
            </option>
          ))}
        </select>
        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
          <ModelIcon type={selectedProviderType} size="md" withBackground={true} />
        </div>
      </div>
    );
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800">
          <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}
      
      <div className="bg-white dark:bg-gray-800 p-8 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-2xl font-medium mb-6">Basic Information</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
          <div>
            <label htmlFor="provider_id" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
              Provider <span className="text-red-500">*</span>
            </label>
            <ProviderSelect />
          </div>

          <div>
            <label htmlFor="model_name" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
              Model Name <span className="text-red-500">*</span>
            </label>
            <Input
              id="model_name"
              name="model_name"
              type="text"
              required
              list="model-suggestions"
              value={formData.model_name}
              onChange={handleChange}
              placeholder="e.g., gpt-3.5-turbo"
              className="py-3 text-lg"
            />
            <datalist id="model-suggestions">
              {getModelSuggestions().map(model => (
                <option key={model} value={model} />
              ))}
            </datalist>
          </div>
        </div>
        
        <div className="mt-6">
          <label htmlFor="capability" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
            Capability <span className="text-red-500">*</span>
          </label>
          <div className="flex flex-wrap gap-6 mt-2">
            <label className="flex items-center">
              <input
                type="radio"
                name="capability"
                value="chat"
                checked={formData.capability === 'chat'}
                onChange={handleChange}
                className="w-5 h-5 rounded-full text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-base">Chat</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="capability"
                value="embedding"
                checked={formData.capability === 'embedding'}
                onChange={handleChange}
                className="w-5 h-5 rounded-full text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-base">Embedding</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="capability"
                value="completion"
                checked={formData.capability === 'completion'}
                onChange={handleChange}
                className="w-5 h-5 rounded-full text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-base">Completion</span>
            </label>
          </div>
        </div>
      </div>

      <div className="flex justify-end space-x-4">
        <Button
          type="button"
          variant="outline"
          size="lg"
          onClick={() => router.back()}
          className="px-6"
        >
          Cancel
        </Button>
        <Button
          type="submit"
          size="lg"
          disabled={isLoading}
          className="px-6"
        >
          {isLoading ? 'Creating...' : 'Create Model'}
        </Button>
      </div>
    </form>
  );
} 