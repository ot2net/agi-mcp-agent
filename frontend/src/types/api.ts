/**
 * 通用API响应接口
 */
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

/**
 * 分页响应接口
 */
export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination?: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

/**
 * API错误接口
 */
export interface ApiError {
  code?: string;
  message: string;
  details?: Record<string, any>;
}

/**
 * 请求状态枚举
 */
export enum RequestStatus {
  IDLE = 'idle',
  LOADING = 'loading',
  SUCCESS = 'success',
  ERROR = 'error'
}

/**
 * API请求配置
 */
export interface ApiRequestConfig extends RequestInit {
  timeout?: number;
  retries?: number;
  retryDelay?: number;
} 