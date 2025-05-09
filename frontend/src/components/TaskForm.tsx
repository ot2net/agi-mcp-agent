'use client';

import { useState } from 'react';
import { Task } from '@/types/task';

interface TaskFormProps {
  onSubmit: (task: Omit<Task, 'id' | 'status' | 'created_at' | 'completed_at' | 'result' | 'error'>) => void;
}

export function TaskForm({ onSubmit }: TaskFormProps) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    model_identifier: 'openai:gpt-3.5-turbo',
    prompt: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
    setFormData({
      name: '',
      description: '',
      model_identifier: 'openai:gpt-3.5-turbo',
      prompt: '',
    });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700">
          Task Name
        </label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
          Description
        </label>
        <input
          type="text"
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label htmlFor="model_identifier" className="block text-sm font-medium text-gray-700">
          Model
        </label>
        <select
          id="model_identifier"
          name="model_identifier"
          value={formData.model_identifier}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        >
          <option value="openai:gpt-3.5-turbo">GPT-3.5 Turbo</option>
          <option value="openai:gpt-4">GPT-4</option>
          <option value="anthropic:claude-3-opus">Claude 3 Opus</option>
          <option value="anthropic:claude-3-sonnet">Claude 3 Sonnet</option>
          <option value="google:gemini-pro">Gemini Pro</option>
          <option value="mistral:mistral-large">Mistral Large</option>
        </select>
      </div>

      <div>
        <label htmlFor="prompt" className="block text-sm font-medium text-gray-700">
          Prompt
        </label>
        <textarea
          id="prompt"
          name="prompt"
          value={formData.prompt}
          onChange={handleChange}
          required
          rows={4}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <button
        type="submit"
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        Create Task
      </button>
    </form>
  );
} 