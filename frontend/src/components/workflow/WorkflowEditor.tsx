'use client';

import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, {
  addEdge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Panel,
  MarkerType,
  Node,
  Edge,
  Connection,
  NodeProps
} from 'reactflow';
import 'reactflow/dist/style.css';
import { HiOutlineLightningBolt, HiOutlineDatabase, HiOutlineCode } from 'react-icons/hi';
import { Button } from '@/components/base/Button';
import { Input } from '@/components/base/Input';
import { Select } from '@/components/base/Select';
import { Card } from '@/components/base/Card';
import { getEnvironments, getAgents } from '@/api/workflow';

// Node type definitions
const NODE_TYPES = {
  environment: 'environment_action',
  agent: 'agent_task',
  conditional: 'conditional',
  parallel: 'parallel'
};

// Custom node components
const EnvironmentNode = ({ data, selected }: NodeProps) => {
  return (
    <div className={`p-4 rounded-lg shadow-md border-2 ${selected ? 'border-blue-500' : 'border-gray-300'} bg-white dark:bg-gray-800 min-w-64`}>
      <div className="flex items-center mb-2">
        <div className="p-2 rounded-lg bg-green-100 dark:bg-green-900/20 mr-3">
          <HiOutlineDatabase className="text-green-600 dark:text-green-400 w-5 h-5" />
        </div>
        <div className="font-bold text-gray-800 dark:text-white">{data.label}</div>
      </div>
      <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">Environment: {data.environment}</div>
      <div className="text-xs text-gray-500 dark:text-gray-400">Operation: {data.action?.operation || 'Not Set'}</div>
    </div>
  );
};

const AgentNode = ({ data, selected }: NodeProps) => {
  return (
    <div className={`p-4 rounded-lg shadow-md border-2 ${selected ? 'border-blue-500' : 'border-gray-300'} bg-white dark:bg-gray-800 min-w-64`}>
      <div className="flex items-center mb-2">
        <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/20 mr-3">
          <HiOutlineLightningBolt className="text-blue-600 dark:text-blue-400 w-5 h-5" />
        </div>
        <div className="font-bold text-gray-800 dark:text-white">{data.label}</div>
      </div>
      <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">Agent: {data.agent}</div>
      <div className="text-xs text-gray-500 dark:text-gray-400">Task: {data.description || 'Not Set'}</div>
    </div>
  );
};

const ConditionalNode = ({ data, selected }: NodeProps) => {
  return (
    <div className={`p-4 rounded-lg shadow-md border-2 ${selected ? 'border-blue-500' : 'border-gray-300'} bg-white dark:bg-gray-800 min-w-64`}>
      <div className="flex items-center mb-2">
        <div className="p-2 rounded-lg bg-yellow-100 dark:bg-yellow-900/20 mr-3">
          <HiOutlineCode className="text-yellow-600 dark:text-yellow-400 w-5 h-5" />
        </div>
        <div className="font-bold text-gray-800 dark:text-white">{data.label}</div>
      </div>
      <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">Condition: {data.condition || 'Not Set'}</div>
      <div className="flex justify-between">
        <div className="text-xs text-green-500 dark:text-green-400">True</div>
        <div className="text-xs text-red-500 dark:text-red-400">False</div>
      </div>
    </div>
  );
};

const nodeTypes = {
  environment: EnvironmentNode,
  agent: AgentNode,
  conditional: ConditionalNode
};

interface WorkflowEditorProps {
  workflowId?: string;
  initialWorkflow?: any;
}

