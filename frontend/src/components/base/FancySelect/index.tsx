import React, { useState, useRef, useEffect } from 'react';
import { HiChevronDown, HiCheck } from 'react-icons/hi';

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
  ({ className = '', options, error, helperText, name, value, onChange, ...props }, ref) => {
    const [isOpen, setIsOpen] = useState(false);
    const [selectedOption, setSelectedOption] = useState<FancySelectOption | null>(
      options.find(opt => opt.value === value) || null
    );
    const selectRef = useRef<HTMLDivElement>(null);
    const hiddenSelectRef = useRef<HTMLSelectElement>(null);

    useEffect(() => {
      // Update selected option when value changes externally
      const newSelected = options.find(opt => opt.value === value) || null;
      setSelectedOption(newSelected);
    }, [value, options]);

    useEffect(() => {
      // Close dropdown when clicking outside
      const handleClickOutside = (event: MouseEvent) => {
        if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
          setIsOpen(false);
        }
      };

      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }, []);

    const handleOptionClick = (option: FancySelectOption) => {
      setSelectedOption(option);
      setIsOpen(false);

      // Create a synthetic event to simulate the native select onChange
      if (hiddenSelectRef.current && onChange) {
        const syntheticEvent = {
          target: {
            name,
            value: option.value
          }
        } as React.ChangeEvent<HTMLSelectElement>;
        
        // Update the hidden select value
        hiddenSelectRef.current.value = option.value;
        
        // Trigger onChange
        onChange(syntheticEvent);
      }
    };

    const baseClasses = 'relative w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition shadow-sm';
    const normalClasses = 'ring-gray-300 dark:ring-gray-600 focus:ring-blue-600';
    const errorClasses = 'ring-red-300 dark:ring-red-600 focus:ring-red-500 dark:bg-red-900/10';
    
    const selectClasses = `${baseClasses} ${error ? errorClasses : normalClasses} ${className}`;

    return (
      <div className="w-full">
        {/* Hidden native select for form submission */}
        <select
          ref={(node) => {
            // Assign to both refs
            if (typeof ref === 'function') {
              ref(node);
            } else if (ref) {
              ref.current = node;
            }
            hiddenSelectRef.current = node;
          }}
          name={name}
          value={selectedOption?.value || ''}
          onChange={onChange}
          className="sr-only"
          {...props}
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>

        {/* Custom styled select */}
        <div className="relative" ref={selectRef}>
          <div 
            className={`${selectClasses} px-4 py-2.5 flex items-center justify-between cursor-pointer`}
            onClick={() => setIsOpen(!isOpen)}
          >
            <div className="flex items-center">
              {selectedOption?.icon && (
                <div className="mr-3 flex-shrink-0">
                  {selectedOption.icon}
                </div>
              )}
              <span>{selectedOption?.label || 'Select an option'}</span>
            </div>
            <HiChevronDown className={`w-5 h-5 text-gray-500 dark:text-gray-400 transition duration-200 ${isOpen ? 'transform rotate-180' : ''}`} />
          </div>

          {/* Dropdown options */}
          {isOpen && (
            <div className="absolute z-10 mt-1 w-full rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-lg max-h-60 overflow-auto">
              {options.map((option) => (
                <div
                  key={option.value}
                  className={`px-4 py-2.5 flex items-center hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer ${
                    option.value === selectedOption?.value 
                      ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-300' 
                      : 'text-gray-900 dark:text-white'
                  }`}
                  onClick={() => handleOptionClick(option)}
                >
                  <div className="flex items-center flex-1">
                    {option.icon && (
                      <div className="mr-3 flex-shrink-0">
                        {option.icon}
                      </div>
                    )}
                    <span>{option.label}</span>
                  </div>
                  {option.value === selectedOption?.value && (
                    <HiCheck className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

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