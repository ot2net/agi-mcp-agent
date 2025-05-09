import React from 'react';

export interface TextAreaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: boolean;
  helperText?: string;
}

const TextArea = React.forwardRef<HTMLTextAreaElement, TextAreaProps>(
  ({ className = '', error, helperText, ...props }, ref) => {
    const baseClasses = 'block w-full rounded-md border-0 py-1.5 text-gray-900 dark:text-white shadow-sm ring-1 ring-inset placeholder:text-gray-400 focus:ring-2 focus:ring-inset sm:text-sm sm:leading-6';
    const normalClasses = 'ring-gray-300 dark:ring-gray-600 focus:ring-blue-600 dark:bg-gray-700';
    const errorClasses = 'ring-red-300 dark:ring-red-600 focus:ring-red-500 dark:bg-red-900/10';
    
    const textareaClasses = `${baseClasses} ${error ? errorClasses : normalClasses} ${className}`;

    return (
      <div className="w-full">
        <textarea
          ref={ref}
          className={textareaClasses}
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

TextArea.displayName = 'TextArea';

export { TextArea }; 