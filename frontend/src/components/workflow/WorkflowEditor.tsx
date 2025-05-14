'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
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
  NodeProps,
  ConnectionMode,
  Handle,
  Position,
  ConnectionLineType,
  BackgroundVariant,
  EdgeProps,
  getBezierPath
} from 'reactflow';
import 'reactflow/dist/style.css';
import { HiOutlineLightningBolt, HiOutlineDatabase, HiOutlineCode, HiLink, HiTrash } from 'react-icons/hi';
import { Button } from '@/components/base/Button';
import { Input } from '@/components/base/Input';
import { Select } from '@/components/base/Select';
import { Card } from '@/components/base/Card';
import { getEnvironments, getAgents } from '@/api/workflow';

// Custom edge component with animated flow
const CustomEdge = ({ id, source, target, sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition, style = {}, markerEnd }: EdgeProps) => {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
    curvature: 0.25,
  });

  return (
    <>
      <path
        id={id}
        className="react-flow__edge-path-bg"
        d={edgePath}
        strokeWidth={style.strokeWidth as number + 2 || 3}
        stroke="rgba(255, 255, 255, 0.5)"
        fill="none"
      />
      <path
        id={id}
        className="react-flow__edge-path"
        d={edgePath}
        strokeWidth={style.strokeWidth as number || 1}
        stroke={style.stroke as string || '#3B82F6'}
        strokeOpacity={style.strokeOpacity as number || 0.75}
        fill="none"
        strokeDasharray={style.strokeDasharray as string || ''}
        markerEnd={markerEnd}
      />
      <path
        id={id + '-animation'}
        className="react-flow__edge-path-flow"
        d={edgePath}
        strokeWidth={(style.strokeWidth as number || 1) - 0.3}
        stroke={style.stroke as string || '#3B82F6'}
        fill="none"
        strokeDasharray="5 10"
        strokeOpacity={0.8}
        style={{
          animation: 'flowAnimation 30s linear infinite',
        }}
      />
    </>
  );
};

// Node type definitions
const NODE_TYPES = {
  environment: 'environment_action',
  agent: 'agent_task',
  conditional: 'conditional',
  parallel: 'parallel',
  mcp_agent: 'mcp_agent',
  browser_action: 'browser_action'
};

// Custom node components
const handleStyle = {
  background: '#fff',
  border: '2px solid #3B82F6',
  width: 10,
  height: 10,
  borderRadius: '50%',
  zIndex: 10,
  transition: 'transform 0.2s ease, opacity 0.2s ease',
  opacity: 0.8,
};

const handleStyleHover = {
  ...handleStyle,
  transform: 'scale(1.3)',
  opacity: 1,
};

const EnvironmentNode = ({ data, selected }: NodeProps) => {
  return (
    <div className={`rounded-lg shadow-md overflow-hidden ${selected ? 'ring-2 ring-blue-500' : 'border border-gray-200 dark:border-gray-700'} bg-white dark:bg-gray-800 min-w-[240px]`}>
      <Handle 
        type="target" 
        position={Position.Top} 
        style={{ ...handleStyle, borderColor: '#10B981' }} 
        className="!w-auto !h-auto !bg-transparent !border-0 hover:!transform hover:!scale-125"
        isConnectableStart={false} 
      />
      <div className="bg-green-50 dark:bg-green-900/20 px-4 py-3 border-b border-green-100 dark:border-green-800/50">
        <div className="flex items-center">
          <div className="p-2 rounded-lg bg-green-100 dark:bg-green-800/50 mr-3">
            <HiOutlineDatabase className="text-green-600 dark:text-green-400 w-5 h-5" />
          </div>
          <div className="font-bold text-gray-800 dark:text-white">{data.label}</div>
        </div>
      </div>
      <div className="p-3">
        <div className="flex items-center text-xs text-gray-500 dark:text-gray-400 mb-2">
          <div className="font-medium w-24">Environment:</div>
          <div className="flex-1 bg-gray-50 dark:bg-gray-700/50 px-2 py-1 rounded">{data.environment || 'Not Set'}</div>
        </div>
        <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
          <div className="font-medium w-24">Operation:</div>
          <div className="flex-1 bg-gray-50 dark:bg-gray-700/50 px-2 py-1 rounded">{data.action?.operation || 'Not Set'}</div>
        </div>
      </div>
      <Handle 
        type="source" 
        position={Position.Bottom} 
        style={{ ...handleStyle, borderColor: '#10B981' }} 
        className="!w-auto !h-auto !bg-transparent !border-0 hover:!transform hover:!scale-125"
      />
    </div>
  );
};

