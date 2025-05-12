'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/base/Button';
import { Input } from '@/components/base/Input';
import { LLMProvider } from '@/types/llm';
import { HiLockClosed, HiOutlineExternalLink } from 'react-icons/hi';
import { ModelIcon } from '@/components/llm/ModelIcon';

interface ApiKeyConfigProps {
  provider: LLMProvider;
  isOpen: boolean;
  onClose: () => void;
  onSave: (apiKey: string, metadata: Record<string, any>) => Promise<void>;
}

// 各提供商的API Key格式提示和文档链接
const providerConfig: Record<string, {
  keyFormat: string;
  docLink: string;
  hasOrgId: boolean;
  hasBaseUrl: boolean;
  apiBaseDefault?: string;
}> = {
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

export function ApiKeyConfig({ provider, isOpen, onClose, onSave }: ApiKeyConfigProps) {
  const [apiKey, setApiKey] = useState('');
  const [orgId, setOrgId] = useState('');
  const [baseUrl, setBaseUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [formValid, setFormValid] = useState(false);

  // 初始化表单
  useEffect(() => {
    if (isOpen && provider) {
      // 从provider.metadata中获取已保存的值（如果有）
      const metadata = provider.metadata || {};
      setOrgId(metadata.org_id || '');
      setBaseUrl(metadata.base_url || '');
      setApiKey('');  // API密钥总是需要重新输入
      setError('');
    }
  }, [isOpen, provider]);

  // 验证表单
  useEffect(() => {
    const config = getProviderConfig();
    const isValid = apiKey.trim() !== '' && 
                   (!config.hasOrgId || orgId.trim() !== '') &&
                   (!config.hasBaseUrl || baseUrl.trim() !== '');
    setFormValid(isValid);
  }, [apiKey, orgId, baseUrl]);

  // 获取当前供应商的配置
  const getProviderConfig = () => {
    const providerType = provider?.type.toLowerCase() || '';
    // 直接匹配
    for (const [key, config] of Object.entries(providerConfig)) {
      if (providerType === key || providerType.includes(key)) {
        return config;
      }
    }
    // 默认返回OpenAI配置
    return providerConfig.openai;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formValid) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      setIsLoading(true);
      setError('');

      // 准备metadata
      const metadata: Record<string, any> = { ...provider.metadata };
      if (orgId) {
        metadata.org_id = orgId;
      }
      if (baseUrl) {
        metadata.base_url = baseUrl;
      }

      await onSave(apiKey, metadata);
      onClose();
    } catch (err) {
      console.error('Error saving API key:', err);
      setError('Failed to save API key. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const config = getProviderConfig();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full">
        <div className="border-b border-gray-200 dark:border-gray-700 p-4 flex items-center">
          <ModelIcon type={provider.type} size="md" withBackground={true} className="mr-3" />
          <h3 className="text-xl font-semibold">
            Configure {provider.name}
          </h3>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          {error && (
            <div className="p-3 mb-4 rounded-md bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800">
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          <div className="space-y-5">
            <div>
              <label htmlFor="api_key" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
                API Key <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Input
                  id="api_key"
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  required
                  placeholder={config.keyFormat}
                  className="pl-10"
                />
                <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                  <HiLockClosed className="text-gray-400" />
                </div>
              </div>
              <div className="mt-1 text-sm">
                <a 
                  href={config.docLink} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-blue-600 hover:text-blue-800"
                >
                  Get API Key
                  <HiOutlineExternalLink className="ml-1" />
                </a>
              </div>
            </div>

            {config.hasOrgId && (
              <div>
                <label htmlFor="org_id" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
                  Organization ID <span className="text-red-500">*</span>
                </label>
                <Input
                  id="org_id"
                  type="text"
                  value={orgId}
                  onChange={(e) => setOrgId(e.target.value)}
                  required={config.hasOrgId}
                  placeholder="org-..."
                />
              </div>
            )}

            {config.hasBaseUrl && (
              <div>
                <label htmlFor="base_url" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
                  API Base URL <span className="text-red-500">*</span>
                </label>
                <Input
                  id="base_url"
                  type="text"
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                  required={config.hasBaseUrl}
                  placeholder={config.apiBaseDefault}
                />
                <p className="mt-1 text-sm text-gray-500">
                  {baseUrl ? 'Custom API endpoint' : 'Default API endpoint will be used'}
                </p>
              </div>
            )}

            <div className="pt-2 text-sm">
              <p className="flex items-center text-gray-500">
                <HiLockClosed className="mr-1 text-gray-400" />
                Your API key is securely encrypted before storage
              </p>
            </div>
          </div>

          <div className="mt-6 border-t border-gray-200 dark:border-gray-700 pt-4 flex justify-end space-x-3">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isLoading || !formValid}
            >
              {isLoading ? 'Saving...' : 'Save'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
} 