'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/base/Button';
import { LLMProviderCreate } from '@/types/llm';
import { createProvider } from '@/api/llm';

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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleModelsChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    // Split models by comma or newline
    const modelsList = e.target.value
      .split(/[,\n]/)
      .map(model => model.trim())
      .filter(model => model !== '');
    
    setFormData(prevData => ({
      ...prevData,
      models: modelsList,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    try {
      setIsLoading(true);
      await createProvider(formData);
      router.push('/llm/providers');
      router.refresh();
    } catch (error) {
      console.error('Error creating provider:', error);
      setError('Failed to create provider. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800">
          <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}
      
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Name *
        </label>
        <input
          id="name"
          name="name"
          type="text"
          required
          value={formData.name}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-700"
          placeholder="Example: OpenAI"
        />
      </div>

      <div>
        <label htmlFor="type" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Type *
        </label>
        <select
          id="type"
          name="type"
          required
          value={formData.type}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-700"
        >
          <option value="openai">OpenAI</option>
          <option value="anthropic">Anthropic</option>
          <option value="google">Google</option>
          <option value="mistral">Mistral</option>
          <option value="huggingface">Hugging Face</option>
          <option value="llama">Llama</option>
          <option value="cohere">Cohere</option>
          <option value="deepseek">DeepSeek</option>
          <option value="qwen">Qwen</option>
          <option value="rest">REST API</option>
        </select>
      </div>

      <div>
        <label htmlFor="api_key" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          API Key
        </label>
        <input
          id="api_key"
          name="api_key"
          type="password"
          value={formData.api_key || ''}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-700"
          placeholder="Example: sk-xxxx"
        />
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          The API key entered here will be securely stored
        </p>
      </div>

      <div>
        <label htmlFor="models" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Supported Models
        </label>
        <textarea
          id="models"
          name="models"
          rows={4}
          onChange={handleModelsChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-700"
          placeholder="One model name per line, or separate with commas"
        />
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
          {isLoading ? 'Creating...' : 'Create Provider'}
        </Button>
      </div>
    </form>
  );
} 