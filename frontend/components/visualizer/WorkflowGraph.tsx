"use client";

import React, { useEffect, useState, useCallback } from 'react';
import ReactFlow, {
    Node,
    Edge,
    Background,
    Controls,
    useNodesState,
    useEdgesState,
    Position
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useWebSocket } from '@/app/hooks/useWebSocket'; // We'll create this hook if needed, or assume it exists/we'll make it
import { motion, AnimatePresence } from 'framer-motion';

// --- Graph Definition ---
// This should match the LangGraph structure define in src/agent/graph.py
const initialNodes: Node[] = [
    { id: 'start', position: { x: 250, y: 0 }, data: { label: 'Start' }, type: 'input' },
    { id: 'agent', position: { x: 250, y: 100 }, data: { label: 'Agent (Generate)' }, style: { width: 180 } },
    { id: 'tools', position: { x: 50, y: 250 }, data: { label: 'Tool Execution' } },
    { id: 'reflect', position: { x: 450, y: 250 }, data: { label: 'Reflection (Critique)' } },
    { id: 'end', position: { x: 250, y: 400 }, data: { label: 'End' }, type: 'output' },
];

const initialEdges: Edge[] = [
    { id: 'e1', source: 'start', target: 'agent', animated: true },
    { id: 'e2', source: 'agent', target: 'tools', label: 'Use Tool' },
    { id: 'e3', source: 'tools', target: 'agent', animated: true },
    { id: 'e4', source: 'agent', target: 'reflect', label: 'Check Quality' },
    { id: 'e5', source: 'reflect', target: 'agent', label: 'Refine', animated: true, style: { stroke: '#ff00ff' } },
    { id: 'e6', source: 'reflect', target: 'end', label: 'Pass' },
    { id: 'e7', source: 'agent', target: 'end', label: 'Direct' },
];

export default function WorkflowGraph() {
    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
    const [activeNodeId, setActiveNodeId] = useState<string | null>(null);

    // Mock WebSocket connection logic - replace with actual context/hook
    useEffect(() => {
        // Ideally, we subscribe to the global EventSocket here.
        // For demo purposes, we'll setup a simple listener if the socket was globally available.

        // Simulating active node update
        const handleGraphUpdate = (event: CustomEvent) => {
            const { node, status } = event.detail;
            if (status === 'running' || status === 'completed') {
                setActiveNodeId(node);
            }
        };

        // window.addEventListener('graph-update', handleGraphUpdate as EventListener);
        // return () => window.removeEventListener('graph-update', handleGraphUpdate as EventListener);
    }, []);

    // Update node styles based on active state
    useEffect(() => {
        setNodes((nds) =>
            nds.map((node) => {
                if (node.id === activeNodeId) {
                    return {
                        ...node,
                        style: {
                            ...node.style,
                            background: '#0a0a0a',
                            color: '#00ffd5',
                            border: '2px solid #00ffd5',
                            boxShadow: '0 0 15px rgba(0, 255, 213, 0.5)',
                        },
                    };
                }
                return {
                    ...node,
                    style: {
                        ...node.style,
                        background: 'rgba(20,20,20,0.8)',
                        color: '#fff',
                        border: '1px solid rgba(255,255,255,0.2)'
                    },
                };
            })
        );
    }, [activeNodeId, setNodes]);

    return (
        <div className="w-full h-[500px] glass-panel rounded-xl overflow-hidden relative">
            <div className="absolute top-4 left-4 z-10">
                <h3 className="neon-text text-lg font-bold">Live Agent Workflow</h3>
                <p className="text-xs text-gray-400">Real-time execution trace</p>
            </div>

            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                fitView
            >
                <Background gap={16} color="#333" />
                <Controls className="bg-gray-800 border-gray-700 fill-white" />
            </ReactFlow>
        </div>
    );
}
