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
    'mistral': '/models/mistral.svg', // Now using actual mistral.svg file
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
    'mistral': 'bg-indigo-100 dark:bg-indigo-900/20', // Updated mistral background color
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
  
  // Size classes - increased sizes to be more prominent
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };

  const sizeClass = sizeClasses[size];
  
  // Background container sizes
  const bgSizeClasses = {
    sm: 'w-10 h-10',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
    xl: 'w-24 h-24'
  };
  
  const bgSizeClass = withBackground ? bgSizeClasses[size] : '';
  
  // Add a container class for better styling
  const containerClass = `flex items-center justify-center ${
    withBackground ? `${bgSizeClass} ${bgColor} rounded-lg p-2` : ''
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