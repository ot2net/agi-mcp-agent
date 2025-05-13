'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/base/Button';
import { Input } from '@/components/base/Input';
import { FormField } from '@/components/base/FormField';
import { LLMModelCreate, LLMProvider } from '@/types/llm';
import { createModel, getProviders } from '@/api/llm';
import { ModelIcon } from '@/components/llm/ModelIcon';
import { HiOutlineChevronDown, HiOutlineInformationCircle } from 'react-icons/hi';

// 各种模型能力的颜色映射
const capabilityColors: Record<string, { bgColor: string, textColor: string, label: string }> = {
  'chat': { 
    bgColor: 'bg-gray-100 dark:bg-gray-700', 
    textColor: 'text-gray-700 dark:text-gray-300',
    label: 'LLM'
  },
  'embedding': { 
    bgColor: 'bg-blue-100 dark:bg-blue-900/20', 
    textColor: 'text-blue-700 dark:text-blue-300',
    label: 'TEXT EMBEDDING'
  },
  'speech': { 
    bgColor: 'bg-green-100 dark:bg-green-900/20', 
    textColor: 'text-green-700 dark:text-green-300',
    label: 'SPEECH2TEXT'
  },
  'tts': { 
    bgColor: 'bg-purple-100 dark:bg-purple-900/20', 
    textColor: 'text-purple-700 dark:text-purple-300',
    label: 'TTS'
  },
  'moderation': { 
    bgColor: 'bg-orange-100 dark:bg-orange-900/20', 
    textColor: 'text-orange-700 dark:text-orange-300',
    label: 'MODERATION'
  },
  'rerank': { 
    bgColor: 'bg-pink-100 dark:bg-pink-900/20', 
    textColor: 'text-pink-700 dark:text-pink-300',
    label: 'RERANK'
  },
  'completion': { 
    bgColor: 'bg-gray-100 dark:bg-gray-700', 
    textColor: 'text-gray-700 dark:text-gray-300',
    label: 'LLM'
  }
};

