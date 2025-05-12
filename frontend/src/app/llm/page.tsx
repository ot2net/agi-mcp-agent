'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { HiOutlinePlus, HiOutlineChip, HiOutlineCog, HiOutlineCube, HiSearch, HiOutlinePencil } from 'react-icons/hi';
import { Button } from '@/components/base/Button';
import { getProviders, getModels, getProviderModels, updateProviderApiKey } from '@/api/llm';
import { LLMProvider, LLMModel } from '@/types/llm';
import { ModelIcon } from '@/components/llm/ModelIcon';
import { Input } from '@/components/base/Input';
import { ApiKeyConfig } from '@/components/llm/ApiKeyConfig';

// 定义模型的能力类型
type ModelCapability = 'LLM' | 'TEXT EMBEDDING' | 'SPEECH2TEXT' | 'TTS' | 'MODERATION' | 'RERANK';

// 定义模型的能力与UI标签的映射
const capabilityLabels: Record<string, { label: string, bgColor: string, textColor: string }> = {
  'chat': { 
    label: 'LLM', 
    bgColor: 'bg-gray-100 dark:bg-gray-700', 
    textColor: 'text-gray-700 dark:text-gray-300' 
  },
  'embedding': { 
    label: 'TEXT EMBEDDING', 
    bgColor: 'bg-blue-100 dark:bg-blue-900/20', 
    textColor: 'text-blue-700 dark:text-blue-300' 
  },
  'speech': { 
    label: 'SPEECH2TEXT', 
    bgColor: 'bg-green-100 dark:bg-green-900/20', 
    textColor: 'text-green-700 dark:text-green-300' 
  },
  'tts': { 
    label: 'TTS', 
    bgColor: 'bg-purple-100 dark:bg-purple-900/20', 
    textColor: 'text-purple-700 dark:text-purple-300' 
  },
  'moderation': { 
    label: 'MODERATION', 
    bgColor: 'bg-orange-100 dark:bg-orange-900/20', 
    textColor: 'text-orange-700 dark:text-orange-300' 
  },
  'rerank': { 
    label: 'RERANK', 
    bgColor: 'bg-pink-100 dark:bg-pink-900/20', 
    textColor: 'text-pink-700 dark:text-pink-300' 
  },
  'completion': { 
    label: 'LLM', 
    bgColor: 'bg-gray-100 dark:bg-gray-700', 
    textColor: 'text-gray-700 dark:text-gray-300' 
  }
};

// 定义提供商支持的能力
const providerCapabilities: Record<string, string[]> = {
  'openai': ['chat', 'embedding', 'moderation', 'tts'],
  'anthropic': ['chat'],
  'google': ['chat', 'embedding'],
  'mistral': ['chat'],
  'huggingface': ['chat', 'embedding'],
  'cohere': ['chat', 'embedding', 'rerank'],
  'deepseek': ['chat'],
  'minimax': ['chat', 'embedding'],
};

