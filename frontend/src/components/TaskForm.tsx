'use client';

import { useState } from 'react';
import { Task } from '@/types/task';
import { Card } from '@/components/base/Card';
import { Input } from '@/components/base/Input';
import { Select } from '@/components/base/Select';
import { TextArea } from '@/components/base/TextArea';
import { Button } from '@/components/base/Button';
import { FormField } from '@/components/base/FormField';

interface TaskFormProps {
  onSubmit: (task: Omit<Task, 'id' | 'status' | 'created_at' | 'completed_at' | 'result' | 'error'>) => void;
}

const modelOptions = [
  { value: 'openai:gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
  { value: 'openai:gpt-4', label: 'GPT-4' },
  { value: 'anthropic:claude-3-opus', label: 'Claude 3 Opus' },
  { value: 'anthropic:claude-3-sonnet', label: 'Claude 3 Sonnet' },
  { value: 'google:gemini-pro', label: 'Gemini Pro' },
  { value: 'mistral:mistral-large', label: 'Mistral Large' },
];

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

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <Card title="Create New Task" description="Configure and create a new AI task">
      <form onSubmit={handleSubmit} className="space-y-6">
        <FormField
          id="name"
          label="Task Name"
          required
        >
          <Input
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Enter task name"
            required
          />
        </FormField>

        <FormField
          id="description"
          label="Description"
          required
        >
          <Input
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Enter task description"
            required
          />
        </FormField>

        <FormField
          id="model_identifier"
          label="Model"
          required
        >
          <Select
            id="model_identifier"
            name="model_identifier"
            value={formData.model_identifier}
            onChange={handleChange}
            options={modelOptions}
          />
        </FormField>

        <FormField
          id="prompt"
          label="Prompt"
          required
          helperText="Enter the instructions or prompt for the AI model"
        >
          <TextArea
            id="prompt"
            name="prompt"
            value={formData.prompt}
            onChange={handleChange}
            placeholder="Enter your prompt here..."
            required
            rows={4}
          />
        </FormField>

        <div className="flex justify-end">
          <Button type="submit">
            Create Task
          </Button>
        </div>
      </form>
    </Card>
  );
} 