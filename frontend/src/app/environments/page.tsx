'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface Environment {
  id: string;
  name: string;
  type: string;
  status: string;
}

interface EnvironmentAction {
  action: Record<string, any>;
}

interface EnvironmentActionResult {
  success: boolean;
  result: Record<string, any>;
}

interface CreateEnvironmentRequest {
  name: string;
  type: string;
  config: Record<string, any>;
}

export default function EnvironmentsPage() {
  const router = useRouter();
  const [environments, setEnvironments] = useState<Environment[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEnvironment, setSelectedEnvironment] = useState<Environment | null>(null);
  const [observation, setObservation] = useState<Record<string, any> | null>(null);
  const [actionInput, setActionInput] = useState<string>('{}');
  const [actionResult, setActionResult] = useState<Record<string, any> | null>(null);
  const [createForm, setCreateForm] = useState<{
    name: string;
    type: string;
    config: string;
  }>({
    name: '',
    type: 'api',
    config: '{}',
  });
  const [showCreateForm, setShowCreateForm] = useState<boolean>(false);

  // Fetch environments on page load
  useEffect(() => {
    fetchEnvironments();
  }, []);

  // Fetch all environments
  const fetchEnvironments = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/environments', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      const data = await response.json();
      setEnvironments(data);
      setError(null);
    } catch (err) {
      setError(`Failed to fetch environments: ${err instanceof Error ? err.message : String(err)}`);
      console.error('Error fetching environments:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch observation for an environment
  const fetchObservation = async (env: Environment) => {
    try {
      const response = await fetch(`/api/environments/${env.id}/observation`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      const data = await response.json();
      setObservation(data);
      setError(null);
    } catch (err) {
      setError(`Failed to fetch observation: ${err instanceof Error ? err.message : String(err)}`);
      console.error('Error fetching observation:', err);
    }
  };

  // Execute an action in an environment
  const executeAction = async () => {
    if (!selectedEnvironment) return;
    
    try {
      let actionJson: Record<string, any>;
      try {
        actionJson = JSON.parse(actionInput);
      } catch (err) {
        setError('Invalid JSON in action input');
        return;
      }
      
      const payload: EnvironmentAction = {
        action: actionJson
      };
      
      const response = await fetch(`/api/environments/${selectedEnvironment.id}/action`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(payload),
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      const result: EnvironmentActionResult = await response.json();
      setActionResult(result.result);
      setError(null);
      
      // Refresh observation after action
      await fetchObservation(selectedEnvironment);
    } catch (err) {
      setError(`Failed to execute action: ${err instanceof Error ? err.message : String(err)}`);
      console.error('Error executing action:', err);
    }
  };

  // Reset an environment
  const resetEnvironment = async () => {
    if (!selectedEnvironment) return;
    
    try {
      const response = await fetch(`/api/environments/${selectedEnvironment.id}/reset`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      const result = await response.json();
      setObservation(result);
      setActionResult(null);
      setError(null);
    } catch (err) {
      setError(`Failed to reset environment: ${err instanceof Error ? err.message : String(err)}`);
      console.error('Error resetting environment:', err);
    }
  };

  // Create a new environment
  const createEnvironment = async () => {
    try {
      let configJson: Record<string, any>;
      try {
        configJson = JSON.parse(createForm.config);
      } catch (err) {
        setError('Invalid JSON in config input');
        return;
      }
      
      const payload: CreateEnvironmentRequest = {
        name: createForm.name,
        type: createForm.type,
        config: configJson
      };
      
      const response = await fetch('/api/environments', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(payload),
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      const newEnv = await response.json();
      setEnvironments([...environments, newEnv]);
      setShowCreateForm(false);
      setCreateForm({
        name: '',
        type: 'api',
        config: '{}',
      });
      setError(null);
    } catch (err) {
      setError(`Failed to create environment: ${err instanceof Error ? err.message : String(err)}`);
      console.error('Error creating environment:', err);
    }
  };

  // Delete an environment
  const deleteEnvironment = async (env: Environment) => {
    if (!confirm(`Are you sure you want to delete environment "${env.name}"?`)) {
      return;
    }
    
    try {
      const response = await fetch(`/api/environments/${env.id}`, {
        method: 'DELETE',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      // Remove from list and clear selection if it was selected
      setEnvironments(environments.filter(e => e.id !== env.id));
      if (selectedEnvironment?.id === env.id) {
        setSelectedEnvironment(null);
        setObservation(null);
        setActionResult(null);
      }
      setError(null);
    } catch (err) {
      setError(`Failed to delete environment: ${err instanceof Error ? err.message : String(err)}`);
      console.error('Error deleting environment:', err);
    }
  };

  const handleEnvironmentSelect = async (env: Environment) => {
    setSelectedEnvironment(env);
    await fetchObservation(env);
    setActionResult(null);
  };

  const getEnvironmentTypeLabel = (type: string): string => {
    const typeLabels: Record<string, string> = {
      'api': 'API',
      'filesystem': 'Filesystem',
      'memory': 'Memory',
      'web': 'Web',
      'database': 'Database',
      'mcp': 'MCP',
    };
    return typeLabels[type] || type.charAt(0).toUpperCase() + type.slice(1);
  };

  const getEnvironmentTypeColor = (type: string): string => {
    const typeColors: Record<string, string> = {
      'api': 'bg-blue-100 text-blue-700',
      'filesystem': 'bg-green-100 text-green-700',
      'memory': 'bg-purple-100 text-purple-700',
      'web': 'bg-yellow-100 text-yellow-700',
      'database': 'bg-indigo-100 text-indigo-700',
      'mcp': 'bg-red-100 text-red-700',
    };
    return typeColors[type] || 'bg-gray-100 text-gray-700';
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Environments</h1>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          {showCreateForm ? 'Cancel' : 'Create Environment'}
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" role="alert">
          <p>{error}</p>
        </div>
      )}

      {showCreateForm && (
        <div className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-6">
          <h2 className="text-xl font-semibold mb-4">Create Environment</h2>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="name">
              Name
            </label>
            <input
              id="name"
              type="text"
              value={createForm.name}
              onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder="Environment Name"
            />
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="type">
              Type
            </label>
            <select
              id="type"
              value={createForm.type}
              onChange={(e) => setCreateForm({ ...createForm, type: e.target.value })}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            >
              <option value="api">API</option>
              <option value="filesystem">Filesystem</option>
              <option value="memory">Memory</option>
              <option value="web">Web</option>
              <option value="database">Database</option>
              <option value="mcp">MCP</option>
            </select>
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="config">
              Configuration (JSON)
            </label>
            <textarea
              id="config"
              value={createForm.config}
              onChange={(e) => setCreateForm({ ...createForm, config: e.target.value })}
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline h-32"
              placeholder='{"key": "value"}'
            />
          </div>
          <div className="flex items-center justify-between">
            <button
              onClick={createEnvironment}
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              type="button"
            >
              Create
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
          <h2 className="text-xl font-semibold mb-4">Environment List</h2>
          {loading ? (
            <p className="text-gray-500">Loading environments...</p>
          ) : environments.length === 0 ? (
            <p className="text-gray-500">No environments found</p>
          ) : (
            <ul>
              {environments.map((env) => (
                <li key={env.id} className="mb-2 flex justify-between">
                  <button
                    onClick={() => handleEnvironmentSelect(env)}
                    className={`flex-grow text-left px-3 py-2 rounded ${
                      selectedEnvironment?.id === env.id ? 'bg-gray-200' : 'hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-center">
                      <span className="font-medium">{env.name}</span>
                      <span className={`ml-2 text-xs px-2 py-1 rounded-full ${getEnvironmentTypeColor(env.type)}`}>
                        {getEnvironmentTypeLabel(env.type)}
                      </span>
                    </div>
                  </button>
                  <button
                    onClick={() => deleteEnvironment(env)}
                    className="text-red-500 hover:text-red-700 ml-2"
                    title="Delete environment"
                  >
                    ×
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 md:col-span-2">
          {selectedEnvironment ? (
            <>
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">
                  {selectedEnvironment.name}{' '}
                  <span className={`text-xs px-2 py-1 rounded-full ${getEnvironmentTypeColor(selectedEnvironment.type)}`}>
                    {getEnvironmentTypeLabel(selectedEnvironment.type)}
                  </span>
                </h2>
                <button
                  onClick={resetEnvironment}
                  className="bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600"
                >
                  Reset
                </button>
              </div>

              <div className="mb-6">
                <h3 className="font-medium mb-2">Current Observation:</h3>
                <pre className="bg-gray-100 p-3 rounded overflow-auto max-h-40">
                  {observation ? JSON.stringify(observation, null, 2) : 'Loading...'}
                </pre>
              </div>

              <div className="mb-6">
                <h3 className="font-medium mb-2">Execute Action:</h3>
                <textarea
                  value={actionInput}
                  onChange={(e) => setActionInput(e.target.value)}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline mb-2 h-32"
                  placeholder='{"operation": "example", "params": {"key": "value"}}'
                />
                <button
                  onClick={executeAction}
                  className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                >
                  Execute
                </button>
              </div>

              {actionResult && (
                <div>
                  <h3 className="font-medium mb-2">Action Result:</h3>
                  <pre className="bg-gray-100 p-3 rounded overflow-auto max-h-40">
                    {JSON.stringify(actionResult, null, 2)}
                  </pre>
                </div>
              )}
            </>
          ) : (
            <p className="text-gray-500">Select an environment to view details</p>
          )}
        </div>
      </div>
    </div>
  );
} 