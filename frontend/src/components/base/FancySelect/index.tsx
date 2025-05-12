import React from 'react';

export interface FancySelectOption {
  value: string;
  label: string;
  icon?: React.ReactNode;
}

export interface FancySelectProps extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'children'> {
  options: FancySelectOption[];
  error?: boolean;
  helperText?: string;
}

const FancySelect = React.forwardRef<HTMLSelectElement, FancySelectProps>(
  ({ className = '', options, error, helperText, ...props }, ref) => {
    const baseClasses = 'block w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 px-4 py-3 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition shadow-sm';
    const normalClasses = 'ring-gray-300 dark:ring-gray-600 focus:ring-blue-600 dark:bg-gray-700';
    const errorClasses = 'ring-red-300 dark:ring-red-600 focus:ring-red-500 dark:bg-red-900/10';
    
    const selectClasses = `${baseClasses} ${error ? errorClasses : normalClasses} ${className}`;

    return (
      <div className="w-full">
        <select
          ref={ref}
          className={selectClasses}
          {...props}
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.icon && <span className="mr-2">{option.icon}</span>}
              {option.label}
            </option>
          ))}
        </select>
        {helperText && (
          <p className={`mt-2 text-sm ${error ? 'text-red-600 dark:text-red-500' : 'text-gray-500 dark:text-gray-400'}`}>
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

FancySelect.displayName = 'FancySelect';

export { FancySelect }; 