export default function WorkflowEditor({ workflowId, initialWorkflow }: WorkflowEditorProps) {
  // Node and edge states
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  
  // Environment and agent lists
  const [environments, setEnvironments] = useState<any[]>([]);
  const [agents, setAgents] = useState<any[]>([]);
  
  // Workflow metadata
  const [workflowName, setWorkflowName] = useState(initialWorkflow?.name || 'New Workflow');
  const [workflowDescription, setWorkflowDescription] = useState(initialWorkflow?.description || '');
  
  // Node property form state
  const [nodeConfig, setNodeConfig] = useState<any>({});

  // Load environment and agent data
  useEffect(() => {
    const loadData = async () => {
      try {
        const envData = await getEnvironments();
        const agentData = await getAgents();
        setEnvironments(envData);
        setAgents(agentData);
      } catch (err) {
        console.error('Error loading data:', err);
        // Add mock data for demonstration
        setEnvironments([
          { id: 'fs', name: 'File System', type: 'FileSystemEnvironment' },
          { id: 'memory', name: 'Memory Store', type: 'MemoryEnvironment' },
          { id: 'api', name: 'API Client', type: 'APIEnvironment' }
        ]);
        
        setAgents([
          { id: 'text', name: 'Text Generator', type: 'LLMAgent' },
          { id: 'vision', name: 'Vision Agent', type: 'VisionAgent' }
        ]);
      }
    };
    
    loadData();
  }, []);

  // If there is an initial workflow, load it
  useEffect(() => {
    if (initialWorkflow) {
      loadWorkflow(initialWorkflow);
    }
  }, [initialWorkflow]);

  // Load workflow
  const loadWorkflow = (workflow: any) => {
    setWorkflowName(workflow.name);
    setWorkflowDescription(workflow.description);
    
    // Convert steps to nodes
    const newNodes: Node[] = [];
    const newEdges: Edge[] = [];
    
    Object.entries(workflow.steps).forEach(([stepId, step]: [string, any], index) => {
      const position = { x: 250, y: 100 + index * 150 };
      
      let nodeType = 'environment';
      if (step.type === NODE_TYPES.agent) {
        nodeType = 'agent';
      } else if (step.type === NODE_TYPES.conditional) {
        nodeType = 'conditional';
      }
      
      newNodes.push({
        id: stepId,
        type: nodeType,
        position,
        data: {
          label: step.name,
          ...step
        }
      });
      
      // Add edges
      step.depends_on?.forEach((depId: string) => {
        newEdges.push({
          id: `${depId}-${stepId}`,
          source: depId,
          target: stepId,
          markerEnd: { type: MarkerType.ArrowClosed }
        });
      });
    });
    
    setNodes(newNodes);
    setEdges(newEdges);
  };

  // Convert current editor state to workflow definition
  const getWorkflowDefinition = () => {
    const steps: any = {};
    
    nodes.forEach(node => {
      const { id, data, type } = node;
      let stepType = NODE_TYPES.environment;
      
      if (type === 'agent') {
        stepType = NODE_TYPES.agent;
      } else if (type === 'conditional') {
        stepType = NODE_TYPES.conditional;
      }
      
      const dependsOn = edges
        .filter(edge => edge.target === id)
        .map(edge => edge.source);
      
      steps[id] = {
        name: data.label,
        type: stepType,
        depends_on: dependsOn,
        ...data
      };
      
      // Remove node-specific properties
      delete steps[id].label;
    });
    
    return {
      id: workflowId || `workflow-${Date.now()}`,
      name: workflowName,
      description: workflowDescription,
      steps
    };
  };

  // Add new node
  const addNode = (type: string) => {
    const newId = `${type}-${Date.now()}`;
    const newNode: Node = {
      id: newId,
      type,
      position: { x: 250, y: 100 + nodes.length * 150 },
      data: { label: `New ${type} Node` }
    };
    
    setNodes([...nodes, newNode]);
    setSelectedNode(newNode);
  };

  // When connection changes
  const onConnect = useCallback((params: Connection) => {
    setEdges(eds => addEdge({ ...params, markerEnd: { type: MarkerType.ArrowClosed } }, eds));
  }, []);

  // Node selection handler
  const onNodeClick = (_: any, node: Node) => {
    setSelectedNode(node);
    setNodeConfig(node.data);
  };

  // Update node configuration
  const updateNodeConfig = (prop: string, value: any) => {
    setNodeConfig({ ...nodeConfig, [prop]: value });
  };

  // Apply node configuration
  const applyNodeConfig = () => {
    if (!selectedNode) return;
    
    setNodes(nds =>
      nds.map(node => {
        if (node.id === selectedNode.id) {
          return {
            ...node,
            data: {
              ...nodeConfig
            }
          };
        }
        return node;
      })
    );
  };

  // Save workflow
  const saveWorkflow = async () => {
    const workflow = getWorkflowDefinition();
    console.log('Saving workflow:', workflow);
    
    // TODO: Implement save API call
    alert('Workflow save functionality will be enabled after API implementation');
  };

  // Different type node configuration panels
  const renderConfigPanel = () => {
    if (!selectedNode) return null;
    
    switch (selectedNode.type) {
      case 'environment':
        return (
          <div className="p-4 space-y-4">
            <h3 className="text-lg font-medium">Environment Action Configuration</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Name
              </label>
              <Input 
                value={nodeConfig.label || ''} 
                onChange={e => updateNodeConfig('label', e.target.value)}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Environment
              </label>
              <Select
                value={nodeConfig.environment || ''}
                onChange={e => updateNodeConfig('environment', e.target.value)}
                options={environments.map(env => ({ value: env.id, label: env.name }))}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Operation
              </label>
              <Select
                value={nodeConfig.action?.operation || ''}
                onChange={e => updateNodeConfig('action', { ...nodeConfig.action, operation: e.target.value })}
                options={[
                  { value: 'read', label: 'Read' },
                  { value: 'write', label: 'Write' },
                  { value: 'delete', label: 'Delete' },
                  { value: 'list', label: 'List' },
                  { value: 'store', label: 'Store' },
                  { value: 'retrieve', label: 'Retrieve' }
                ]}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Output Key
              </label>
              <Input 
                value={nodeConfig.output_key || ''} 
                onChange={e => updateNodeConfig('output_key', e.target.value)}
                placeholder="Variable name for referencing in subsequent steps"
              />
            </div>
            
            {/* Show different parameters based on operation type */}
            {nodeConfig.action?.operation === 'read' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Path
                </label>
                <Input 
                  value={nodeConfig.action?.path || ''} 
                  onChange={e => updateNodeConfig('action', { ...nodeConfig.action, path: e.target.value })}
                  placeholder="File path"
                />
              </div>
            )}
            
            {nodeConfig.action?.operation === 'write' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Path
                  </label>
                  <Input 
                    value={nodeConfig.action?.path || ''} 
                    onChange={e => updateNodeConfig('action', { ...nodeConfig.action, path: e.target.value })}
                    placeholder="File path"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Content
                  </label>
                  <textarea 
                    value={nodeConfig.action?.content || ''} 
                    onChange={e => updateNodeConfig('action', { ...nodeConfig.action, content: e.target.value })}
                    placeholder="File content"
                    className="w-full h-24 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>
              </>
            )}
            
            <Button onClick={applyNodeConfig}>Apply Changes</Button>
          </div>
        );
        
      case 'agent':
        return (
          <div className="p-4 space-y-4">
            <h3 className="text-lg font-medium">Agent Task Configuration</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Name
              </label>
              <Input 
                value={nodeConfig.label || ''} 
                onChange={e => updateNodeConfig('label', e.target.value)}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Agent
              </label>
              <Select
                value={nodeConfig.agent || ''}
                onChange={e => updateNodeConfig('agent', e.target.value)}
                options={agents.map(agent => ({ value: agent.id, label: agent.name }))}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Description
              </label>
              <Input 
                value={nodeConfig.description || ''} 
                onChange={e => updateNodeConfig('description', e.target.value)}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Input Prompt
              </label>
              <textarea 
                value={nodeConfig.task_input?.prompt || ''} 
                onChange={e => updateNodeConfig('task_input', { ...nodeConfig.task_input, prompt: e.target.value })}
                placeholder="Task prompt, you can use {{variable}} to reference values from previous steps"
                className="w-full h-24 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Output Key
              </label>
              <Input 
                value={nodeConfig.output_key || ''} 
                onChange={e => updateNodeConfig('output_key', e.target.value)}
                placeholder="Variable name for referencing in subsequent steps"
              />
            </div>
            
            <Button onClick={applyNodeConfig}>Apply Changes</Button>
          </div>
        );
        
      case 'conditional':
        return (
          <div className="p-4 space-y-4">
            <h3 className="text-lg font-medium">Condition Configuration</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Name
              </label>
              <Input 
                value={nodeConfig.label || ''} 
                onChange={e => updateNodeConfig('label', e.target.value)}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Condition Expression
              </label>
              <Input 
                value={nodeConfig.condition || ''} 
                onChange={e => updateNodeConfig('condition', e.target.value)}
                placeholder="Example: {{result.success}} or len({{items}}) > 0"
              />
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  If True
                </label>
                <Select
                  value={nodeConfig.if_true || ''}
                  onChange={e => updateNodeConfig('if_true', e.target.value)}
                  options={nodes.filter(n => n.id !== selectedNode.id).map(n => ({ value: n.id, label: n.data.label }))}
                />
              </div>
              
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  If False
                </label>
                <Select
                  value={nodeConfig.if_false || ''}
                  onChange={e => updateNodeConfig('if_false', e.target.value)}
                  options={nodes.filter(n => n.id !== selectedNode.id).map(n => ({ value: n.id, label: n.data.label }))}
                />
              </div>
            </div>
            
            <Button onClick={applyNodeConfig}>Apply Changes</Button>
          </div>
        );
        
      default:
        return null;
    }
  };

  return (
    <div className="flex h-[calc(100vh-64px)] bg-gray-50 dark:bg-gray-900">
      {/* Left sidebar */}
      <div className="w-64 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4 overflow-y-auto">
        <h2 className="text-lg font-bold mb-4">Workflow Components</h2>
        
        <div className="space-y-3 mb-6">
          <button
            className="flex items-center w-full p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            onClick={() => addNode('environment')}
          >
            <div className="p-2 rounded-lg bg-green-100 dark:bg-green-900/20 mr-3">
              <HiOutlineDatabase className="text-green-600 dark:text-green-400 w-5 h-5" />
            </div>
            <span>Environment Action</span>
          </button>
          
          <button
            className="flex items-center w-full p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            onClick={() => addNode('agent')}
          >
            <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/20 mr-3">
              <HiOutlineLightningBolt className="text-blue-600 dark:text-blue-400 w-5 h-5" />
            </div>
            <span>Agent Task</span>
          </button>
          
          <button
            className="flex items-center w-full p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            onClick={() => addNode('conditional')}
          >
            <div className="p-2 rounded-lg bg-yellow-100 dark:bg-yellow-900/20 mr-3">
              <HiOutlineCode className="text-yellow-600 dark:text-yellow-400 w-5 h-5" />
            </div>
            <span>Conditional Branch</span>
          </button>
        </div>
        
        <h2 className="text-lg font-bold mb-4">Workflow Properties</h2>
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Name
            </label>
            <Input 
              value={workflowName}
              onChange={e => setWorkflowName(e.target.value)}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Description
            </label>
            <textarea 
              value={workflowDescription}
              onChange={e => setWorkflowDescription(e.target.value)}
              className="w-full h-24 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>
          
          <Button 
            className="w-full justify-center" 
            onClick={saveWorkflow}
          >
            Save Workflow
          </Button>
        </div>
      </div>
      
      {/* Center edit area */}
      <div className="flex-1 relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
        >
          <Controls />
          <MiniMap />
          <Background />
          <Panel position="top-right">
            <div className="bg-white dark:bg-gray-800 p-2 rounded-lg shadow-md">
              <Button size="sm" onClick={saveWorkflow}>Save</Button>
            </div>
          </Panel>
        </ReactFlow>
      </div>
      
      {/* Right configuration panel */}
      {selectedNode && (
        <div className="w-80 border-l border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 overflow-y-auto">
          {renderConfigPanel()}
        </div>
      )}
    </div>
  );
} 