const AgentNode = ({ data, selected }: NodeProps) => {
  return (
    <div className={`rounded-lg shadow-md overflow-hidden ${selected ? 'ring-2 ring-blue-500' : 'border border-gray-200 dark:border-gray-700'} bg-white dark:bg-gray-800 min-w-[240px]`}>
      <Handle 
        type="target" 
        position={Position.Top} 
        style={{ ...handleStyle, borderColor: '#3B82F6' }} 
        className="!w-auto !h-auto !bg-transparent !border-0 hover:!transform hover:!scale-125"
        isConnectableStart={false}
      />
      <div className="bg-blue-50 dark:bg-blue-900/20 px-4 py-3 border-b border-blue-100 dark:border-blue-800/50">
        <div className="flex items-center">
          <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-800/50 mr-3">
            <HiOutlineLightningBolt className="text-blue-600 dark:text-blue-400 w-5 h-5" />
          </div>
          <div className="font-bold text-gray-800 dark:text-white">{data.label}</div>
        </div>
      </div>
      <div className="p-3">
        <div className="flex items-center text-xs text-gray-500 dark:text-gray-400 mb-2">
          <div className="font-medium w-24">Agent:</div>
          <div className="flex-1 bg-gray-50 dark:bg-gray-700/50 px-2 py-1 rounded">{data.agent || 'Not Set'}</div>
        </div>
        <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
          <div className="font-medium w-24">Task:</div>
          <div className="flex-1 bg-gray-50 dark:bg-gray-700/50 px-2 py-1 rounded">{data.description || 'Not Set'}</div>
        </div>
      </div>
      <Handle 
        type="source" 
        position={Position.Bottom} 
        style={{ ...handleStyle, borderColor: '#3B82F6' }} 
        className="!w-auto !h-auto !bg-transparent !border-0 hover:!transform hover:!scale-125"
      />
    </div>
  );
};

const ConditionalNode = ({ data, selected }: NodeProps) => {
  return (
    <div className={`rounded-lg shadow-md ${selected ? 'ring-2 ring-blue-500' : ''} bg-white dark:bg-gray-800 min-w-[240px]`}>
      <Handle 
        type="target" 
        position={Position.Top} 
        style={{ ...handleStyle, borderColor: '#F59E0B' }} 
        className="!w-auto !h-auto !bg-transparent !border-0 hover:!transform hover:!scale-125"
        isConnectableStart={false}
      />
      
      {/* Diamond header */}
      <div className="flex justify-center -mt-3 mb-2">
        <div className="h-16 w-16 bg-yellow-100 dark:bg-yellow-800/30 rotate-45 flex items-center justify-center shadow-md border border-yellow-200 dark:border-yellow-700">
          <div className="-rotate-45 flex flex-col items-center">
            <HiOutlineCode className="text-yellow-600 dark:text-yellow-400 w-6 h-6 mb-1" />
          </div>
        </div>
      </div>
      
      {/* Content */}
      <div className="px-4 pb-4 pt-1">
        <div className="font-medium text-center text-gray-800 dark:text-white mb-2">{data.label}</div>
        <div className="text-xs text-gray-500 dark:text-gray-400 mb-3 text-center border border-dashed border-gray-200 dark:border-gray-700 p-2 rounded bg-gray-50 dark:bg-gray-900/50">
          {data.condition || 'Set condition expression...'}
        </div>
        
        {/* Branches */}
        <div className="grid grid-cols-2 gap-2 mt-2">
          <div className="text-xs px-3 py-1.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded text-center font-medium">
            True
          </div>
          <div className="text-xs px-3 py-1.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded text-center font-medium">
            False
          </div>
        </div>
      </div>
      
      {/* Multiple output handles for true/false paths */}
      <Handle 
        type="source" 
        position={Position.Bottom} 
        id="true" 
        style={{ ...handleStyle, borderColor: '#22C55E', left: '30%' }} 
        className="!w-auto !h-auto !bg-transparent !border-0 hover:!transform hover:!scale-125"
      />
      <Handle 
        type="source" 
        position={Position.Bottom} 
        id="false" 
        style={{ ...handleStyle, borderColor: '#EF4444', left: '70%' }} 
        className="!w-auto !h-auto !bg-transparent !border-0 hover:!transform hover:!scale-125"
      />
    </div>
  );
};

