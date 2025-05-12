'use client';

import { useState, useEffect } from 'react';
import { SystemStatus } from '@/types/systemStatus';
import { Card } from '@/components/base/Card';
import { HiOutlineServer, HiOutlineRefresh } from 'react-icons/hi';
import { Button } from './base/Button';

export function SystemStatusCard() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStatus();
    // Poll status every 30 seconds
    const intervalId = setInterval(fetchStatus, 30000);
    return () => clearInterval(intervalId);
  }, []);

  const fetchStatus = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/status');
      if (!response.ok) {
        throw new Error('Failed to fetch system status');
      }
      const data = await response.json();
      console.log('Status data:', data); // 调试用，可以在需要时移除
      setStatus(data);
      setError(null);
    } catch (err) {
      setError('Failed to load system status');
      console.error('Error fetching system status:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  return (
    <Card 
      title="System Status" 
      description="Current status of the MCP system"
      icon={<HiOutlineServer className="w-6 h-6" />}
      showDivider
    >
      <div className="flex justify-end mb-4">
        <Button
          variant="outline"
          size="sm"
          onClick={fetchStatus}
          icon={<HiOutlineRefresh className="w-4 h-4" />}
        >
          Refresh
        </Button>
      </div>
      
      {isLoading ? (
        <div className="flex justify-center items-center h-40">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800">
          <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      ) : status ? (
        <div className="grid grid-cols-2 gap-4">
          <div className="col-span-2 md:col-span-1">
            <div className="p-4 rounded-lg bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800">
              <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">Agents</h3>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <p className="text-2xl font-bold">{status.agents.total}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Total</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-green-500">{status.agents.active}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Active</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="col-span-2 md:col-span-1">
            <div className="p-4 rounded-lg bg-purple-50 dark:bg-purple-900/10 border border-purple-200 dark:border-purple-800">
              <h3 className="text-sm font-medium text-purple-800 dark:text-purple-200 mb-2">Tasks</h3>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <p className="text-2xl font-bold text-orange-500">{status.tasks.pending}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Pending</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-blue-500">{status.tasks.running}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Running</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="col-span-2 md:col-span-1">
            <div className="p-4 rounded-lg bg-green-50 dark:bg-green-900/10 border border-green-200 dark:border-green-800">
              <h3 className="text-sm font-medium text-green-800 dark:text-green-200 mb-2">Completed Tasks</h3>
              <p className="text-2xl font-bold text-green-500">{status.tasks.completed}</p>
            </div>
          </div>
          
          <div className="col-span-2 md:col-span-1">
            <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800">
              <h3 className="text-sm font-medium text-red-800 dark:text-red-200 mb-2">Failed Tasks</h3>
              <p className="text-2xl font-bold text-red-500">{status.tasks.failed}</p>
            </div>
          </div>
          
          <div className="col-span-2">
            <div className="p-4 rounded-lg bg-gray-50 dark:bg-gray-900/10 border border-gray-200 dark:border-gray-800">
              <h3 className="text-sm font-medium text-gray-800 dark:text-gray-200 mb-2">System Status</h3>
              <div className="grid grid-cols-2 gap-2 mb-2">
                <div>
                  <p className="text-lg font-medium">Running</p>
                  <p className={`text-lg font-bold ${status.running ? 'text-green-500' : 'text-red-500'}`}>
                    {status.running ? 'Active' : 'Stopped'}
                  </p>
                </div>
                <div>
                  <p className="text-lg font-medium">Last Updated</p>
                  <p className="text-sm text-gray-600">{formatDate(status.timestamp)}</p>
                </div>
              </div>
              
              {status.system_load !== undefined && (
                <>
                  <h3 className="text-sm font-medium text-gray-800 dark:text-gray-200 mt-4 mb-2">System Load</h3>
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded-full">
                    <div 
                      className="h-4 bg-blue-500 rounded-full" 
                      style={{ width: `${Math.min(status.system_load * 100, 100)}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {(status.system_load * 100).toFixed(1)}%
                  </p>
                </>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <p className="text-gray-500 dark:text-gray-400">No system status data available.</p>
        </div>
      )}
    </Card>
  );
} 