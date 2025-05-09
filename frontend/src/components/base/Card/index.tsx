import React from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
  showDivider?: boolean;
  icon?: React.ReactNode;
  badge?: React.ReactNode;
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className = '', title, description, showDivider = false, icon, badge, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={`
          relative
          rounded-xl border border-gray-200 dark:border-gray-700
          bg-white dark:bg-gray-800
          shadow-[0_2px_8px_0_rgba(0,0,0,0.04)]
          hover:shadow-[0_4px_16px_0_rgba(0,0,0,0.08)]
          hover:bg-gray-50 dark:hover:bg-gray-700
          transition-all duration-300 animate-fade-in
          ${className}
        `}
        {...props}
      >
        {(title || description || icon || badge) && (
          <div className="flex items-start gap-3 px-6 pt-5 pb-2">
            {icon && (
              <div className="flex-shrink-0 mt-1 text-blue-500 dark:text-blue-400">
                {icon}
              </div>
            )}
            <div className="flex-1">
              {title && (
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  {title}
                  {badge && <span className="ml-2 align-middle">{badge}</span>}
                </h3>
              )}
              {description && (
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{description}</p>
              )}
            </div>
          </div>
        )}
        {(title || description || showDivider || icon || badge) && (
          <div className="border-t border-gray-100 dark:border-gray-700 mx-6" />
        )}
        <div className="px-6 py-5">{children}</div>
      </div>
    );
  }
);

Card.displayName = 'Card';

export { Card }; 