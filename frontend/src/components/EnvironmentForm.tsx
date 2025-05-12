'use client';

import { useState } from 'react';
import { Environment } from '@/types/environment';
import { Card } from '@/components/base/Card';
import { Input } from '@/components/base/Input';
import { Select } from '@/components/base/Select';
import { TextArea } from '@/components/base/TextArea';
import { Button } from '@/components/base/Button';
import { FormField } from '@/components/base/FormField';
import { HiOutlinePlus } from 'react-icons/hi';
import { FancySelect } from '@/components/base/FancySelect';

interface EnvironmentFormProps {
  onSubmit: (env: Omit<Environment, 'id' | 'status' | 'created_at' | 'updated_at'>) => void;
}

const ENV_TYPE_OPTIONS = [
  { value: 'api', label: 'API', icon: <span>🌐</span> },
  { value: 'filesystem', label: 'Filesystem', icon: <span>📁</span> },
  { value: 'memory', label: 'Memory', icon: <span>💾</span> },
  { value: 'web', label: 'Web', icon: <span>🌍</span> },
  { value: 'database', label: 'Database', icon: <span>🗄️</span> },
  { value: 'mcp', label: 'MCP', icon: <span>🔧</span> },
];

export function EnvironmentForm({ onSubmit }: EnvironmentFormProps) {
  const [formData, setFormData] = useState({
    name: '',
    type: 'api',
    config: '{}',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const configJson = JSON.parse(formData.config);
      onSubmit({
        name: formData.name,
        type: formData.type,
        config: configJson,
      });
      setFormData({
        name: '',
        type: 'api',
        config: '{}',
      });
    } catch (err) {
      console.error('Invalid JSON in config:', err);
    }
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
    <form onSubmit={handleSubmit} className="space-y-6">
      <FormField
        id="name"
        label="Environment Name"
        required
      >
        <Input
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          placeholder="Enter environment name"
          required
        />
      </FormField>

      <FormField
        id="type"
        label="Type"
        required
      >
        <FancySelect
          id="type"
          name="type"
          value={formData.type}
          onChange={handleChange}
          options={ENV_TYPE_OPTIONS}
        />
      </FormField>

      <FormField
        id="config"
        label="Configuration (JSON)"
        required
        helperText="Enter the environment configuration in JSON format"
      >
        <TextArea
          id="config"
          name="config"
          value={formData.config}
          onChange={handleChange}
          placeholder='{"key": "value"}'
          required
          rows={4}
        />
      </FormField>

      <div className="flex justify-end">
        <Button type="submit" icon={<HiOutlinePlus className="w-5 h-5" />}>
          Create Environment
        </Button>
      </div>
    </form>
  );
} 