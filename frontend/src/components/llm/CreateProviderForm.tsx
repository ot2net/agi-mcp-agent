'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@/components/base/Button';
import { Input } from '@/components/base/Input';
import { Select } from '@/components/base/Select';
import { FormField } from '@/components/base/FormField';
import { LLMProviderCreate } from '@/types/llm';
import { createProvider } from '@/api/llm';
import { ModelIcon } from '@/components/llm/ModelIcon';
import Link from 'next/link';
import { HiArrowLeft, HiLockClosed, HiOutlineExternalLink } from 'react-icons/hi';

// 各提供商的API Key格式提示和文档链接
const providerConfig = {
  'openai': { 
    keyFormat: 'sk-...', 
    docLink: 'https://platform.openai.com/account/api-keys',
    hasOrgId: true,
    hasBaseUrl: true,
    apiBaseDefault: 'https://api.openai.com'
  },
  'anthropic': { 
    keyFormat: 'sk-ant-...', 
    docLink: 'https://console.anthropic.com/keys',
    hasOrgId: false,
    hasBaseUrl: true,
    apiBaseDefault: 'https://api.anthropic.com'
  },
  'google': { 
    keyFormat: 'AIza...', 
    docLink: 'https://ai.google.dev/',
    hasOrgId: false,
    hasBaseUrl: false
  },
  'mistral': { 
    keyFormat: 'MISTRAL_API_KEY', 
    docLink: 'https://docs.mistral.ai/',
    hasOrgId: false,
    hasBaseUrl: true,
    apiBaseDefault: 'https://api.mistral.ai'
  },
  'huggingface': { 
    keyFormat: 'hf_...', 
    docLink: 'https://huggingface.co/settings/tokens',
    hasOrgId: false,
    hasBaseUrl: false
  },
  'cohere': { 
    keyFormat: 'COHERE_API_KEY', 
    docLink: 'https://dashboard.cohere.com/api-keys',
    hasOrgId: false,
    hasBaseUrl: false
  },
  'deepseek': { 
    keyFormat: 'DEEPSEEK_API_KEY', 
    docLink: 'https://platform.deepseek.com/',
    hasOrgId: false,
    hasBaseUrl: false
  },
  'minimax': { 
    keyFormat: 'MINIMAX_API_KEY',
    docLink: 'https://api.minimax.chat/',
    hasOrgId: true,
    hasBaseUrl: false
  }
};

