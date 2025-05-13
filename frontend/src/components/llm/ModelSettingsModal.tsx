'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/base/Button';
import { LLMModel } from '@/types/llm';
import { getModels } from '@/api/llm';
import { ModelIcon } from '@/components/llm/ModelIcon';
import { HiOutlineExclamationCircle } from 'react-icons/hi';

interface ModelSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (settings: SystemModelSettings) => Promise<void>;
  initialSettings?: SystemModelSettings;
}

export interface SystemModelSettings {
  chatModel: number | null;
  embeddingModel: number | null;
  rerankModel: number | null;
  speechToTextModel: number | null;
  textToSpeechModel: number | null;
}

// 各种模型能力的颜色映射
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

export function ModelSettingsModal({ isOpen, onClose, onSave, initialSettings }: ModelSettingsModalProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingModels, setIsLoadingModels] = useState(true);
  const [models, setModels] = useState<LLMModel[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [settings, setSettings] = useState<SystemModelSettings>({
    chatModel: null,
    embeddingModel: null,
    rerankModel: null,
    speechToTextModel: null,
    textToSpeechModel: null,
    ...initialSettings
  });

  // Get all available models
  useEffect(() => {
    const fetchModels = async () => {
      if (!isOpen) return;
      
      try {
        setIsLoadingModels(true);
        const allModels = await getModels();
        setModels(allModels.filter(model => model.status === 'enabled'));
      } catch (error) {
        console.error('Failed to fetch models:', error);
        setError('Failed to load models. Please try again later.');
      } finally {
        setIsLoadingModels(false);
      }
    };

    fetchModels();
  }, [isOpen]);

  // Get models by capability
  const getModelsByCapability = (capability: string): LLMModel[] => {
    return models.filter(model => model.capability === capability);
  };

  // Handle model selection change
  const handleModelChange = (key: keyof SystemModelSettings, modelId: number | null) => {
    setSettings(prev => ({
      ...prev,
      [key]: modelId
    }));
  };

  // Save system settings
  const handleSave = async () => {
    try {
      setIsLoading(true);
      setError(null);
      await onSave(settings);
      onClose();
    } catch (error) {
      console.error('Failed to save system settings:', error);
      setError('Failed to save settings. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Render model selector
  const renderModelSelector = (
    title: string,
    settingKey: keyof SystemModelSettings,
    capability: string,
    helpText: string
  ) => {
    const availableModels = getModelsByCapability(capability);
    const selectedModelId = settings[settingKey] as number | null;
    const selectedModel = selectedModelId ? models.find(m => m.id === selectedModelId) : null;
    
    return (
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-2">
          <label className="block text-base font-medium text-gray-900 dark:text-white">
            {title}
          </label>
          <span 
            className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium ${
              capabilityLabels[capability]?.bgColor || 'bg-gray-100 dark:bg-gray-700'
            } ${
              capabilityLabels[capability]?.textColor || 'text-gray-700 dark:text-gray-300'
            }`}
          >
            {capabilityLabels[capability]?.label || capability.toUpperCase()}
          </span>
        </div>
        
        <p className="text-sm text-gray-500 mb-2">{helpText}</p>
        
        {availableModels.length === 0 ? (
          <div className="p-4 bg-gray-50 dark:bg-gray-900 border border-dashed border-gray-300 dark:border-gray-700 rounded-lg">
            <div className="flex items-center text-gray-500 dark:text-gray-400">
              <HiOutlineExclamationCircle className="mr-2" />
              <span>No {capability} models available. Please add one first.</span>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-2">
            {availableModels.map(model => (
              <div 
                key={model.id}
                className={`flex items-center p-3 rounded-lg border ${
                  selectedModelId === model.id 
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/10' 
                    : 'border-gray-200 dark:border-gray-700'
                } cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700`}
                onClick={() => handleModelChange(settingKey, model.id)}
              >
                <input
                  type="radio"
                  checked={selectedModelId === model.id}
                  onChange={() => {}}
                  className="w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <div className="ml-3 flex items-center flex-1">
                  <ModelIcon type={model.provider_name} size="sm" withBackground={true} className="mr-2" />
                  <div>
                    <p className="font-medium">{model.model_name}</p>
                    <p className="text-sm text-gray-500">{model.provider_name}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 overflow-auto">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-3xl w-full">
        <div className="border-b border-gray-200 dark:border-gray-700 p-4">
          <h3 className="text-xl font-semibold">System Model Settings</h3>
          <p className="text-sm text-gray-500 mt-1">
            Configure default models for system functions
          </p>
        </div>

        <div className="p-6 max-h-[70vh] overflow-y-auto">
          {error && (
            <div className="p-4 mb-6 rounded-lg bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800">
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          {isLoadingModels ? (
            <div className="flex items-center justify-center py-12">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-500 border-r-transparent" role="status">
                <span className="sr-only">Loading...</span>
              </div>
              <p className="ml-3 text-gray-600">Loading models...</p>
            </div>
          ) : (
            <div>
              {renderModelSelector(
                'System LLM Model',
                'chatModel',
                'chat',
                'Default large language model for system chat and reasoning'
              )}
              
              {renderModelSelector(
                'Embedding Model',
                'embeddingModel',
                'embedding',
                'For text vectorization and semantic search'
              )}
              
              {renderModelSelector(
                'Rerank Model',
                'rerankModel',
                'rerank',
                'For reranking search results'
              )}
              
              {renderModelSelector(
                'Speech-to-Text Model',
                'speechToTextModel',
                'speech',
                'For speech recognition and transcription'
              )}
              
              {renderModelSelector(
                'Text-to-Speech Model',
                'textToSpeechModel',
                'tts',
                'For text-to-speech and audio generation'
              )}
            </div>
          )}
        </div>

        <div className="border-t border-gray-200 dark:border-gray-700 p-4 flex justify-end gap-3">
          <Button
            variant="outline"
            onClick={onClose}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            disabled={isLoading || isLoadingModels}
          >
            {isLoading ? 'Saving...' : 'Save'}
          </Button>
        </div>
      </div>
    </div>
  );
} 