const MCPAgentNode = ({ data, selected }: NodeProps) => {
  return (
    <div className={`rounded-lg shadow-md overflow-hidden ${selected ? 'ring-2 ring-blue-500' : 'border border-gray-200 dark:border-gray-700'} bg-white dark:bg-gray-800 min-w-[240px]`}>
      <Handle 
        type="target" 
        position={Position.Top} 
        style={{ ...handleStyle, borderColor: '#8B5CF6' }} 
        className="!w-auto !h-auto !bg-transparent !border-0 hover:!transform hover:!scale-125"
        isConnectableStart={false}
      />
      <div className="bg-purple-50 dark:bg-purple-900/20 px-4 py-3 border-b border-purple-100 dark:border-purple-800/50">
        <div className="flex items-center">
          <div className="p-2 rounded-lg bg-purple-100 dark:bg-purple-800/50 mr-3">
            <HiOutlineLightningBolt className="text-purple-600 dark:text-purple-400 w-5 h-5" />
          </div>
          <div className="font-bold text-gray-800 dark:text-white">{data.label}</div>
        </div>
      </div>
      <div className="p-3">
        <div className="flex items-center text-xs text-gray-500 dark:text-gray-400 mb-2">
          <div className="font-medium w-24">MCP Server:</div>
          <div className="flex-1 bg-gray-50 dark:bg-gray-700/50 px-2 py-1 rounded">{data.mcp_server || 'Not Set'}</div>
        </div>
        <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
          <div className="font-medium w-24">Tool:</div>
          <div className="flex-1 bg-gray-50 dark:bg-gray-700/50 px-2 py-1 rounded">{data.tool || 'Not Set'}</div>
        </div>
      </div>
      <Handle 
        type="source" 
        position={Position.Bottom} 
        style={{ ...handleStyle, borderColor: '#8B5CF6' }} 
        className="!w-auto !h-auto !bg-transparent !border-0 hover:!transform hover:!scale-125"
      />
    </div>
  );
};

const BrowserActionNode = ({ data, selected }: NodeProps) => {
  return (
    <div className={`rounded-lg shadow-md overflow-hidden ${selected ? 'ring-2 ring-blue-500' : 'border border-gray-200 dark:border-gray-700'} bg-white dark:bg-gray-800 min-w-[240px]`}>
      <Handle 
        type="target" 
        position={Position.Top} 
        style={{ ...handleStyle, borderColor: '#6366F1' }} 
        className="!w-auto !h-auto !bg-transparent !border-0 hover:!transform hover:!scale-125"
        isConnectableStart={false}
      />
      <div className="bg-indigo-50 dark:bg-indigo-900/20 px-4 py-3 border-b border-indigo-100 dark:border-indigo-800/50">
        <div className="flex items-center">
          <div className="p-2 rounded-lg bg-indigo-100 dark:bg-indigo-800/50 mr-3">
            <HiOutlineDatabase className="text-indigo-600 dark:text-indigo-400 w-5 h-5" />
          </div>
          <div className="font-bold text-gray-800 dark:text-white">{data.label}</div>
        </div>
      </div>
      <div className="p-3">
        <div className="flex items-center text-xs text-gray-500 dark:text-gray-400 mb-2">
          <div className="font-medium w-24">Action:</div>
          <div className="flex-1 bg-gray-50 dark:bg-gray-700/50 px-2 py-1 rounded">{data.browser_action || 'Not Set'}</div>
        </div>
        <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
          <div className="font-medium w-24">URL:</div>
          <div className="flex-1 bg-gray-50 dark:bg-gray-700/50 px-2 py-1 rounded overflow-hidden text-ellipsis">{data.url || 'Not Set'}</div>
        </div>
      </div>
      <Handle 
        type="source" 
        position={Position.Bottom} 
        style={{ ...handleStyle, borderColor: '#6366F1' }} 
        className="!w-auto !h-auto !bg-transparent !border-0 hover:!transform hover:!scale-125"
      />
    </div>
  );
};

