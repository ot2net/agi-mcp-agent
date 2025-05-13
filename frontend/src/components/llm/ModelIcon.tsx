'use client';

import { HiOutlineChip, HiOutlineCog } from 'react-icons/hi';

type ModelIconProps = {
  type: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  withBackground?: boolean;
};

export function ModelIcon({ type, size = 'md', className = '', withBackground = false }: ModelIconProps) {
  // Map of provider types to their SVG icons
  const iconMap: Record<string, string> = {
    'openai': '/models/openai.svg',
    'anthropic': '/models/claude.svg',
    'claude': '/models/claude.svg',
    'google': '/models/gemini.svg',
    'gemini': '/models/gemini.svg', 
    'deepseek': '/models/deepseek.svg',
    'qwen': '/models/qwen.svg',
    'rest': '/models/qwen.svg', // For type "rest" which should use Qwen icon
    'mistral': '/models/mistral.svg',
    'huggingface': '/models/huggingface.svg',
    'cohere': '/models/cohere.svg',
    'minimax': '/models/minimax.svg',
  };
  
  // Map of provider types to their brand colors for background
  const colorMap: Record<string, string> = {
    'openai': 'bg-green-100 dark:bg-green-900/20',
    'anthropic': 'bg-orange-100 dark:bg-orange-900/20',
    'claude': 'bg-orange-100 dark:bg-orange-900/20',
    'google': 'bg-blue-100 dark:bg-blue-900/20',
    'gemini': 'bg-blue-100 dark:bg-blue-900/20',
    'deepseek': 'bg-blue-100 dark:bg-blue-900/20',
    'qwen': 'bg-blue-100 dark:bg-blue-900/20',
    'rest': 'bg-blue-100 dark:bg-blue-900/20',
    'mistral': 'bg-indigo-100 dark:bg-indigo-900/20',
    'huggingface': 'bg-yellow-100 dark:bg-yellow-900/20',
    'cohere': 'bg-purple-100 dark:bg-purple-900/20',
    'minimax': 'bg-gray-100 dark:bg-gray-800',
  };

  // Get icon from map, or from partial match
  const getIconSrc = (providerType: string): string | null => {
    const lowerType = providerType.toLowerCase();
    
    // Direct match
    if (iconMap[lowerType]) {
      return iconMap[lowerType];
    }
    
    // Partial match
    for (const [key, value] of Object.entries(iconMap)) {
      if (lowerType.includes(key)) {
        return value;
      }
    }
    
    return null;
  };
  
  // Get color for provider type
  const getColor = (providerType: string): string => {
    const lowerType = providerType.toLowerCase();
    
    // Direct match
    if (colorMap[lowerType]) {
      return colorMap[lowerType];
    }
    
    // Partial match
    for (const [key, value] of Object.entries(colorMap)) {
      if (lowerType.includes(key)) {
        return value;
      }
    }
    
    return 'bg-gray-100 dark:bg-gray-800';
  };

  const iconSrc = getIconSrc(type);
  const bgColor = withBackground ? getColor(type) : '';
  
  // Icon sizes - consistent across different providers
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-10 h-10',
    xl: 'w-14 h-14'
  };

  const sizeClass = sizeClasses[size];
  
  // Background container sizes - slightly larger than the icon to provide padding
  const bgSizeClasses = {
    sm: 'w-10 h-10',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
    xl: 'w-20 h-20'
  };
  
  const bgSizeClass = withBackground ? bgSizeClasses[size] : '';
  
  // Container class with proper centering and fixed dimensions
  const containerClass = `flex items-center justify-center ${
    withBackground ? `${bgSizeClass} ${bgColor} rounded-lg` : ''
  } ${className}`;
  
  // If no icon is found, use a default icon
  if (!iconSrc) {
    const DefaultIcon = type.toLowerCase().includes('model') ? HiOutlineChip : HiOutlineCog;
    return (
      <div className={containerClass}>
        <DefaultIcon className={`${sizeClass} text-gray-600`} />
      </div>
    );
  }
  
  return (
    <div className={containerClass}>
      <img 
        src={iconSrc}
        alt={type}
        className={`${sizeClass} object-contain`}
      />
    </div>
  );
} 