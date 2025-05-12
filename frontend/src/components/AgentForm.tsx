'use client';

import { useState } from 'react';
import { Agent } from '@/types/agent';
import { Button } from '@/components/base/Button';
import { HiOutlineSave } from 'react-icons/hi';

interface AgentFormProps {
  onSubmit: (agent: Omit<Agent, 'id' | 'created_at' | 'updated_at'>) => Promise<void>;
  initialAgent?: Partial<Agent>;
}

export function AgentForm({ onSubmit, initialAgent }: AgentFormProps) {
  const [formData, setFormData] = useState<Partial<Agent>>({
    name: initialAgent?.name || '',
    type: initialAgent?.type || '',
    capabilities: initialAgent?.capabilities || {},
    status: initialAgent?.status || 'active',
    metadata: initialAgent?.metadata || {},
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleCapabilitiesChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    try {
      const capabilities = JSON.parse(e.target.value);
      setFormData(prev => ({ ...prev, capabilities }));
      setError(null);
    } catch (err) {
      setError('Invalid JSON for capabilities');
    }
  };

  const handleMetadataChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    try {
      const metadata = JSON.parse(e.target.value);
      setFormData(prev => ({ ...prev, metadata }));
      setError(null);
    } catch (err) {
      setError('Invalid JSON for metadata');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name || !formData.type) {
      setError('Name and type are required');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      await onSubmit(formData as Omit<Agent, 'id' | 'created_at' | 'updated_at'>);
      // Reset form after successful submission
      setFormData({
        name: '',
        type: '',
        capabilities: {},
        status: 'active',
        metadata: {},
      });
    } catch (err) {
      setError('Failed to submit agent');
      console.error('Error submitting agent:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800">
          <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}

      <div>
        <label htmlFor="name" className="block text-sm font-medium">
          Name
        </label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name || ''}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
      </div>

      <div>
        <label htmlFor="type" className="block text-sm font-medium">
          Type
        </label>
        <input
          type="text"
          id="type"
          name="type"
          value={formData.type || ''}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
      </div>

      <div>
        <label htmlFor="status" className="block text-sm font-medium">
          Status
        </label>
        <select
          id="status"
          name="status"
          value={formData.status || 'active'}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="error">Error</option>
        </select>
      </div>

      <div>
        <label htmlFor="capabilities" className="block text-sm font-medium">
          Capabilities (JSON)
        </label>
        <textarea
          id="capabilities"
          name="capabilities"
          value={JSON.stringify(formData.capabilities, null, 2)}
          onChange={handleCapabilitiesChange}
          rows={5}
          className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label htmlFor="metadata" className="block text-sm font-medium">
          Metadata (JSON)
        </label>
        <textarea
          id="metadata"
          name="metadata"
          value={JSON.stringify(formData.metadata, null, 2)}
          onChange={handleMetadataChange}
          rows={5}
          className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <Button
        type="submit"
        disabled={isLoading}
        className="w-full"
        icon={<HiOutlineSave className="w-5 h-5" />}
      >
        {isLoading ? 'Saving...' : 'Save Agent'}
      </Button>
    </form>
  );
} 