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
    params: {},
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

  const handleParamsChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    try {
      const params = JSON.parse(e.target.value);
      setFormData(prevData => ({
        ...prevData,
        params,
      }));
    } catch (error) {
      // Silently ignore invalid JSON - will validate on submit
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    try {
      setIsLoading(true);
      await createModel(formData);
      router.push('/llm/models');
      router.refresh();
    } catch (error) {
      console.error('Error creating model:', error);
      setError('Failed to create model. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

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
      
      <div>
        <label htmlFor="provider_id" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Provider *
        </label>
        <select
          id="provider_id"
          name="provider_id"
          required
          value={formData.provider_id}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-700"
        >
          {providers.map(provider => (
            <option key={provider.id} value={provider.id}>
              {provider.name} ({provider.type})
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="model_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Model Name *
        </label>
        <input
          id="model_name"
          name="model_name"
          type="text"
          required
          value={formData.model_name}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-700"
          placeholder="Example: gpt-3.5-turbo"
        />
      </div>

      <div>
        <label htmlFor="capability" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Capability *
        </label>
        <select
          id="capability"
          name="capability"
          required
          value={formData.capability}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-700"
        >
          <option value="chat">Chat</option>
          <option value="embedding">Embedding</option>
          <option value="completion">Completion</option>
        </select>
      </div>

      <div>
        <label htmlFor="params" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Parameters (JSON format)
        </label>
        <textarea
          id="params"
          name="params"
          rows={6}
          onChange={handleParamsChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-700"
          placeholder='Example: {"temperature": 0.7, "max_tokens": 1000}'
        />
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Enter model parameters in JSON format
        </p>
      </div>

      <div className="flex justify-end">
        <Button
          type="button"
          variant="outline"
          className="mr-4"
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