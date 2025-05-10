'use client';

import { useState, useEffect } from 'react';
import { Environment } from '@/types/environment';
import { Card } from '@/components/base/Card';
import { Button } from '@/components/base/Button';
import { EnvironmentList } from '@/components/EnvironmentList';
import { EnvironmentForm } from '@/components/EnvironmentForm';
import { HiOutlineRefresh, HiOutlinePlus, HiOutlineServer } from 'react-icons/hi';

export default function EnvironmentsPage() {
  const [environments, setEnvironments] = useState<Environment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEnv, setSelectedEnv] = useState<Environment | null>(null);

  const fetchEnvironments = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('/api/environments');
      if (!response.ok) {
        throw new Error('Failed to fetch environments');
      }
      const data = await response.json();
      setEnvironments(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateEnvironment = async (env: Omit<Environment, 'id' | 'status' | 'created_at' | 'updated_at'>) => {
    try {
      setError(null);
      const response = await fetch('/api/environments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(env),
      });

      if (!response.ok) {
        throw new Error('Failed to create environment');
      }

      await fetchEnvironments();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const handleDeleteEnvironment = async (env: Environment) => {
    try {
      setError(null);
      const response = await fetch(`/api/environments/${env.id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete environment');
      }

      await fetchEnvironments();
      if (selectedEnv?.id === env.id) {
        setSelectedEnv(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  useEffect(() => {
    fetchEnvironments();
  }, []);

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Environments</h1>
        <Button
          onClick={fetchEnvironments}
          variant="outline"
          icon={<HiOutlineRefresh className="w-5 h-5" />}
          className="animate-fade-in"
        >
          Refresh
        </Button>
      </div>

      {error && (
        <Card className="bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <Card
            title="Create Environment"
            description="Create a new environment to manage your resources"
            icon={<HiOutlinePlus className="w-5 h-5" />}
          >
            <EnvironmentForm onSubmit={handleCreateEnvironment} />
          </Card>
        </div>
        <div>
          <Card
            title="Environment List"
            description="View and manage your environments"
            icon={<HiOutlineServer className="w-5 h-5" />}
          >
            <div className="animate-fade-in">
              {loading ? (
                <div className="flex justify-center items-center h-32">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-white"></div>
                </div>
              ) : (
                <EnvironmentList
                  environments={environments}
                  selectedEnvironment={selectedEnv}
                  onSelect={setSelectedEnv}
                  onDelete={handleDeleteEnvironment}
                />
              )}
            </div>
          </Card>
        </div>
      </div>

      {selectedEnv && (
        <Card
          title="Environment Details"
          description={`Details for ${selectedEnv.name}`}
          badge={
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              selectedEnv.status === 'active' 
                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
            }`}>
              {selectedEnv.status}
            </span>
          }
        >
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Type</h3>
              <p className="mt-1">{selectedEnv.type}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Configuration</h3>
              <pre className="mt-1 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg overflow-x-auto">
                {JSON.stringify(selectedEnv.config, null, 2)}
              </pre>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Created</h3>
              <p className="mt-1">{selectedEnv.created_at ? new Date(selectedEnv.created_at).toLocaleString() : 'N/A'}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Last Updated</h3>
              <p className="mt-1">{selectedEnv.updated_at ? new Date(selectedEnv.updated_at).toLocaleString() : 'N/A'}</p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
} 