const nodeTypes = {
  environment: EnvironmentNode,
  agent: AgentNode,
  conditional: ConditionalNode,
  mcp_agent: MCPAgentNode,
  browser_action: BrowserActionNode
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
  
  // Connection mode
  const [connectionMode, setConnectionMode] = useState<ConnectionMode>(ConnectionMode.Loose);
  
  // Environment and agent lists
  const [environments, setEnvironments] = useState<any[]>([]);
  const [agents, setAgents] = useState<any[]>([]);
  
  // Workflow metadata
  const [workflowName, setWorkflowName] = useState(initialWorkflow?.name || 'New Workflow');
  const [workflowDescription, setWorkflowDescription] = useState(initialWorkflow?.description || '');
  
  // Node property form state
  const [nodeConfig, setNodeConfig] = useState<any>({});

  // Editor modes
  const [isConnectionMode, setIsConnectionMode] = useState(false);
  const [isDeletionMode, setIsDeletionMode] = useState(false);

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
      } else if (step.type === NODE_TYPES.mcp_agent) {
        nodeType = 'mcp_agent';
      } else if (step.type === NODE_TYPES.browser_action) {
        nodeType = 'browser_action';
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
      } else if (type === 'mcp_agent') {
        stepType = NODE_TYPES.mcp_agent;
      } else if (type === 'browser_action') {
        stepType = NODE_TYPES.browser_action;
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
  const addNode = (type: string, connectTo?: Node) => {
    const newId = `${type}-${Date.now()}`;
    let newNode: Node = {
      id: newId,
      type,
      position: { 
        x: connectTo ? connectTo.position.x : 250 + Math.random() * 100, 
        y: connectTo ? connectTo.position.y + 220 : 100 + nodes.length * 120 + Math.random() * 50 
      },
      data: { label: '' }
    };
    
    // Set default values based on node type
    switch(type) {
      case 'environment':
        newNode.data = { 
          label: 'New Environment Action',
          environment: environments.length > 0 ? environments[0].id : '',
          action: { operation: 'read' },
          output_key: `env_result_${nodes.length + 1}`
        };
        break;
      case 'agent':
        newNode.data = { 
          label: 'New Agent Task',
          agent: agents.length > 0 ? agents[0].id : '',
          description: 'Perform a task',
          task_input: { prompt: '' },
          output_key: `task_result_${nodes.length + 1}`
        };
        break;
      case 'conditional':
        newNode.data = { 
          label: 'Condition Check',
          condition: '',
          if_true: '',
          if_false: ''
        };
        break;
      case 'mcp_agent':
        newNode.data = { 
          label: 'MCP Agent',
          mcp_server: 'http://localhost:8000',
          tool: '',
          output_key: `mcp_result_${nodes.length + 1}`
        };
        break;
      case 'browser_action':
        newNode.data = { 
          label: 'Browser Action',
          browser_action: 'navigate',
          url: '',
          output_key: `browser_result_${nodes.length + 1}`
        };
        break;
    }
    
    const updatedNodes = [...nodes, newNode];
    setNodes(updatedNodes);
    
    // Add connection if connectTo is provided
    if (connectTo) {
      const newEdge = {
        id: `${connectTo.id}-${newId}`,
        source: connectTo.id,
        target: newId,
        type: 'smoothstep',
        animated: true,
        style: { stroke: '#64748B', strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, width: 20, height: 20 }
      };
      setEdges(edges => [...edges, newEdge]);
    }
    
    setSelectedNode(newNode);
    setNodeConfig(newNode.data);
    
    return newNode;
  };

  // Add flow animation style to head
  useEffect(() => {
    const styleEl = document.createElement('style');
    styleEl.innerHTML = `
      @keyframes flowAnimation {
        0% {
          stroke-dashoffset: 100;
        }
        100% {
          stroke-dashoffset: 0;
        }
      }
    `;
    document.head.appendChild(styleEl);
    return () => {
      document.head.removeChild(styleEl);
    };
  }, []);

  // When connection changes
  const onConnect = useCallback((params: Connection) => {
    const newEdge = {
      ...params,
      type: 'custom', // Use our custom edge
      animated: false, // We handle animation ourselves
      style: { 
        stroke: '#3B82F6', 
        strokeWidth: 2,
        strokeOpacity: 0.75
      },
      markerEnd: { 
        type: MarkerType.ArrowClosed,
        width: 20,
        height: 20,
        color: '#3B82F6'
      }
    };
    setEdges(eds => addEdge(newEdge, eds));
  }, []);

  // Delete an edge
  const onEdgeClick = useCallback((event: React.MouseEvent, edge: Edge) => {
    if (isDeletionMode) {
      setEdges(edges => edges.filter(e => e.id !== edge.id));
    }
  }, [isDeletionMode]);

  // Delete a node
  const onNodeDoubleClick = useCallback((event: React.MouseEvent, node: Node) => {
    if (isDeletionMode) {
      // Remove connected edges
      setEdges(edges => edges.filter(e => e.source !== node.id && e.target !== node.id));
      
      // Remove the node
      setNodes(nodes => nodes.filter(n => n.id !== node.id));
      
      // Clear selection if the selected node is deleted
      if (selectedNode && selectedNode.id === node.id) {
        setSelectedNode(null);
      }
    }
  }, [isDeletionMode, selectedNode]);

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
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                Name
              </label>
              <Input 
                value={nodeConfig.label || ''} 
                onChange={e => updateNodeConfig('label', e.target.value)}
                className="text-sm"
                placeholder="Enter node name"
              />
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                Environment
              </label>
              <Select
                value={nodeConfig.environment || ''}
                onChange={e => updateNodeConfig('environment', e.target.value)}
                options={environments.map(env => ({ value: env.id, label: env.name }))}
                className="text-sm"
              />
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
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
                className="text-sm"
              />
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                Output Key
              </label>
              <Input 
                value={nodeConfig.output_key || ''} 
                onChange={e => updateNodeConfig('output_key', e.target.value)}
                placeholder="Variable name for referencing"
                className="text-sm"
              />
            </div>
            
            {/* Show different parameters based on operation type */}
            {nodeConfig.action?.operation === 'read' && (
              <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-100 dark:border-blue-800/30">
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                  Path
                </label>
                <Input 
                  value={nodeConfig.action?.path || ''} 
                  onChange={e => updateNodeConfig('action', { ...nodeConfig.action, path: e.target.value })}
                  placeholder="File path"
                  className="text-sm"
                />
              </div>
            )}
            
            {nodeConfig.action?.operation === 'write' && (
              <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-100 dark:border-blue-800/30 space-y-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                    Path
                  </label>
                  <Input 
                    value={nodeConfig.action?.path || ''} 
                    onChange={e => updateNodeConfig('action', { ...nodeConfig.action, path: e.target.value })}
                    placeholder="File path"
                    className="text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                    Content
                  </label>
                  <textarea 
                    value={nodeConfig.action?.content || ''} 
                    onChange={e => updateNodeConfig('action', { ...nodeConfig.action, content: e.target.value })}
                    placeholder="File content"
                    className="w-full h-20 px-3 py-2 text-sm border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>
              </div>
            )}
            
            <Button onClick={applyNodeConfig} size="sm" className="w-full justify-center mt-2">Apply Changes</Button>
          </div>
        );
        
      case 'agent':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                Name
              </label>
              <Input 
                value={nodeConfig.label || ''} 
                onChange={e => updateNodeConfig('label', e.target.value)}
                className="text-sm"
                placeholder="Enter node name"
              />
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                Agent
              </label>
              <Select
                value={nodeConfig.agent || ''}
                onChange={e => updateNodeConfig('agent', e.target.value)}
                options={agents.map(agent => ({ value: agent.id, label: agent.name }))}
                className="text-sm"
              />
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                Description
              </label>
              <Input 
                value={nodeConfig.description || ''} 
                onChange={e => updateNodeConfig('description', e.target.value)}
                className="text-sm"
                placeholder="Enter task description"
              />
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                Input Prompt
              </label>
              <textarea 
                value={nodeConfig.task_input?.prompt || ''} 
                onChange={e => updateNodeConfig('task_input', { ...nodeConfig.task_input, prompt: e.target.value })}
                placeholder="Use {{variable}} for references"
                className="w-full h-20 px-3 py-2 text-sm border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                Output Key
              </label>
              <Input 
                value={nodeConfig.output_key || ''} 
                onChange={e => updateNodeConfig('output_key', e.target.value)}
                placeholder="Variable name for referencing"
                className="text-sm"
              />
            </div>
            
            <Button onClick={applyNodeConfig} size="sm" className="w-full justify-center mt-2">Apply Changes</Button>
          </div>
        );
        
      case 'conditional':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                Name
              </label>
              <Input 
                value={nodeConfig.label || ''} 
                onChange={e => updateNodeConfig('label', e.target.value)}
                className="text-sm"
                placeholder="Enter node name"
              />
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                Condition Expression
              </label>
              <div className="relative">
                <textarea 
                  value={nodeConfig.condition || ''} 
                  onChange={e => updateNodeConfig('condition', e.target.value)}
                  placeholder="{{result.success}} or len({{items}}) > 0"
                  className="w-full h-20 px-3 py-2 text-sm border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white bg-yellow-50/50 dark:bg-yellow-900/10"
                />
                <div className="absolute top-1 right-1">
                  <div className="w-5 h-5 bg-yellow-100 dark:bg-yellow-800 rotate-45 flex items-center justify-center">
                    <HiOutlineCode className="text-yellow-600 dark:text-yellow-400 w-3 h-3 -rotate-45" />
                  </div>
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5 flex items-center">
                  <div className="w-2 h-2 bg-green-400 rounded-full mr-1.5"></div>
                  If True
                </label>
                <Select
                  value={nodeConfig.if_true || ''}
                  onChange={e => updateNodeConfig('if_true', e.target.value)}
                  options={nodes.filter(n => n.id !== selectedNode.id).map(n => ({ value: n.id, label: n.data.label }))}
                  className="text-sm"
                />
              </div>
              
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5 flex items-center">
                  <div className="w-2 h-2 bg-red-400 rounded-full mr-1.5"></div>
                  If False
                </label>
                <Select
                  value={nodeConfig.if_false || ''}
                  onChange={e => updateNodeConfig('if_false', e.target.value)}
                  options={nodes.filter(n => n.id !== selectedNode.id).map(n => ({ value: n.id, label: n.data.label }))}
                  className="text-sm"
                />
              </div>
            </div>
            
            <Button onClick={applyNodeConfig} size="sm" className="w-full justify-center mt-2">Apply Changes</Button>
          </div>
        );
        
      case 'mcp_agent':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                Name
              </label>
              <Input 
                value={nodeConfig.label || ''} 
                onChange={e => updateNodeConfig('label', e.target.value)}
                className="text-sm"
                placeholder="Enter node name"
              />
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                MCP Server
              </label>
              <Input 
                value={nodeConfig.mcp_server || ''} 
                onChange={e => updateNodeConfig('mcp_server', e.target.value)}
                className="text-sm"
                placeholder="Server URL"
              />
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                Tool
              </label>
              <Input 
                value={nodeConfig.tool || ''} 
                onChange={e => updateNodeConfig('tool', e.target.value)}
                className="text-sm"
                placeholder="Tool name"
              />
            </div>
            
            <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-100 dark:border-purple-800/30 text-xs text-gray-600 dark:text-gray-400 mt-2">
              The MCP Agent allows you to connect to Model Context Protocol servers to extend functionality.
            </div>
            
            <Button onClick={applyNodeConfig} size="sm" className="w-full justify-center mt-2">Apply Changes</Button>
          </div>
        );
        
      case 'browser_action':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                Name
              </label>
              <Input 
                value={nodeConfig.label || ''} 
                onChange={e => updateNodeConfig('label', e.target.value)}
                className="text-sm"
                placeholder="Enter node name"
              />
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                Action
              </label>
              <Select
                value={nodeConfig.browser_action || ''}
                onChange={e => updateNodeConfig('browser_action', e.target.value)}
                options={[
                  { value: 'navigate', label: 'Navigate' },
                  { value: 'click', label: 'Click Element' },
                  { value: 'extract', label: 'Extract Data' },
                  { value: 'search', label: 'Search' }
                ]}
                className="text-sm"
              />
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                URL
              </label>
              <Input 
                value={nodeConfig.url || ''} 
                onChange={e => updateNodeConfig('url', e.target.value)}
                placeholder="https://example.com"
                className="text-sm"
              />
            </div>
            
            <Button onClick={applyNodeConfig} size="sm" className="w-full justify-center mt-2">Apply Changes</Button>
          </div>
        );
        
      default:
        return null;
    }
  };

  // Define edge types
  const edgeTypes = {
    custom: CustomEdge,
  };

  return (
    <div className="flex flex-col h-[calc(100vh-64px)] bg-gray-50 dark:bg-gray-900">
      {/* Header area */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-gray-900 dark:text-white">
              {workflowName || 'New Workflow'}
            </h1>
          </div>
          <div className="flex items-center space-x-3">
            {/* Connection mode toggle */}
            <Button 
              onClick={() => {
                setIsConnectionMode(!isConnectionMode);
                setIsDeletionMode(false);
              }}
              size="sm"
              variant={isConnectionMode ? "default" : "outline"}
              className="flex items-center space-x-1.5"
            >
              <HiLink className="w-4 h-4" />
              <span>Connect Mode</span>
            </Button>
            
            {/* Deletion mode toggle */}
            <Button 
              onClick={() => {
                setIsDeletionMode(!isDeletionMode);
                setIsConnectionMode(false);
              }}
              size="sm"
              variant={isDeletionMode ? "destructive" : "outline"}
              className="flex items-center space-x-1.5"
            >
              <HiTrash className="w-4 h-4" />
              <span>Delete Mode</span>
            </Button>
            
            <Button 
              onClick={saveWorkflow}
              className="px-4"
            >
              Save Workflow
            </Button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left sidebar */}
        <div className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 overflow-y-auto">
          <div className="p-4">
            {/* Components section */}
            <div className="mb-6">
              <h2 className="text-xs uppercase tracking-wider font-semibold text-gray-500 dark:text-gray-400 mb-3 px-1">
                Components
              </h2>
              
              <div className="space-y-2">
                <div className="group relative">
                  <button
                    className="flex items-center w-full p-2.5 text-sm rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 group transition-colors border border-gray-100 dark:border-gray-700"
                    onClick={() => addNode('environment')}
                  >
                    <div className="p-1.5 rounded-lg bg-green-100 dark:bg-green-900/30 mr-3 group-hover:bg-green-200 dark:group-hover:bg-green-800/50 transition-colors">
                      <HiOutlineDatabase className="text-green-600 dark:text-green-400 w-4 h-4" />
                    </div>
                    <span className="font-medium">Environment Action</span>
                  </button>
                  
                  {/* Connect option only shown when a node is selected */}
                  {selectedNode && (
                    <button
                      className="absolute right-0 top-0 h-full px-2 hidden group-hover:flex items-center justify-center text-xs font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-r-lg"
                      onClick={() => addNode('environment', selectedNode)}
                      title="Add & connect to selected node"
                    >
                      <HiLink className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
                
                <div className="group relative">
                  <button
                    className="flex items-center w-full p-2.5 text-sm rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 group transition-colors border border-gray-100 dark:border-gray-700"
                    onClick={() => addNode('agent')}
                  >
                    <div className="p-1.5 rounded-lg bg-blue-100 dark:bg-blue-900/30 mr-3 group-hover:bg-blue-200 dark:group-hover:bg-blue-800/50 transition-colors">
                      <HiOutlineLightningBolt className="text-blue-600 dark:text-blue-400 w-4 h-4" />
                    </div>
                    <span className="font-medium">Agent Task</span>
                  </button>
                  
                  {selectedNode && (
                    <button
                      className="absolute right-0 top-0 h-full px-2 hidden group-hover:flex items-center justify-center text-xs font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-r-lg"
                      onClick={() => addNode('agent', selectedNode)}
                      title="Add & connect to selected node"
                    >
                      <HiLink className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
                
                <div className="group relative">
                  <button
                    className="flex items-center w-full p-2.5 text-sm rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 group transition-colors border border-gray-100 dark:border-gray-700"
                    onClick={() => addNode('conditional')}
                  >
                    <div className="w-7 h-7 flex items-center justify-center mr-3">
                      <div className="w-5 h-5 bg-yellow-100 dark:bg-yellow-900/30 rotate-45 group-hover:bg-yellow-200 dark:group-hover:bg-yellow-800/50 transition-colors flex items-center justify-center">
                        <HiOutlineCode className="text-yellow-600 dark:text-yellow-400 w-3 h-3 -rotate-45" />
                      </div>
                    </div>
                    <span className="font-medium">Conditional Branch</span>
                  </button>
                  
                  {selectedNode && (
                    <button
                      className="absolute right-0 top-0 h-full px-2 hidden group-hover:flex items-center justify-center text-xs font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-r-lg"
                      onClick={() => addNode('conditional', selectedNode)}
                      title="Add & connect to selected node"
                    >
                      <HiLink className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
                
                <div className="group relative">
                  <button
                    className="flex items-center w-full p-2.5 text-sm rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 group transition-colors border border-gray-100 dark:border-gray-700"
                    onClick={() => addNode('mcp_agent')}
                  >
                    <div className="p-1.5 rounded-lg bg-purple-100 dark:bg-purple-900/30 mr-3 group-hover:bg-purple-200 dark:group-hover:bg-purple-800/50 transition-colors">
                      <HiOutlineLightningBolt className="text-purple-600 dark:text-purple-400 w-4 h-4" />
                    </div>
                    <span className="font-medium">MCP Agent</span>
                  </button>
                  
                  {selectedNode && (
                    <button
                      className="absolute right-0 top-0 h-full px-2 hidden group-hover:flex items-center justify-center text-xs font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-r-lg"
                      onClick={() => addNode('mcp_agent', selectedNode)}
                      title="Add & connect to selected node"
                    >
                      <HiLink className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
                
                <div className="group relative">
                  <button
                    className="flex items-center w-full p-2.5 text-sm rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 group transition-colors border border-gray-100 dark:border-gray-700"
                    onClick={() => addNode('browser_action')}
                  >
                    <div className="p-1.5 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 mr-3 group-hover:bg-indigo-200 dark:group-hover:bg-indigo-800/50 transition-colors">
                      <HiOutlineDatabase className="text-indigo-600 dark:text-indigo-400 w-4 h-4" />
                    </div>
                    <span className="font-medium">Browser Action</span>
                  </button>
                  
                  {selectedNode && (
                    <button
                      className="absolute right-0 top-0 h-full px-2 hidden group-hover:flex items-center justify-center text-xs font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-r-lg"
                      onClick={() => addNode('browser_action', selectedNode)}
                      title="Add & connect to selected node"
                    >
                      <HiLink className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>
            </div>
            
            {/* Workflow settings section */}
            <div>
              <h2 className="text-xs uppercase tracking-wider font-semibold text-gray-500 dark:text-gray-400 mb-3 px-1">
                Workflow Settings
              </h2>
              
              <div className="space-y-4 bg-gray-50 dark:bg-gray-900 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                    Name
                  </label>
                  <Input 
                    value={workflowName}
                    onChange={e => setWorkflowName(e.target.value)}
                    className="text-sm py-1.5"
                    placeholder="Enter workflow name"
                  />
                </div>
                
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                    Description
                  </label>
                  <textarea 
                    value={workflowDescription}
                    onChange={e => setWorkflowDescription(e.target.value)}
                    placeholder="Describe the workflow purpose"
                    className="w-full h-20 px-3 py-2 text-sm border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Center edit area */}
        <div className="flex-1 relative bg-gray-100 dark:bg-gray-950">
          {isConnectionMode && (
            <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-white dark:bg-gray-800 p-3 rounded-lg z-10 shadow-md border border-blue-200 dark:border-blue-800">
              <div className="text-center text-sm text-blue-600 dark:text-blue-400 font-medium mb-2">
                Connection Mode
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
                Click and drag between nodes to create connections
              </div>
            </div>
          )}
          
          {isDeletionMode && (
            <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-white dark:bg-gray-800 p-3 rounded-lg z-10 shadow-md border border-red-200 dark:border-red-800">
              <div className="text-center text-sm text-red-600 dark:text-red-400 font-medium mb-2">
                Deletion Mode
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
                Double-click on nodes or click on edges to delete them
              </div>
            </div>
          )}
          
          {nodes.length === 0 && (
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center justify-center bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md border border-blue-100 dark:border-blue-900/30 z-10 w-96">
              <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-full mb-4">
                <HiOutlineDatabase className="w-8 h-8 text-blue-500" />
              </div>
              <h3 className="text-lg font-semibold mb-2 text-center">Create Your Workflow</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 text-center mb-5">
                Start by adding components from the left sidebar. Drag and connect them to create your workflow.
              </p>
              <div className="flex space-x-3">
                <button
                  className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition-colors"
                  onClick={() => addNode('environment')}
                >
                  Add Environment
                </button>
                <button
                  className="px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-lg text-sm font-medium transition-colors"
                  onClick={() => addNode('agent')}
                >
                  Add Agent
                </button>
              </div>
            </div>
          )}
          
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onNodeDoubleClick={onNodeDoubleClick}
            onEdgeClick={onEdgeClick}
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
            connectionMode={isConnectionMode ? ConnectionMode.Strict : ConnectionMode.Loose}
            fitView
            fitViewOptions={{ padding: 0.2 }}
            defaultEdgeOptions={{
              type: 'custom',
              animated: false,
              style: { 
                stroke: '#3B82F6', 
                strokeWidth: 2,
                strokeOpacity: 0.75
              },
              markerEnd: { 
                type: MarkerType.ArrowClosed,
                width: 20,
                height: 20,
                color: '#3B82F6'
              }
            }}
            connectionLineStyle={{ 
              stroke: '#3B82F6', 
              strokeWidth: 2, 
              strokeDasharray: '5,5',
              strokeOpacity: 0.75
            }}
            connectionLineType={ConnectionLineType.SmoothStep}
            snapToGrid={true}
            snapGrid={[10, 10]}
          >
            <Controls 
              position="bottom-right" 
              showInteractive={false} 
              style={{ 
                background: 'white', 
                borderRadius: '8px', 
                border: '1px solid #e5e7eb',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)'
              }} 
            />
            <MiniMap 
              nodeStrokeWidth={3}
              nodeColor={(node) => {
                switch (node.type) {
                  case 'environment': return '#10B981';
                  case 'agent': return '#3B82F6';
                  case 'conditional': return '#F59E0B';
                  case 'mcp_agent': return '#8B5CF6';
                  case 'browser_action': return '#6366F1';
                  default: return '#64748B';
                }
              }}
              style={{ 
                background: 'white', 
                borderRadius: '8px', 
                border: '1px solid #e5e7eb', 
                bottom: '120px',
                right: '10px',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)'
              }}
              maskColor="rgba(0, 0, 0, 0.05)"
            />
            <Background 
              color="#aaa" 
              gap={20} 
              size={1}
              variant={BackgroundVariant.Dots}
            />
            
            {/* Connection panel */}
            <Panel position="top-right" className={isConnectionMode ? 'bg-white dark:bg-gray-800 p-3 rounded-lg shadow-md border border-blue-100 dark:border-blue-800' : 'hidden'}>
              <div className="text-sm font-medium mb-2">Connection Options</div>
              <div className="flex items-center space-x-3">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setConnectionMode(ConnectionMode.Strict)}
                  className={connectionMode === ConnectionMode.Strict ? 'border-blue-500 text-blue-500' : ''}
                >
                  Strict
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setConnectionMode(ConnectionMode.Loose)}
                  className={connectionMode === ConnectionMode.Loose ? 'border-blue-500 text-blue-500' : ''}
                >
                  Loose
                </Button>
              </div>
            </Panel>
          </ReactFlow>
        </div>
        
        {/* Right configuration panel */}
        {selectedNode && (
          <div className="w-72 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 overflow-y-auto p-0">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
              <h3 className="font-medium">Node Configuration</h3>
            </div>
            <div className="p-4">
              {renderConfigPanel()}
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 