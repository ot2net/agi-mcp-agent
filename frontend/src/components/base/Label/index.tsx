import React from 'react';

export interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  required?: boolean;
}

const Label = React.forwardRef<HTMLLabelElement, LabelProps>(
  ({ className = '', children, required, ...props }, ref) => {
    return (
      <label
        ref={ref}
        className={`block text-sm font-medium leading-6 text-gray-900 dark:text-white ${className}`}
        {...props}
      >
        {children}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
    );
  }
);

Label.displayName = 'Label';

export { Label }; 