export function CreateProviderForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<LLMProviderCreate & { org_id?: string, base_url?: string }>({
    name: '',
    type: 'openai',
    api_key: '',
    org_id: '',
    base_url: '',
    models: [],
    metadata: {}
  });
  const [error, setError] = useState<string | null>(null);
  const [formValid, setFormValid] = useState(false);
  
  // 从URL获取预选的provider类型
  useEffect(() => {
    const typeParam = searchParams?.get('type');
    if (typeParam && Object.keys(providerConfig).includes(typeParam)) {
      setFormData(prev => ({
        ...prev,
        type: typeParam,
        name: typeParam.charAt(0).toUpperCase() + typeParam.slice(1)
      }));
      
      // 设置默认baseUrl
      if (providerConfig[typeParam as keyof typeof providerConfig]?.hasBaseUrl) {
        setFormData(prev => ({
          ...prev,
          base_url: providerConfig[typeParam as keyof typeof providerConfig]?.apiBaseDefault || ''
        }));
      }
    }
  }, [searchParams]);

  // 更新表单验证状态
  useEffect(() => {
    const isValid = formData.name.trim() !== '' && 
                   formData.api_key.trim() !== '' && 
                   (!providerConfig[formData.type as keyof typeof providerConfig]?.hasOrgId || 
                    (formData.org_id && formData.org_id.trim() !== '')) &&
                   (!providerConfig[formData.type as keyof typeof providerConfig]?.hasBaseUrl || 
                    (formData.base_url && formData.base_url.trim() !== ''));
    setFormValid(isValid);
  }, [formData]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleProviderTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const { value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      type: value,
      name: value.charAt(0).toUpperCase() + value.slice(1),
      // 重置组织ID和基础URL
      org_id: '',
      base_url: providerConfig[value as keyof typeof providerConfig]?.apiBaseDefault || '',
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    if (!formValid) {
      setError('Please fill in all required fields.');
      return;
    }
    
    try {
      setIsLoading(true);
      
      // 将额外字段添加到metadata中
      const metadata: Record<string, any> = { ...formData.metadata };
      if (formData.org_id) {
        metadata.org_id = formData.org_id;
      }
      if (formData.base_url) {
        metadata.base_url = formData.base_url;
      }
      
      // 准备提交的数据
      const submitData = {
        name: formData.name,
        type: formData.type,
        api_key: formData.api_key,
        models: formData.models,
        metadata
      };
      
      await createProvider(submitData);
      router.push('/llm');
      router.refresh();
    } catch (error) {
      console.error('Error creating provider:', error);
      setError('Failed to create provider. Please check your API key and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const providerOptions = Object.keys(providerConfig).map(key => ({
    value: key,
    label: key.charAt(0).toUpperCase() + key.slice(1)
  }));

  // 获取当前选中的提供商配置
  const selectedProviderConfig = providerConfig[formData.type as keyof typeof providerConfig] || providerConfig.openai;

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6">
        <Link href="/llm" className="inline-flex items-center text-gray-600 hover:text-gray-900">
          <HiArrowLeft className="mr-2" />
          <span>Back to Models</span>
        </Link>
      </div>
      
      <div className="mb-6">
        <h1 className="text-2xl font-bold flex items-center">
          <ModelIcon type={formData.type} size="lg" withBackground={true} className="mr-3" />
          <span>Add {formData.type.charAt(0).toUpperCase() + formData.type.slice(1)}</span>
        </h1>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800">
            <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
          </div>
        )}
        
        <div className="bg-white dark:bg-gray-800 p-8 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="space-y-6">
            <div>
              <label htmlFor="type" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
                Provider Type <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <select
                  id="type"
                  name="type"
                  required
                  value={formData.type}
                  onChange={handleProviderTypeChange}
                  className="block w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 pl-12 pr-4 py-3 text-lg shadow-sm focus:border-blue-500 focus:ring-blue-500"
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
            </div>

            <div>
              <label htmlFor="api_key" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
                API Key <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Input
                  id="api_key"
                  name="api_key"
                  type="password"
                  required
                  value={formData.api_key}
                  onChange={handleChange}
                  placeholder={selectedProviderConfig.keyFormat}
                  className="py-3 text-lg pl-10"
                />
                <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                  <HiLockClosed className="text-gray-400" />
                </div>
              </div>
              <div className="mt-2 flex items-center text-sm text-gray-500">
                <a 
                  href={selectedProviderConfig.docLink} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-blue-600 hover:text-blue-800"
                >
                  Get API Key
                  <HiOutlineExternalLink className="ml-1" />
                </a>
              </div>
            </div>

            {selectedProviderConfig.hasOrgId && (
              <div>
                <label htmlFor="org_id" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
                  Organization ID <span className="text-red-500">*</span>
                </label>
                <Input
                  id="org_id"
                  name="org_id"
                  type="text"
                  required={selectedProviderConfig.hasOrgId}
                  value={formData.org_id}
                  onChange={handleChange}
                  placeholder="org-..."
                  className="py-3 text-lg"
                />
                <p className="mt-1 text-sm text-gray-500">
                  Your Organization ID is required for API requests.
                </p>
              </div>
            )}

            {selectedProviderConfig.hasBaseUrl && (
              <div>
                <label htmlFor="base_url" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
                  API Base URL {selectedProviderConfig.hasBaseUrl && <span className="text-red-500">*</span>}
                </label>
                <Input
                  id="base_url"
                  name="base_url"
                  type="text"
                  required={selectedProviderConfig.hasBaseUrl}
                  value={formData.base_url}
                  onChange={handleChange}
                  placeholder={selectedProviderConfig.apiBaseDefault}
                  className="py-3 text-lg"
                />
                <p className="mt-1 text-sm text-gray-500">
                  {formData.base_url ? 'Custom API endpoint' : 'Default API endpoint will be used'}
                </p>
              </div>
            )}

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
                placeholder="My Provider"
                className="py-3 text-lg"
              />
            </div>
            
            <div className="pt-4 text-sm">
              <p className="flex items-center text-gray-500">
                <HiLockClosed className="mr-1 text-gray-400" />
                Your API key is securely encrypted before storage
              </p>
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
            disabled={isLoading || !formValid}
            className="px-6"
          >
            {isLoading ? 'Adding...' : 'Add Provider'}
          </Button>
        </div>
      </form>
    </div>
  );
} 