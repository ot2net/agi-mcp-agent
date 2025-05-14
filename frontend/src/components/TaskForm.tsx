'use client';

import { useState } from 'react';
import { Task } from '@/types/task';
import { Input } from '@/components/base/Input';
import { TextArea } from '@/components/base/TextArea';
import { Button } from '@/components/base/Button';
import { FormField } from '@/components/base/FormField';
import { FancySelect } from '@/components/base/FancySelect';
import { ModelIcon } from '@/components/llm/ModelIcon';

interface TaskFormProps {
  onSubmit: (task: Omit<Task, 'id' | 'status' | 'created_at' | 'completed_at' | 'result' | 'error'>) => void;
}

// Group models by provider for better organization
const modelOptions = [
  // OpenAI
  { 
    value: 'openai:gpt-4o', 
    label: 'GPT-4o', 
    icon: <ModelIcon type="openai" size="sm" withBackground={true} />,
    group: 'OpenAI'
  },
  { 
    value: 'openai:gpt-4', 
    label: 'GPT-4', 
    icon: <ModelIcon type="openai" size="sm" withBackground={true} />,
    group: 'OpenAI'
  },
  { 
    value: 'openai:gpt-3.5-turbo', 
    label: 'GPT-3.5 Turbo', 
    icon: <ModelIcon type="openai" size="sm" withBackground={true} />,
    group: 'OpenAI'
  },
  
  // Anthropic
  { 
    value: 'anthropic:claude-3-opus', 
    label: 'Claude 3 Opus', 
    icon: <ModelIcon type="claude" size="sm" withBackground={true} />,
    group: 'Anthropic'
  },
  { 
    value: 'anthropic:claude-3-sonnet', 
    label: 'Claude 3 Sonnet', 
    icon: <ModelIcon type="claude" size="sm" withBackground={true} />,
    group: 'Anthropic'
  },
  { 
    value: 'anthropic:claude-3-haiku', 
    label: 'Claude 3 Haiku', 
    icon: <ModelIcon type="claude" size="sm" withBackground={true} />,
    group: 'Anthropic'
  },
  
  // Google
  { 
    value: 'google:gemini-pro', 
    label: 'Gemini Pro', 
    icon: <ModelIcon type="gemini" size="sm" withBackground={true} />,
    group: 'Google'
  },
  { 
    value: 'google:gemini-ultra', 
    label: 'Gemini Ultra', 
    icon: <ModelIcon type="gemini" size="sm" withBackground={true} />,
    group: 'Google'
  },
  
  // Mistral
  { 
    value: 'mistral:mistral-large', 
    label: 'Mistral Large', 
    icon: <ModelIcon type="mistral" size="sm" withBackground={true} />,
    group: 'Mistral AI'
  },
  { 
    value: 'mistral:mistral-medium', 
    label: 'Mistral Medium', 
    icon: <ModelIcon type="mistral" size="sm" withBackground={true} />,
    group: 'Mistral AI'
  },
  
  // Other providers
  { 
    value: 'cohere:command', 
    label: 'Command', 
    icon: <ModelIcon type="cohere" size="sm" withBackground={true} />,
    group: 'Other Providers'
  },
  { 
    value: 'deepseek:deepseek-coder', 
    label: 'DeepSeek Coder', 
    icon: <ModelIcon type="deepseek" size="sm" withBackground={true} />,
    group: 'Other Providers'
  },
  { 
    value: 'huggingface:llama-3', 
    label: 'Llama 3', 
    icon: <ModelIcon type="huggingface" size="sm" withBackground={true} />,
    group: 'Other Providers'
  },
  { 
    value: 'qwen:qwen-max', 
    label: 'Qwen Max', 
    icon: <ModelIcon type="qwen" size="sm" withBackground={true} />,
    group: 'Other Providers'
  }
];

// Group the models for display
const groupedModelOptions = modelOptions.reduce((acc: any[], option) => {
  const groupIndex = acc.findIndex(group => group.label === option.group);
  
  if (groupIndex === -1) {
    // Create a new group
    acc.push({
      label: option.group,
      options: [option]
    });
  } else {
    // Add to existing group
    acc[groupIndex].options.push(option);
  }
  
  return acc;
}, []);

export function TaskForm({ onSubmit }: TaskFormProps) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    model_identifier: 'openai:gpt-4', // Default to GPT-4
    prompt: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
    setFormData({
      name: '',
      description: '',
      model_identifier: 'openai:gpt-4',
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

  // Get the selected model details
  const selectedModel = modelOptions.find(model => model.value === formData.model_identifier);

  return (
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
        label="Select Model"
        required
        helperText={selectedModel ? `Using ${selectedModel.group} - ${selectedModel.label}` : ''}
      >
        <FancySelect
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
  );
} 