// 定义新的LLM整合页面
export default function LLMPage() {
  const [providers, setProviders] = useState<LLMProvider[]>([]);
  const [models, setModels] = useState<LLMModel[]>([]);
  const [providerModels, setProviderModels] = useState<Record<number, LLMModel[]>>({});
  const [expandedProviders, setExpandedProviders] = useState<Record<number, boolean>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedProvider, setSelectedProvider] = useState<LLMProvider | null>(null);
  const [isApiKeyModalOpen, setIsApiKeyModalOpen] = useState(false);

  // 获取数据
  const fetchData = async () => {
    try {
      setIsLoading(true);
      const [providersData, modelsData] = await Promise.all([
        getProviders(),
        getModels(),
      ]);
      setProviders(providersData);
      setModels(modelsData);

      // 为每个提供商获取模型
      const modelsByProvider: Record<number, LLMModel[]> = {};
      for (const provider of providersData) {
        try {
          const providerModels = await getProviderModels(provider.id);
          modelsByProvider[provider.id] = providerModels;
        } catch (error) {
          console.error(`Error fetching models for provider ${provider.id}:`, error);
          modelsByProvider[provider.id] = [];
        }
      }
      setProviderModels(modelsByProvider);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to fetch data. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // 切换模型展示
  const toggleProviderExpanded = (providerId: number) => {
    setExpandedProviders(prev => ({
      ...prev,
      [providerId]: !prev[providerId]
    }));
  };

  // 打开API Key配置模态框
  const openApiKeyModal = (provider: LLMProvider) => {
    setSelectedProvider(provider);
    setIsApiKeyModalOpen(true);
  };

  // 保存API Key
  const handleSaveApiKey = async (apiKey: string, metadata: Record<string, any>) => {
    if (!selectedProvider) return;
    
    try {
      await updateProviderApiKey(selectedProvider.id, apiKey, metadata);
      // 刷新数据
      fetchData();
    } catch (error) {
      console.error('Error saving API key:', error);
      throw error; // 让ApiKeyConfig组件可以捕获错误
    }
  };

  // 过滤提供商
  const filteredProviders = providers.filter(provider => 
    provider.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    provider.type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // 计数已配置和未配置的提供商
  const configuredProviders = providers.filter(p => p.status === 'enabled');
  const pendingProviders = providers.filter(p => p.status !== 'enabled');

  // 获取提供商支持的能力
  const getProviderCapabilities = (providerType: string): string[] => {
    const type = providerType.toLowerCase();
    // 尝试直接匹配
    if (providerCapabilities[type]) {
      return providerCapabilities[type];
    }
    
    // 尝试部分匹配
    for (const [key, capabilities] of Object.entries(providerCapabilities)) {
      if (type.includes(key)) {
        return capabilities;
      }
    }
    
    return ['chat'];  // 默认至少支持聊天
  };

  // 可用的模型图标
  const availableProviders = ['openai', 'anthropic', 'google', 'deepseek', 'qwen', 'mistral', 'huggingface', 'cohere', 'minimax'];

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="flex flex-col space-y-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <h1 className="text-2xl font-bold">LLM Management</h1>
          <div className="w-full md:w-auto flex flex-col md:flex-row gap-3">
            <div className="relative">
              <Input
                type="search"
                placeholder="Search providers..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
              <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <HiSearch className="text-gray-400" />
              </div>
            </div>
            <Button 
              className="flex items-center"
              onClick={() => {
                const dialog = document.getElementById('add-provider-modal') as HTMLDialogElement;
                if (dialog) dialog.showModal();
              }}
            >
              <HiOutlinePlus className="mr-2" />
              Add Provider
            </Button>
          </div>
        </div>

        {/* 系统模型设置按钮 */}
        <div className="flex justify-end">
          <Button
            variant="outline"
            size="sm"
            className="flex items-center text-sm"
          >
            <HiOutlineCog className="mr-2" />
            System Model Settings
          </Button>
        </div>

        {isLoading ? (
          <div className="text-center py-12">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-500 border-r-transparent" role="status">
              <span className="sr-only">Loading...</span>
            </div>
            <p className="mt-4 text-gray-600">Loading...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 p-4 rounded-md">
            <p className="text-red-800 dark:text-red-200">{error}</p>
          </div>
        ) : (
          <div className="space-y-8">
            {/* 模型列表 */}
            <div>
              <h2 className="text-xl font-semibold mb-4">Model List</h2>
              
              {filteredProviders.length > 0 ? (
                <div className="space-y-4">
                  {filteredProviders.map((provider) => (
                    <div key={provider.id} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
                      <div className="p-5">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                          <div className="flex items-center space-x-4">
                            <ModelIcon type={provider.type} size="lg" withBackground={true} />
                            <div>
                              <h3 className="text-lg font-semibold">{provider.name}</h3>
                              <div className="flex flex-wrap gap-2 mt-2">
                                {getProviderCapabilities(provider.type).map(capability => (
                                  <span 
                                    key={capability}
                                    className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium ${capabilityLabels[capability].bgColor} ${capabilityLabels[capability].textColor}`}
                                  >
                                    {capabilityLabels[capability].label}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </div>
                          
                          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
                            {/* 费用信息 */}
                            <div className="text-center px-4 py-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
                              <div className="text-sm text-gray-500 dark:text-gray-400">
                                Usage
                              </div>
                              <div className="font-semibold">
                                {provider.models_count > 0 ? `${provider.models_count} models` : '-'}
                              </div>
                            </div>
                            
                            {/* API Key 配置按钮 */}
                            <Button
                              variant="outline" 
                              size="sm"
                              className={`flex items-center ${provider.status !== 'enabled' ? 'border-red-300 text-red-500' : ''}`}
                              onClick={() => openApiKeyModal(provider)}
                            >
                              <span className="flex items-center">
                                API-KEY
                                {provider.status !== 'enabled' && (
                                  <span className="ml-1 h-2 w-2 rounded-full bg-red-500"></span>
                                )}
                              </span>
                              <HiOutlinePencil className="ml-2" />
                            </Button>
                          </div>
                        </div>
                        
                        {/* 模型展示按钮 */}
                        <div className="mt-4">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-blue-600 hover:text-blue-700 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 flex items-center"
                            onClick={() => toggleProviderExpanded(provider.id)}
                          >
                            {expandedProviders[provider.id] ? 'Hide Models' : 'Show Models'}
                            <svg 
                              className={`ml-1 h-4 w-4 transition-transform ${expandedProviders[provider.id] ? 'rotate-180' : ''}`} 
                              fill="none" 
                              viewBox="0 0 24 24" 
                              stroke="currentColor"
                            >
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                          </Button>
                        </div>
                      </div>
                      
                      {/* 展开的模型列表 */}
                      {expandedProviders[provider.id] && (
                        <div className="border-t border-gray-200 dark:border-gray-700 px-5 py-3 bg-gray-50 dark:bg-gray-800">
                          {providerModels[provider.id] && providerModels[provider.id].length > 0 ? (
                            <div className="space-y-3">
                              {providerModels[provider.id].map(model => (
                                <div 
                                  key={model.id}
                                  className="flex justify-between items-center p-3 bg-white dark:bg-gray-700 rounded-lg shadow-sm"
                                >
                                  <div className="flex items-center space-x-3">
                                    <ModelIcon type={provider.type} size="sm" withBackground={true} />
                                    <div>
                                      <p className="font-medium">{model.model_name}</p>
                                      <span 
                                        className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${capabilityLabels[model.capability]?.bgColor || 'bg-gray-100'} ${capabilityLabels[model.capability]?.textColor || 'text-gray-700'}`}
                                      >
                                        {capabilityLabels[model.capability]?.label || model.capability}
                                      </span>
                                    </div>
                                  </div>
                                  
                                  <div className="flex items-center space-x-2">
                                    <span className={`inline-flex h-2 w-2 rounded-full ${model.status === 'enabled' ? 'bg-green-500' : 'bg-red-500'}`}></span>
                                    <span className="text-sm">{model.status === 'enabled' ? 'Enabled' : 'Disabled'}</span>
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div className="text-center py-4">
                              <p className="text-gray-500 dark:text-gray-400">No models configured for this provider.</p>
                              <Button
                                size="sm"
                                variant="ghost"
                                className="mt-2 text-blue-600 hover:text-blue-700 dark:text-blue-400"
                                onClick={() => {
                                  // 创建新模型URL
                                  window.location.href = `/llm/models/create?provider=${provider.id}`;
                                }}
                              >
                                <HiOutlinePlus className="mr-1" />
                                Add Model
                              </Button>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-16 border border-dashed border-gray-300 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-900">
                  <HiOutlineCube className="mx-auto h-16 w-16 text-gray-400" />
                  <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-white">No providers found</h3>
                  <p className="mt-2 text-gray-500 dark:text-gray-400 max-w-sm mx-auto">
                    {searchTerm ? "No providers match your search criteria." : "Get started by adding a new LLM provider."}
                  </p>
                  {!searchTerm && (
                    <div className="mt-6">
                      <Button 
                        className="flex items-center mx-auto"
                        onClick={() => {
                          const dialog = document.getElementById('add-provider-modal') as HTMLDialogElement;
                          if (dialog) dialog.showModal();
                        }}
                      >
                        <HiOutlinePlus className="mr-1" />
                        Add Provider
                      </Button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Add Provider Dialog */}
      <dialog id="add-provider-modal" className="modal rounded-lg shadow-lg p-0 bg-white dark:bg-gray-800 max-w-lg w-full">
        <div className="border-b border-gray-200 dark:border-gray-700 p-4">
          <h3 className="text-xl font-semibold">Add a Provider</h3>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {availableProviders.map(provider => (
              <div 
                key={provider}
                className="text-center p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                onClick={() => {
                  // Close modal and navigate to provider setup
                  const dialog = document.getElementById('add-provider-modal') as HTMLDialogElement;
                  if (dialog) dialog.close();
                  window.location.href = `/llm/providers/create?type=${provider}`;
                }}
              >
                <ModelIcon type={provider} size="lg" withBackground={true} />
                <p className="mt-2 font-medium capitalize">{provider}</p>
              </div>
            ))}
          </div>
        </div>
        
        <div className="border-t border-gray-200 dark:border-gray-700 p-4 flex justify-end">
          <Button
            variant="outline"
            onClick={() => {
              const dialog = document.getElementById('add-provider-modal') as HTMLDialogElement;
              if (dialog) dialog.close();
            }}
          >
            Cancel
          </Button>
        </div>
      </dialog>

      {/* API Key Configuration Modal */}
      {selectedProvider && (
        <ApiKeyConfig
          provider={selectedProvider}
          isOpen={isApiKeyModalOpen}
          onClose={() => setIsApiKeyModalOpen(false)}
          onSave={handleSaveApiKey}
        />
      )}
    </div>
  );
} 