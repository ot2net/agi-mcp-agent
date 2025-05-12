'use client';

import { SystemStatusCard } from '@/components/SystemStatusCard';
import { Card } from '@/components/base/Card';
import { HiOutlineCode, HiOutlineChartBar, HiOutlineServer, HiOutlineDatabase } from 'react-icons/hi';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      <div className="text-center space-y-4 mb-8">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white">
          <span className="text-blue-600 dark:text-blue-400">AGI-MCP</span> Agent System
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          A multi-cloud platform for orchestrating intelligent agents
        </p>
      </div>

      <SystemStatusCard />

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mt-8">
        <Link href="/agents" className="block">
          <Card
            title="Agents"
            description="Configure and manage AI agents"
            icon={<HiOutlineServer className="w-6 h-6" />}
            className="h-full hover:border-blue-500 cursor-pointer"
          >
            <p className="text-gray-600 dark:text-gray-400">
              Create, monitor, and control the agents that power your AI ecosystem.
            </p>
          </Card>
        </Link>

        <Link href="/tasks" className="block">
          <Card
            title="Tasks"
            description="Create and manage agent tasks"
            icon={<HiOutlineChartBar className="w-6 h-6" />}
            className="h-full hover:border-blue-500 cursor-pointer"
          >
            <p className="text-gray-600 dark:text-gray-400">
              Create tasks for agents to execute, monitor progress, and view completed task results.
            </p>
          </Card>
        </Link>

        <Link href="/environments" className="block">
          <Card
            title="Environments"
            description="Configure agent execution environments"
            icon={<HiOutlineDatabase className="w-6 h-6" />}
            className="h-full hover:border-blue-500 cursor-pointer"
          >
            <p className="text-gray-600 dark:text-gray-400">
              Define environments where agents can securely access tools, data sources, and external services.
            </p>
          </Card>
        </Link>
      </div>

      <div className="mt-12 border-t border-gray-200 dark:border-gray-700 pt-8">
        <h2 className="text-2xl font-bold mb-4">
          System Overview
        </h2>
        <Card
          title="About the MCP Architecture"
          description="Learn about the Multi-Cloud Platform"
          icon={<HiOutlineCode className="w-6 h-6" />}
        >
          <div className="prose dark:prose-invert max-w-none">
            <p>
              The Master Control Program (MCP) is designed as a centralized orchestration layer that manages agents,
              tasks, and environments in a secure and scalable manner.
            </p>
            <p className="mt-4">
              Key components include:
            </p>
            <ul className="list-disc pl-5 mt-2">
              <li>Agent management for different AI capabilities</li>
              <li>Task scheduling and dependency management</li>
              <li>Secure environment isolation</li>
              <li>Cross-cloud integration</li>
              <li>Real-time monitoring and logging</li>
            </ul>
          </div>
        </Card>
      </div>
    </div>
  );
}
