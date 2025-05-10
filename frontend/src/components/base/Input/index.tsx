import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
  helperText?: string;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className = '', error, helperText, ...props }, ref) => {
    const baseClasses = 'block w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 px-4 py-3 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition shadow-sm';
    const normalClasses = 'ring-gray-300 dark:ring-gray-600 focus:ring-blue-600 dark:bg-gray-700';
    const errorClasses = 'ring-red-300 dark:ring-red-600 focus:ring-red-500 dark:bg-red-900/10';
    
    const inputClasses = `${baseClasses} ${error ? errorClasses : normalClasses} ${className}`;

    return (
      <div className="w-full">
        <input
          ref={ref}
          className={inputClasses}
          {...props}
        />
        {helperText && (
          <p className={`mt-2 text-sm ${error ? 'text-red-600 dark:text-red-500' : 'text-gray-500 dark:text-gray-400'}`}>
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input }; 