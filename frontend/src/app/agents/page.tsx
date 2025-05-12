'use client';

import { useState, useEffect } from 'react';
import { AgentForm } from '@/components/AgentForm';
import { AgentList } from '@/components/AgentList';
import { LoadingState } from '@/components/LoadingState';
import { Agent } from '@/types/agent';
import { Card } from '@/components/base/Card';
import { Button } from '@/components/base/Button';
import { HiOutlinePlus, HiOutlineUserGroup, HiOutlineRefresh } from 'react-icons/hi';

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await fetch('/api/agents');
      if (!response.ok) {
        throw new Error('Failed to fetch agents');
      }
      const data = await response.json();
      setAgents(data);
      setError(null);
    } catch (err) {
      setError('Failed to load agents. Please try again later.');
      console.error('Error fetching agents:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateAgent = async (agentData: Omit<Agent, 'id' | 'created_at' | 'updated_at'>) => {
    try {
      const response = await fetch('/api/agents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(agentData),
      });

      if (!response.ok) {
        throw new Error('Failed to create agent');
      }

      const newAgent = await response.json();
      setAgents(prevAgents => [...prevAgents, newAgent]);
      setError(null);
      return Promise.resolve();
    } catch (err) {
      console.error('Error creating agent:', err);
      setError('Failed to create agent. Please try again.');
      return Promise.reject(err);
    }
  };

  const handleDeleteAgent = async (agentId: number) => {
    try {
      const response = await fetch(`/api/agents/${agentId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete agent');
      }

      setAgents(prevAgents => prevAgents.filter(agent => agent.id !== agentId));
      setError(null);
    } catch (err) {
      console.error('Error deleting agent:', err);
      setError('Failed to delete agent. Please try again.');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Agents</h1>
        <Button
          variant="outline"
          onClick={fetchAgents}
          className="animate-fade-in"
          icon={<HiOutlineRefresh className="w-5 h-5" />}
        >
          Refresh
        </Button>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <Card
            title="Create New Agent"
            description="Configure and create a new AI agent"
            icon={<HiOutlinePlus className="w-6 h-6" />}
            showDivider
          >
            <AgentForm onSubmit={handleCreateAgent} />
          </Card>
        </div>
        <div>
          <Card
            title="Agent List"
            description="View and manage your AI agents"
            icon={<HiOutlineUserGroup className="w-6 h-6" />}
            showDivider
          >
            {error && (
              <div className="mb-4 rounded-lg bg-red-50 dark:bg-red-900/10 p-4 border border-red-200 dark:border-red-800">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-red-800 dark:text-red-200">{error}</p>
                  </div>
                </div>
              </div>
            )}
            <div className="animate-fade-in">
              {isLoading ? <LoadingState /> : <AgentList agents={agents} onDelete={handleDeleteAgent} />}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
} 