import React from 'react';
import { Label } from '../Label';

export interface FormFieldProps {
  id: string;
  label?: string;
  required?: boolean;
  error?: boolean;
  helperText?: string;
  className?: string;
  children: React.ReactNode;
}

export function FormField({
  id,
  label,
  required,
  error,
  helperText,
  className = '',
  children,
}: FormFieldProps) {
  return (
    <div className={`space-y-2 ${className}`}>
      {label && (
        <Label htmlFor={id} required={required}>
          {label}
        </Label>
      )}
      {children}
      {helperText && (
        <p
          className={`text-sm ${
            error ? 'text-red-600 dark:text-red-500' : 'text-gray-500 dark:text-gray-400'
          }`}
        >
          {helperText}
        </p>
      )}
    </div>
  );
} 