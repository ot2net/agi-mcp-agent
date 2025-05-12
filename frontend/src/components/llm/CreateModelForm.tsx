'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/base/Button';
import { LLMModelCreate, LLMProvider } from '@/types/llm';
import { createModel, getProviders } from '@/api/llm';

export function CreateModelForm() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [providers, setProviders] = useState<LLMProvider[]>([]);
  const [isLoadingProviders, setIsLoadingProviders] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<LLMModelCreate>({
    provider_id: 0,
    model_name: '',
    capability: 'chat',
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
    anthropic: ['claude-2', 'claude-instant-1'],
    mistral: ['mistral-tiny', 'mistral-small', 'mistral-medium'],
    cohere: ['command', 'command-light', 'embed-english-v3.0'],
  };

  const getModelSuggestions = () => {
    const provider = providers.find(p => p.id === formData.provider_id);
    if (!provider) return [];
    
    const providerType = provider.type as keyof typeof presetModels;
    return presetModels[providerType] || [];
  };

  // Auto-select popular models when provider changes
  useEffect(() => {
    const provider = providers.find(p => p.id === formData.provider_id);
    if (!provider) return;
    
    const providerType = provider.type as keyof typeof presetModels;
    const models = presetModels[providerType] || [];
    
    // For embedding capability, auto-select embedding model when available
    if (formData.capability === 'embedding' && providerType === 'openai') {
      setFormData(prev => ({
        ...prev,
        model_name: 'text-embedding-ada-002'
      }));
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
    return <div className="text-center py-4">Loading providers...</div>;
  }

  if (providers.length === 0) {
    return (
      <div className="text-center py-4">
        <p className="mb-4">No providers available. Please create a provider first.</p>
        <Button onClick={() => router.push('/llm/providers/create')}>
          Create Provider
        </Button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800">
          <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}
      
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-medium mb-4">Basic Information</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="provider_id" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Provider *
            </label>
            <select
              id="provider_id"
              name="provider_id"
              required
              value={formData.provider_id}
              onChange={handleChange}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-700"
            >
              {providers.map(provider => (
                <option key={provider.id} value={provider.id}>
                  {provider.name} ({provider.type})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="model_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Model Name *
            </label>
            <input
              id="model_name"
              name="model_name"
              type="text"
              required
              list="model-suggestions"
              value={formData.model_name}
              onChange={handleChange}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-700"
              placeholder="e.g., gpt-3.5-turbo"
            />
            <datalist id="model-suggestions">
              {getModelSuggestions().map(model => (
                <option key={model} value={model} />
              ))}
            </datalist>
          </div>
        </div>
        
        <div className="mt-4">
          <label htmlFor="capability" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Capability *
          </label>
          <div className="flex flex-wrap gap-3 mt-1">
            {['chat', 'embedding', 'completion'].map(capability => (
              <label key={capability} className="flex items-center">
                <input
                  type="radio"
                  name="capability"
                  value={capability}
                  checked={formData.capability === capability}
                  onChange={handleChange}
                  className="rounded-full text-blue-600 focus:ring-blue-500 h-4 w-4"
                />
                <span className="ml-2 text-sm capitalize">{capability}</span>
              </label>
            ))}
          </div>
        </div>
      </div>

      <div className="flex justify-end space-x-4">
        <Button
          type="button"
          variant="outline"
          onClick={() => router.back()}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          disabled={isLoading}
        >
          {isLoading ? 'Creating...' : 'Create Model'}
        </Button>
      </div>
    </form>
  );
} 