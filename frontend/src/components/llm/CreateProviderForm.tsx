'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/base/Button';
import { Input } from '@/components/base/Input';
import { Select } from '@/components/base/Select';
import { FormField } from '@/components/base/FormField';
import { LLMProviderCreate } from '@/types/llm';
import { createProvider } from '@/api/llm';
import { ModelIcon } from '@/components/llm/ModelIcon';

export function CreateProviderForm() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<LLMProviderCreate>({
    name: '',
    type: 'openai',
    api_key: '',
    models: [],
  });
  const [error, setError] = useState<string | null>(null);

  // Update name automatically based on provider type
  useEffect(() => {
    if (!formData.name || formData.name === 'OpenAI' || formData.name === 'Anthropic' || 
        formData.name === 'Mistral AI' || formData.name === 'Google AI') {
      const providerOption = providerOptions.find(p => p.value === formData.type);
      if (providerOption) {
        setFormData(prev => ({
          ...prev,
          name: providerOption.label
        }));
      }
    }
  }, [formData.type]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleProviderChange = (value: string) => {
    setFormData(prevData => ({
      ...prevData,
      type: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    try {
      setIsLoading(true);
      await createProvider(formData);
      router.push('/llm');
      router.refresh();
    } catch (error) {
      console.error('Error creating provider:', error);
      setError('Failed to create provider. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const providerOptions = [
    { value: 'openai', label: 'OpenAI', keyFormat: 'sk-...', docLink: 'https://platform.openai.com/account/api-keys' },
    { value: 'anthropic', label: 'Anthropic', keyFormat: 'sk-ant-...', docLink: 'https://console.anthropic.com/keys' },
    { value: 'google', label: 'Google AI', keyFormat: 'AIza...', docLink: 'https://ai.google.dev/' },
    { value: 'mistral', label: 'Mistral AI', keyFormat: 'MISTRAL_API_KEY', docLink: 'https://docs.mistral.ai/' },
    { value: 'huggingface', label: 'Hugging Face', keyFormat: 'hf_...', docLink: 'https://huggingface.co/settings/tokens' },
    { value: 'cohere', label: 'Cohere', keyFormat: 'COHERE_API_KEY', docLink: 'https://dashboard.cohere.com/api-keys' },
    { value: 'deepseek', label: 'DeepSeek', keyFormat: 'DEEPSEEK_API_KEY', docLink: 'https://platform.deepseek.com/' },
  ];

  const selectOptions = providerOptions.map(option => ({
    value: option.value,
    label: option.label
  }));

  const selectedProvider = providerOptions.find(p => p.value === formData.type) || providerOptions[0];

  // Custom Provider Select with Icons
  const ProviderSelect = () => {
    return (
      <div className="relative">
        <select
          id="type"
          name="type"
          required
          value={formData.type}
          onChange={handleChange}
          className="block w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 pl-12 pr-4 py-3 text-lg text-left shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          {providerOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
          <ModelIcon type={formData.type} size="md" withBackground={true} />
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
        <h3 className="text-2xl font-medium mb-6">Provider Information</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
          <div>
            <label htmlFor="type" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
              Provider Type <span className="text-red-500">*</span>
            </label>
            <ProviderSelect />
          </div>

          <div>
            <label htmlFor="name" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
              Display Name <span className="text-red-500">*</span>
            </label>
            <Input
              id="name"
              name="name"
              type="text"
              required
              value={formData.name}
              onChange={handleChange}
              placeholder="My OpenAI Account"
              className="py-3 text-lg"
            />
          </div>
        </div>
        
        <div className="mt-6">
          <div>
            <label htmlFor="api_key" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
              API Key <span className="text-red-500">*</span>
            </label>
            <Input
              id="api_key"
              name="api_key"
              type="password"
              required
              value={formData.api_key}
              onChange={handleChange}
              placeholder={selectedProvider.keyFormat}
              className="py-3 text-lg"
            />
            <div className="mt-2 flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              <p>Format: {selectedProvider.keyFormat}</p>
              <a 
                href={selectedProvider.docLink} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300"
              >
                Get API Key
              </a>
            </div>
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
          {isLoading ? 'Creating...' : 'Create Provider'}
        </Button>
      </div>
    </form>
  );
} 