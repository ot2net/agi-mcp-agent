'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import ReactFlow, {
  addEdge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
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
import { HiOutlineLightningBolt, HiOutlineDatabase, HiOutlineCode, HiTrash, HiPencil } from 'react-icons/hi';
import { Button } from '@/components/base/Button';
import { Input } from '@/components/base/Input';
import { Select } from '@/components/base/Select';
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
    curvature: 0.3,
  });

  return (
    <>
      <path
        id={id}
        className="react-flow__edge-path-bg"
        d={edgePath}
        strokeWidth={(style.strokeWidth as number || 2) + 2}
        stroke="rgba(255, 255, 255, 0.8)"
        fill="none"
      />
      <path
        id={id}
        className="react-flow__edge-path"
        d={edgePath}
        strokeWidth={style.strokeWidth as number || 2}
        stroke={style.stroke as string || '#3B82F6'}
        strokeOpacity={style.strokeOpacity as number || 0.85}
        fill="none"
        strokeDasharray={style.strokeDasharray as string || ''}
        markerEnd={markerEnd}
      />
      <path
        id={id + '-animation'}
        className="react-flow__edge-path-flow"
        d={edgePath}
        strokeWidth={(style.strokeWidth as number || 2) - 0.5}
        stroke={style.stroke as string || '#3B82F6'}
        fill="none"
        strokeDasharray="4 8"
        strokeOpacity={0.7}
        style={{
          animation: 'flowAnimation 12s linear infinite',
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
  width: 7,
  height: 7,
  borderRadius: '50%',
  zIndex: 10,
  transition: 'all 0.2s ease',
  opacity: 0.6,
};

const EnvironmentNode = ({ data, selected }: NodeProps) => {
  return (
    <div className={`rounded-md shadow-sm overflow-hidden ${selected ? 'ring-2 ring-blue-500' : 'border border-gray-200 dark:border-gray-700'} bg-white dark:bg-gray-800 min-w-[180px] transition-all`}>
      <Handle 
        type="target" 
        position={Position.Top} 
        style={{ ...handleStyle, borderColor: '#10B981' }} 
        className="connection-handle !w-auto !h-auto !bg-transparent !border-0"
        isConnectableStart={false} 
      />
      <div className="px-3 py-1.5 border-b border-gray-100 dark:border-gray-700 flex items-center bg-green-50 dark:bg-green-900/10">
        <div className="p-1 rounded-md bg-green-100 dark:bg-green-900/20 mr-2">
          <HiOutlineDatabase className="text-green-600 dark:text-green-400 w-3.5 h-3.5" />
        </div>
        <div className="font-medium text-xs text-gray-800 dark:text-white truncate">{data.label}</div>
      </div>
      <div className="p-2 text-xs">
        <div className="flex items-center text-gray-500 dark:text-gray-400 mb-1">
          <div className="font-medium w-16 text-gray-600 dark:text-gray-300 text-xs">Environment:</div>
          <div className="flex-1 bg-gray-50 dark:bg-gray-700/30 px-1.5 py-0.5 rounded truncate text-xs">{data.environment || 'Not Set'}</div>
        </div>
        <div className="flex items-center text-gray-500 dark:text-gray-400">
          <div className="font-medium w-16 text-gray-600 dark:text-gray-300 text-xs">Operation:</div>
          <div className="flex-1 bg-gray-50 dark:bg-gray-700/30 px-1.5 py-0.5 rounded truncate text-xs">{data.action?.operation || 'Not Set'}</div>
        </div>
      </div>
      <Handle 
        type="source" 
        position={Position.Bottom} 
        style={{ ...handleStyle, borderColor: '#10B981' }} 
        className="connection-handle !w-auto !h-auto !bg-transparent !border-0"
      />
    </div>
  );
};

const AgentNode = ({ data, selected }: NodeProps) => {
  return (
    <div className={`rounded-md shadow-sm overflow-hidden ${selected ? 'ring-2 ring-blue-500' : 'border border-gray-200 dark:border-gray-700'} bg-white dark:bg-gray-800 min-w-[180px] transition-all`}>
      <Handle 
        type="target" 
        position={Position.Top} 
        style={{ ...handleStyle, borderColor: '#3B82F6' }} 
        className="connection-handle !w-auto !h-auto !bg-transparent !border-0"
        isConnectableStart={false}
      />
      <div className="px-3 py-1.5 border-b border-gray-100 dark:border-gray-700 flex items-center bg-blue-50 dark:bg-blue-900/10">
        <div className="p-1 rounded-md bg-blue-100 dark:bg-blue-900/20 mr-2">
          <HiOutlineLightningBolt className="text-blue-600 dark:text-blue-400 w-3.5 h-3.5" />
        </div>
        <div className="font-medium text-xs text-gray-800 dark:text-white truncate">{data.label}</div>
      </div>
      <div className="p-2 text-xs">
        <div className="flex items-center text-gray-500 dark:text-gray-400 mb-1">
          <div className="font-medium w-16 text-gray-600 dark:text-gray-300 text-xs">Agent:</div>
          <div className="flex-1 bg-gray-50 dark:bg-gray-700/30 px-1.5 py-0.5 rounded truncate text-xs">{data.agent || 'Not Set'}</div>
        </div>
        <div className="flex items-center text-gray-500 dark:text-gray-400">
          <div className="font-medium w-16 text-gray-600 dark:text-gray-300 text-xs">Task:</div>
          <div className="flex-1 bg-gray-50 dark:bg-gray-700/30 px-1.5 py-0.5 rounded truncate text-xs">{data.description || 'Not Set'}</div>
        </div>
      </div>
      <Handle 
        type="source" 
        position={Position.Bottom} 
        style={{ ...handleStyle, borderColor: '#3B82F6' }} 
        className="connection-handle !w-auto !h-auto !bg-transparent !border-0"
      />
    </div>
  );
};

const ConditionalNode = ({ data, selected }: NodeProps) => {
  return (
    <div className={`rounded-md shadow-sm ${selected ? 'ring-2 ring-blue-500' : 'border border-gray-200 dark:border-gray-700'} bg-white dark:bg-gray-800 min-w-[180px] transition-all overflow-hidden`}>
      <Handle 
        type="target" 
        position={Position.Top} 
        style={{ ...handleStyle, borderColor: '#F59E0B' }} 
        className="connection-handle !w-auto !h-auto !bg-transparent !border-0"
        isConnectableStart={false}
      />
      
      <div className="px-3 py-1.5 border-b border-gray-100 dark:border-gray-700 flex items-center bg-yellow-50 dark:bg-yellow-900/10">
        <div className="flex items-center">
          <div className="p-1 rounded-md bg-yellow-100 dark:bg-yellow-900/20 mr-2 rotate-45 w-5 h-5 flex items-center justify-center">
            <HiOutlineCode className="text-yellow-600 dark:text-yellow-400 w-3 h-3 -rotate-45" />
          </div>
          <div className="font-medium text-xs text-gray-800 dark:text-white truncate">{data.label}</div>
        </div>
      </div>
      
      <div className="p-2 text-xs">
        <div className="text-gray-500 dark:text-gray-400 mb-1.5 border border-dashed border-gray-200 dark:border-gray-700 p-1 rounded bg-gray-50 dark:bg-gray-900/30 text-center text-xs">
          {data.condition || 'Set condition expression...'}
        </div>
        
        <div className="grid grid-cols-2 gap-1">
          <div className="text-[10px] px-1.5 py-0.5 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded text-center">
            True
          </div>
          <div className="text-[10px] px-1.5 py-0.5 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded text-center">
            False
          </div>
        </div>
      </div>
      
      <Handle 
        type="source" 
        position={Position.Bottom} 
        id="true" 
        style={{ ...handleStyle, borderColor: '#22C55E', left: '30%' }} 
        className="connection-handle !w-auto !h-auto !bg-transparent !border-0"
      />
      <Handle 
        type="source" 
        position={Position.Bottom} 
        id="false" 
        style={{ ...handleStyle, borderColor: '#EF4444', left: '70%' }} 
        className="connection-handle !w-auto !h-auto !bg-transparent !border-0"
      />
    </div>
  );
};

const MCPAgentNode = ({ data, selected }: NodeProps) => {
  return (
    <div className={`rounded-md shadow-sm overflow-hidden ${selected ? 'ring-2 ring-blue-500' : 'border border-gray-200 dark:border-gray-700'} bg-white dark:bg-gray-800 min-w-[180px] transition-all`}>
      <Handle 
        type="target" 
        position={Position.Top} 
        style={{ ...handleStyle, borderColor: '#8B5CF6' }} 
        className="connection-handle !w-auto !h-auto !bg-transparent !border-0"
        isConnectableStart={false}
      />
      <div className="px-3 py-1.5 border-b border-gray-100 dark:border-gray-700 flex items-center bg-purple-50 dark:bg-purple-900/10">
        <div className="p-1 rounded-md bg-purple-100 dark:bg-purple-900/20 mr-2">
          <HiOutlineLightningBolt className="text-purple-600 dark:text-purple-400 w-3.5 h-3.5" />
        </div>
        <div className="font-medium text-xs text-gray-800 dark:text-white truncate">{data.label}</div>
      </div>
      <div className="p-2 text-xs">
        <div className="flex items-center text-gray-500 dark:text-gray-400 mb-1">
          <div className="font-medium w-16 text-gray-600 dark:text-gray-300 text-xs">MCP Server:</div>
          <div className="flex-1 bg-gray-50 dark:bg-gray-700/30 px-1.5 py-0.5 rounded truncate text-xs">{data.mcp_server || 'Not Set'}</div>
        </div>
        <div className="flex items-center text-gray-500 dark:text-gray-400">
          <div className="font-medium w-16 text-gray-600 dark:text-gray-300 text-xs">Tool:</div>
          <div className="flex-1 bg-gray-50 dark:bg-gray-700/30 px-1.5 py-0.5 rounded truncate text-xs">{data.tool || 'Not Set'}</div>
        </div>
      </div>
      <Handle 
        type="source" 
        position={Position.Bottom} 
        style={{ ...handleStyle, borderColor: '#8B5CF6' }} 
        className="connection-handle !w-auto !h-auto !bg-transparent !border-0"
      />
    </div>
  );
};

const BrowserActionNode = ({ data, selected }: NodeProps) => {
  return (
    <div className={`rounded-md shadow-sm overflow-hidden ${selected ? 'ring-2 ring-blue-500' : 'border border-gray-200 dark:border-gray-700'} bg-white dark:bg-gray-800 min-w-[180px] transition-all`}>
      <Handle 
        type="target" 
        position={Position.Top} 
        style={{ ...handleStyle, borderColor: '#6366F1' }} 
        className="connection-handle !w-auto !h-auto !bg-transparent !border-0"
        isConnectableStart={false}
      />
      <div className="px-3 py-1.5 border-b border-gray-100 dark:border-gray-700 flex items-center bg-indigo-50 dark:bg-indigo-900/10">
        <div className="p-1 rounded-md bg-indigo-100 dark:bg-indigo-900/20 mr-2">
          <HiOutlineDatabase className="text-indigo-600 dark:text-indigo-400 w-3.5 h-3.5" />
        </div>
        <div className="font-medium text-xs text-gray-800 dark:text-white truncate">{data.label}</div>
      </div>
      <div className="p-2 text-xs">
        <div className="flex items-center text-gray-500 dark:text-gray-400 mb-1">
          <div className="font-medium w-16 text-gray-600 dark:text-gray-300 text-xs">Action:</div>
          <div className="flex-1 bg-gray-50 dark:bg-gray-700/30 px-1.5 py-0.5 rounded truncate text-xs">{data.browser_action || 'Not Set'}</div>
        </div>
        <div className="flex items-center text-gray-500 dark:text-gray-400">
          <div className="font-medium w-16 text-gray-600 dark:text-gray-300 text-xs">URL:</div>
          <div className="flex-1 bg-gray-50 dark:bg-gray-700/30 px-1.5 py-0.5 rounded truncate text-xs">{data.url || 'Not Set'}</div>
        </div>
      </div>
      <Handle 
        type="source" 
        position={Position.Bottom} 
        style={{ ...handleStyle, borderColor: '#6366F1' }} 
        className="connection-handle !w-auto !h-auto !bg-transparent !border-0"
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

// Empty state component
const EmptyWorkflowState = ({ onAddNode }: { onAddNode: (type: string) => void }) => {
  return (
    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center justify-center bg-white dark:bg-gray-800 p-5 rounded-lg shadow-sm border border-blue-100 dark:border-blue-900/30 z-10 w-80">
      <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-full mb-3">
        <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 text-blue-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="22 12 16 12 14 15 10 15 8 12 2 12"></polyline>
          <path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"></path>
        </svg>
      </div>
      <h3 className="text-base font-medium mb-1.5 text-center">Start Building Your Workflow</h3>
      <p className="text-xs text-gray-500 dark:text-gray-400 text-center mb-4">
        Add nodes from the left panel and connect them to create a workflow.
      </p>
      <div className="flex space-x-2">
        <button
          className="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-md text-xs font-medium transition-colors"
          onClick={() => onAddNode('agent')}
        >
          Add Agent
        </button>
        <button
          className="px-3 py-1.5 bg-green-500 hover:bg-green-600 text-white rounded-md text-xs font-medium transition-colors"
          onClick={() => onAddNode('environment')}
        >
          Add Environment
        </button>
      </div>
    </div>
  );
};

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

  // Context menu state
  const [contextMenu, setContextMenu] = useState<{
    visible: boolean;
    x: number;
    y: number;
    nodeId?: string;
    edgeId?: string;
  }>({
    visible: false,
    x: 0,
    y: 0
  });

  // Reference to the ReactFlow container
  const reactFlowWrapper = useRef<HTMLDivElement>(null);

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

  // Delete a node
  const deleteNode = (nodeId: string) => {
    // Remove connected edges
    setEdges(edges => edges.filter(e => e.source !== nodeId && e.target !== nodeId));
    
    // Remove the node
    setNodes(nodes => nodes.filter(n => n.id !== nodeId));
    
    // Clear selection if the selected node is deleted
    if (selectedNode && selectedNode.id === nodeId) {
      setSelectedNode(null);
    }
    
    // Hide context menu
    setContextMenu({ visible: false, x: 0, y: 0 });
  };

  // Delete an edge
  const deleteEdge = (edgeId: string) => {
    setEdges(edges => edges.filter(e => e.id !== edgeId));
    
    // Hide context menu
    setContextMenu({ visible: false, x: 0, y: 0 });
  };

  // Handle right click on node
  const onNodeContextMenu = (event: React.MouseEvent, node: Node) => {
    // Prevent default context menu
    event.preventDefault();
    
    // Get viewport bounds
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    // Get ReactFlow container bounds
    const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect();
    
    // Calculate position, ensuring menu stays in viewport
    let x = event.clientX;
    let y = event.clientY;
    
    // Adjust position based on container position if available
    if (reactFlowBounds) {
      x = x - reactFlowBounds.left;
      y = y - reactFlowBounds.top;
    }
    
    // Estimate menu dimensions
    const menuWidth = 150;
    const menuHeight = 100;
    
    // Adjust if would render outside viewport
    if (reactFlowBounds && x + menuWidth > reactFlowBounds.width) {
      x = reactFlowBounds.width - menuWidth - 10;
    }
    
    if (reactFlowBounds && y + menuHeight > reactFlowBounds.height) {
      y = reactFlowBounds.height - menuHeight - 10;
    }
    
    // Show our custom context menu
    setContextMenu({
      visible: true,
      x,
      y,
      nodeId: node.id
    });
    
    // Select the node
    setSelectedNode(node);
    setNodeConfig(node.data);
  };

  // Handle right click on edge
  const onEdgeContextMenu = (event: React.MouseEvent, edge: Edge) => {
    // Prevent default context menu
    event.preventDefault();
    
    // Get ReactFlow container bounds
    const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect();
    
    // Calculate position, ensuring menu stays in viewport
    let x = event.clientX;
    let y = event.clientY;
    
    // Adjust position based on container position if available
    if (reactFlowBounds) {
      x = x - reactFlowBounds.left;
      y = y - reactFlowBounds.top;
    }
    
    // Estimate menu dimensions
    const menuWidth = 150;
    const menuHeight = 50;
    
    // Adjust if would render outside viewport
    if (reactFlowBounds && x + menuWidth > reactFlowBounds.width) {
      x = reactFlowBounds.width - menuWidth - 10;
    }
    
    if (reactFlowBounds && y + menuHeight > reactFlowBounds.height) {
      y = reactFlowBounds.height - menuHeight - 10;
    }
    
    // Show our custom context menu
    setContextMenu({
      visible: true,
      x,
      y,
      edgeId: edge.id
    });
  };

  // Handle click away to hide context menu
  const onPaneClick = () => {
    setContextMenu({ visible: false, x: 0, y: 0 });
  };

  // When connection changes
  const onConnect = useCallback((params: Connection) => {
    const newEdge = {
      ...params,
      type: 'custom', // Use our custom edge
      animated: false, // We handle animation ourselves
      style: { 
        stroke: '#3B82F6', 
        strokeWidth: 2,
        strokeOpacity: 0.85
      },
      markerEnd: { 
        type: MarkerType.ArrowClosed,
        width: 12,
        height: 12,
        color: '#3B82F6'
      }
    };
    setEdges(eds => addEdge(newEdge, eds));
  }, []);

  // Delete an edge via click (legacy method, kept for convenience)
  const onEdgeClick = useCallback((event: React.MouseEvent, edge: Edge) => {
    deleteEdge(edge.id);
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

  // Handle document clicks to close context menu
  useEffect(() => {
    const handleDocumentClick = (e: MouseEvent) => {
      // Close context menu when clicking outside
      if (contextMenu.visible) {
        // Check if click target is not part of the context menu
        const contextMenuElement = document.querySelector('.context-menu');
        if (contextMenuElement && !contextMenuElement.contains(e.target as Element)) {
          setContextMenu({ visible: false, x: 0, y: 0 });
        }
      }
    };

    document.addEventListener('click', handleDocumentClick);
    return () => {
      document.removeEventListener('click', handleDocumentClick);
    };
  }, [contextMenu.visible]);

  // Add flow animation style to head
  useEffect(() => {
    const styleEl = document.createElement('style');
    styleEl.innerHTML = `
      @keyframes flowAnimation {
        0% {
          stroke-dashoffset: 24;
        }
        100% {
          stroke-dashoffset: 0;
        }
      }
      
      /* Hover effect for connection handles */
      .react-flow__node:hover .connection-handle {
        opacity: 1;
        transform: scale(1.2);
      }
      
      /* Default state for connection handles */
      .connection-handle {
        opacity: 0.4;
      }
      
      /* Node selection style */
      .react-flow__node.selected {
        box-shadow: 0 0 0 2px #3B82F6;
      }

      /* Connection line animation */
      .react-flow__connection-path {
        stroke: #3B82F6;
        stroke-width: 2;
        stroke-dasharray: 5,5;
        animation: dashdraw 0.5s linear infinite;
      }
      
      @keyframes dashdraw {
        from {
          stroke-dashoffset: 10;
        }
      }
      
      /* Node style adjustments */
      .react-flow__node {
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
      }
      
      .react-flow__node:hover {
        transform: translateY(-1px);
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
      }
      
      /* Context menu styles */
      .context-menu {
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        background: white;
        z-index: 1000;
        min-width: 120px;
        font-size: 12px;
      }
      
      .context-menu-item {
        padding: 6px 12px;
        display: flex;
        align-items: center;
        cursor: pointer;
        transition: background 0.2s;
      }
      
      .context-menu-item:hover {
        background: #f5f5f5;
      }
      
      .context-menu-item svg {
        margin-right: 8px;
      }
      
      .context-menu-divider {
        height: 1px;
        background: #e5e7eb;
        margin: 4px 0;
      }
    `;
    document.head.appendChild(styleEl);
    return () => {
      document.head.removeChild(styleEl);
    };
  }, []);

  return (
    <div className="flex flex-col h-[calc(100vh-64px)] bg-gray-50 dark:bg-gray-900">
      {/* Header area */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-base font-semibold text-gray-900 dark:text-white">
              {workflowName || 'New Workflow'}
            </h1>
          </div>
          <div className="flex items-center space-x-3">
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
                      <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                        <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                      </svg>
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
                      <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                        <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                      </svg>
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
                      <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                        <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                      </svg>
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
                      <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                        <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                      </svg>
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
                      <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                        <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                      </svg>
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
        <div className="flex-1 relative bg-gray-100 dark:bg-gray-950" ref={reactFlowWrapper}>
          {nodes.length === 0 && (
            <EmptyWorkflowState onAddNode={addNode} />
          )}
          
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onNodeContextMenu={onNodeContextMenu}
            onEdgeContextMenu={onEdgeContextMenu}
            onEdgeClick={onEdgeClick}
            onPaneClick={onPaneClick}
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
            connectionMode={ConnectionMode.Loose}
            fitView
            fitViewOptions={{ padding: 0.2 }}
            defaultEdgeOptions={{
              type: 'custom',
              animated: false,
              style: { 
                stroke: '#3B82F6', 
                strokeWidth: 2,
                strokeOpacity: 0.85
              },
              markerEnd: { 
                type: MarkerType.ArrowClosed,
                width: 12,
                height: 12,
                color: '#3B82F6'
              }
            }}
            connectionLineStyle={{ 
              stroke: '#3B82F6', 
              strokeWidth: 2, 
              strokeDasharray: '5,5',
              strokeOpacity: 0.8
            }}
            connectionLineType={ConnectionLineType.SmoothStep}
            snapToGrid={true}
            snapGrid={[10, 10]}
            proOptions={{ hideAttribution: true }}
            defaultViewport={{ x: 0, y: 0, zoom: 1.2 }}
            minZoom={0.5}
            maxZoom={2}
            nodesDraggable={true}
            elementsSelectable={true}
            nodesConnectable={true}
            className="bg-[#fafafa] dark:bg-gray-900"
          >
            <Background 
              color="#e0e0e0" 
              gap={16} 
              size={1}
              variant={BackgroundVariant.Dots}
              className="bg-[#fafafa] dark:bg-gray-900"
            />
            
            <Controls 
              position="bottom-right" 
              showInteractive={false} 
              style={{ 
                background: 'white', 
                borderRadius: '8px', 
                border: '1px solid #e5e7eb',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)',
                bottom: '20px',
                right: '20px'
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
                bottom: '100px',
                right: '20px',
                width: '160px',
                height: '90px',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)'
              }}
              maskColor="rgba(0, 0, 0, 0.05)"
            />
          </ReactFlow>
          
          {/* Context Menu */}
          {contextMenu.visible && (
            <div 
              className="context-menu absolute dark:bg-gray-800 dark:border-gray-700 dark:text-white border border-gray-200 shadow-lg z-50"
              style={{ 
                left: `${contextMenu.x}px`, 
                top: `${contextMenu.y}px`,
                minWidth: '120px'
              }}
              onClick={(e) => e.stopPropagation()}
            >
              {contextMenu.nodeId && (
                <>
                  <div 
                    className="context-menu-item text-gray-800 dark:text-gray-200"
                    onClick={() => {
                      // Edit node - already in config panel when selected
                      setContextMenu({ visible: false, x: 0, y: 0 });
                    }}
                  >
                    <HiPencil className="w-3.5 h-3.5 text-gray-600 dark:text-gray-400" />
                    <span>Edit Node</span>
                  </div>
                  <div className="context-menu-divider"></div>
                  <div 
                    className="context-menu-item text-red-600 dark:text-red-400"
                    onClick={() => deleteNode(contextMenu.nodeId!)}
                  >
                    <HiTrash className="w-3.5 h-3.5" />
                    <span>Delete</span>
                  </div>
                </>
              )}
              
              {contextMenu.edgeId && (
                <div 
                  className="context-menu-item text-red-600 dark:text-red-400"
                  onClick={() => deleteEdge(contextMenu.edgeId!)}
                >
                  <HiTrash className="w-3.5 h-3.5" />
                  <span>Delete Connection</span>
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* Right configuration panel */}
        {selectedNode && (
          <div className="w-72 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 overflow-y-auto p-0">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 flex items-center justify-between">
              <h3 className="font-medium">Node Configuration</h3>
              <button 
                onClick={() => deleteNode(selectedNode.id)}
                className="p-1 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
                title="Delete node"
              >
                <HiTrash className="w-4 h-4" />
              </button>
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