export function CreateModelForm() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [providers, setProviders] = useState<LLMProvider[]>([]);
  const [isLoadingProviders, setIsLoadingProviders] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [advancedMode, setAdvancedMode] = useState(false);
  const [formData, setFormData] = useState<LLMModelCreate>({
    provider_id: 0,
    model_name: '',
    capability: 'chat',
    params: {
      temperature: 0.7,
      max_tokens: 1000
    },
  });

  // 预设模型参数
  const defaultParams: Record<string, Record<string, any>> = {
    'chat': {
      temperature: 0.7,
      max_tokens: 1000,
      top_p: 0.95,
      frequency_penalty: 0,
      presence_penalty: 0
    },
    'embedding': {
      dimensions: 1536
    },
    'completion': {
      temperature: 0.7,
      max_tokens: 1000,
      top_p: 0.95
    },
    'speech': {
      language: 'en'
    },
    'tts': {
      voice: 'alloy',
      speed: 1.0
    },
    'moderation': {
      categories: ['hate', 'harassment', 'self-harm', 'sexual', 'violence']
    },
    'rerank': {
      top_n: 10
    }
  };

  useEffect(() => {
    const fetchProviders = async () => {
      try {
        const data = await getProviders();
        setProviders(data);
        
        // Set default provider if available and use URL parameters if present
        if (data.length > 0) {
          const urlParams = new URLSearchParams(window.location.search);
          const providerId = urlParams.get('provider');
          
          if (providerId && data.some(p => p.id.toString() === providerId)) {
            setFormData(prevData => ({
              ...prevData,
              provider_id: parseInt(providerId, 10),
            }));
          } else {
            setFormData(prevData => ({
              ...prevData,
              provider_id: data[0].id,
            }));
          }
        }
      } catch (error) {
        console.error('Error fetching providers:', error);
        setError('Failed to load providers. Please try again later.');
      } finally {
        setIsLoadingProviders(false);
      }
    };

    fetchProviders();
  }, []);

  // 更新参数当能力改变时
  useEffect(() => {
    setFormData(prev => ({
      ...prev,
      params: defaultParams[prev.capability] || {}
    }));
  }, [formData.capability]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;

    if (name === 'provider_id') {
      setFormData(prevData => ({
        ...prevData,
        provider_id: parseInt(value, 10),
      }));
    } else if (name.startsWith('params.')) {
      const paramName = name.substring(7); // 移除 'params.' 前缀
      let paramValue: any = value;
      
      // 尝试转换数字
      if (!isNaN(Number(value)) && value !== '') {
        paramValue = Number(value);
      }
      
      setFormData(prevData => ({
        ...prevData,
        params: {
          ...prevData.params,
          [paramName]: paramValue
        }
      }));
    } else {
      setFormData(prevData => ({
        ...prevData,
        [name]: value,
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    try {
      setIsLoading(true);
      await createModel(formData);
      router.push('/llm');
      router.refresh();
    } catch (error) {
      console.error('Error creating model:', error);
      setError('Failed to create model. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const presetModels = {
    openai: {
      chat: ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo', 'gpt-4-vision-preview'],
      embedding: ['text-embedding-ada-002', 'text-embedding-3-small', 'text-embedding-3-large'],
      moderation: ['text-moderation-latest'],
      tts: ['tts-1', 'tts-1-hd'],
      speech: ['whisper-1']
    },
    anthropic: {
      chat: ['claude-2', 'claude-instant-1', 'claude-3-sonnet', 'claude-3-opus', 'claude-3-haiku']
    },
    mistral: {
      chat: ['mistral-tiny', 'mistral-small', 'mistral-medium', 'mistral-large']
    },
    cohere: {
      chat: ['command', 'command-light', 'command-r', 'command-light-nightly'],
      embedding: ['embed-english-v3.0', 'embed-multilingual-v3.0'],
      rerank: ['rerank-english-v3.0', 'rerank-multilingual-v3.0']
    },
    google: {
      chat: ['gemini-pro', 'gemini-pro-vision', 'gemini-ultra'],
      embedding: ['text-embedding-gecko']
    },
    deepseek: {
      chat: ['deepseek-chat', 'deepseek-coder']
    },
    minimax: {
      chat: ['abab6-chat', 'abab5.5s-chat', 'abab5.5-chat']
    },
    huggingface: {
      chat: ['meta-llama/Llama-2-70b-chat-hf', 'mistralai/Mistral-7B-Instruct-v0.2']
    }
  };

  const getModelSuggestions = () => {
    const provider = providers.find(p => p.id === formData.provider_id);
    if (!provider) return [];
    
    const providerType = provider.type.toLowerCase();
    // 查找匹配的提供商类型
    for (const [key, models] of Object.entries(presetModels)) {
      if (providerType.includes(key)) {
        return models[formData.capability as keyof typeof models] || [];
      }
    }
    
    return [];
  };

  // 获取当前选中的提供商类型
  const getSelectedProviderType = () => {
    const provider = providers.find(p => p.id === formData.provider_id);
    return provider?.type || '';
  };

  // 当提供商变更时自动选择热门模型
  useEffect(() => {
    const provider = providers.find(p => p.id === formData.provider_id);
    if (!provider) return;
    
    const providerType = provider.type.toLowerCase();
    
    // 查找匹配的提供商类型和推荐模型
    for (const [key, modelsByType] of Object.entries(presetModels)) {
      if (providerType.includes(key)) {
        const models = modelsByType[formData.capability as keyof typeof modelsByType] || [];
        if (models.length > 0) {
          setFormData(prev => ({
            ...prev,
            model_name: models[0]
          }));
        }
        break;
      }
    }
  }, [formData.provider_id, formData.capability, providers]);

  // 渲染参数输入表单
  const renderParamInputs = () => {
    const params = formData.params || {};
    
    if (formData.capability === 'chat' || formData.capability === 'completion') {
      return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
          <div>
            <label htmlFor="params.temperature" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
              Temperature
            </label>
            <Input
              id="params.temperature"
              name="params.temperature"
              type="number"
              min="0"
              max="2"
              step="0.1"
              value={params.temperature?.toString() || "0.7"}
              onChange={handleChange}
              className="py-3 text-lg"
            />
            <p className="mt-1 text-sm text-gray-500">Controls randomness: 0 is deterministic, higher values are more random.</p>
          </div>
          
          <div>
            <label htmlFor="params.max_tokens" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
              Max Tokens
            </label>
            <Input
              id="params.max_tokens"
              name="params.max_tokens"
              type="number"
              min="0"
              value={params.max_tokens?.toString() || "1000"}
              onChange={handleChange}
              className="py-3 text-lg"
            />
            <p className="mt-1 text-sm text-gray-500">Maximum number of tokens to generate.</p>
          </div>
          
          {advancedMode && (
            <>
              <div>
                <label htmlFor="params.top_p" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
                  Top P
                </label>
                <Input
                  id="params.top_p"
                  name="params.top_p"
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  value={params.top_p?.toString() || "0.95"}
                  onChange={handleChange}
                  className="py-3 text-lg"
                />
                <p className="mt-1 text-sm text-gray-500">Controls diversity via nucleus sampling.</p>
              </div>
              
              <div>
                <label htmlFor="params.frequency_penalty" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
                  Frequency Penalty
                </label>
                <Input
                  id="params.frequency_penalty"
                  name="params.frequency_penalty"
                  type="number"
                  min="-2"
                  max="2"
                  step="0.1"
                  value={params.frequency_penalty?.toString() || "0"}
                  onChange={handleChange}
                  className="py-3 text-lg"
                />
                <p className="mt-1 text-sm text-gray-500">Reduces repetition of frequent tokens.</p>
              </div>
              
              <div>
                <label htmlFor="params.presence_penalty" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
                  Presence Penalty
                </label>
                <Input
                  id="params.presence_penalty"
                  name="params.presence_penalty"
                  type="number"
                  min="-2"
                  max="2"
                  step="0.1"
                  value={params.presence_penalty?.toString() || "0"}
                  onChange={handleChange}
                  className="py-3 text-lg"
                />
                <p className="mt-1 text-sm text-gray-500">Reduces repetition of any token that has appeared in the output.</p>
              </div>
            </>
          )}
        </div>
      );
    } else if (formData.capability === 'embedding') {
      return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
          <div>
            <label htmlFor="params.dimensions" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
              Dimensions
            </label>
            <Input
              id="params.dimensions"
              name="params.dimensions"
              type="number"
              min="1"
              value={params.dimensions?.toString() || "1536"}
              onChange={handleChange}
              className="py-3 text-lg"
            />
            <p className="mt-1 text-sm text-gray-500">The dimensionality of the generated embeddings.</p>
          </div>
        </div>
      );
    } else if (formData.capability === 'tts') {
      return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
          <div>
            <label htmlFor="params.voice" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
              Voice
            </label>
            <select
              id="params.voice"
              name="params.voice"
              value={params.voice || "alloy"}
              onChange={handleChange}
              className="block w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 px-4 py-3 text-lg shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="alloy">Alloy</option>
              <option value="echo">Echo</option>
              <option value="fable">Fable</option>
              <option value="onyx">Onyx</option>
              <option value="nova">Nova</option>
              <option value="shimmer">Shimmer</option>
            </select>
            <p className="mt-1 text-sm text-gray-500">The voice to use for audio generation.</p>
          </div>
          
          <div>
            <label htmlFor="params.speed" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
              Speed
            </label>
            <Input
              id="params.speed"
              name="params.speed"
              type="number"
              min="0.25"
              max="4.0"
              step="0.25"
              value={params.speed?.toString() || "1.0"}
              onChange={handleChange}
              className="py-3 text-lg"
            />
            <p className="mt-1 text-sm text-gray-500">The speed of the generated audio.</p>
          </div>
        </div>
      );
    } else if (formData.capability === 'rerank') {
      return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
          <div>
            <label htmlFor="params.top_n" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
              Top N
            </label>
            <Input
              id="params.top_n"
              name="params.top_n"
              type="number"
              min="1"
              max="100"
              value={params.top_n?.toString() || "10"}
              onChange={handleChange}
              className="py-3 text-lg"
            />
            <p className="mt-1 text-sm text-gray-500">Number of top documents to return after reranking.</p>
          </div>
        </div>
      );
    }
    
    return null;
  };

  if (isLoadingProviders) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-500 border-r-transparent" role="status">
          <span className="sr-only">Loading...</span>
        </div>
        <p className="ml-3 text-gray-600">Loading providers...</p>
      </div>
    );
  }

  if (providers.length === 0) {
    return (
      <div className="text-center py-8 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="mx-auto w-16 h-16 flex items-center justify-center rounded-full bg-blue-50 dark:bg-blue-900/20 mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 className="text-xl font-semibold mb-2">No Providers Available</h3>
        <p className="mb-6 text-gray-500 dark:text-gray-400 max-w-sm mx-auto">
          You need to add a provider before you can create a model.
        </p>
        <Button 
          onClick={() => router.push('/llm')}
          className="px-6"
        >
          Add Provider
        </Button>
      </div>
    );
  }

  const selectedProviderType = getSelectedProviderType();
  const modelSuggestions = getModelSuggestions();

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800">
          <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}
      
      <div className="bg-white dark:bg-gray-800 p-8 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-2xl font-medium mb-6">Model Information</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
          <div>
            <label htmlFor="provider_id" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
              Provider <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <select
                id="provider_id"
                name="provider_id"
                required
                value={formData.provider_id.toString()}
                onChange={handleChange}
                className="block w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 pl-12 pr-4 py-3 text-lg text-left shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                {providers.map((provider) => (
                  <option key={provider.id} value={provider.id.toString()}>
                    {provider.name} ({provider.type})
                  </option>
                ))}
              </select>
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <ModelIcon type={selectedProviderType} size="md" withBackground={true} />
              </div>
            </div>
          </div>

          <div>
            <label htmlFor="model_name" className="block text-base font-medium text-gray-900 dark:text-white mb-2">
              Model Name <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <Input
                id="model_name"
                name="model_name"
                type="text"
                required
                list="model-suggestions"
                value={formData.model_name}
                onChange={handleChange}
                placeholder="e.g., gpt-3.5-turbo"
                className="py-3 text-lg"
              />
              {modelSuggestions.length > 0 && (
                <datalist id="model-suggestions">
                  {modelSuggestions.map(model => (
                    <option key={model} value={model} />
                  ))}
                </datalist>
              )}
            </div>
            {modelSuggestions.length > 0 && (
              <p className="mt-1 text-sm text-gray-500">
                Suggested models: {modelSuggestions.slice(0, 2).join(', ')} {modelSuggestions.length > 2 ? 'and more' : ''}
              </p>
            )}
          </div>
        </div>
        
        <div className="mt-6">
          <label className="block text-base font-medium text-gray-900 dark:text-white mb-2">
            Model Capability <span className="text-red-500">*</span>
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 mt-2">
            {Object.entries(capabilityColors).map(([capability, config]) => (
              <div 
                key={capability}
                className={`flex items-center rounded-lg border ${
                  formData.capability === capability
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/10'
                    : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700'
                } p-4 cursor-pointer transition-colors`}
                onClick={() => setFormData(prev => ({ ...prev, capability: capability as any }))}
              >
                <div className="flex-1">
                  <div className="flex items-center">
                    <input
                      type="radio"
                      name="capability"
                      value={capability}
                      checked={formData.capability === capability}
                      onChange={() => {}}
                      className="w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                    />
                    <span 
                      className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium ${config.bgColor} ${config.textColor}`}
                    >
                      {config.label}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      <div className="bg-white dark:bg-gray-800 p-8 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6">
          <h3 className="text-2xl font-medium">Model Parameters</h3>
          
          <button
            type="button"
            className="flex items-center text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 mt-2 sm:mt-0"
            onClick={() => setAdvancedMode(!advancedMode)}
          >
            {advancedMode ? 'Hide Advanced Parameters' : 'Show Advanced Parameters'}
            <HiOutlineChevronDown className={`ml-1 transition-transform ${advancedMode ? 'rotate-180' : ''}`} />
          </button>
        </div>
        
        {renderParamInputs()}
        
        <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-start">
            <div className="flex items-center h-5">
              <input
                id="use_default"
                name="use_default"
                type="checkbox"
                checked={true}
                disabled
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>
            <div className="ml-3">
              <label htmlFor="use_default" className="text-sm text-gray-700 dark:text-gray-300">Use default parameter settings</label>
              <p className="text-xs text-gray-500 dark:text-gray-400">Automatically set recommended parameters based on model type</p>
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
          disabled={isLoading || !formData.model_name}
          className="px-6"
        >
          {isLoading ? 'Creating...' : 'Create Model'}
        </Button>
      </div>
    </form>
  );
} 