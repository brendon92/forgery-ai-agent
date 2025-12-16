"use client";

import React from 'react';
import { ReactFlow, Background, Controls } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

// Reuse the initial mock data or fetch from API in real implementation
const initialNodes = [
    { id: "start", position: { x: 50, y: 50 }, data: { label: "Start" }, type: 'input' },
    { id: "agent1", position: { x: 250, y: 50 }, data: { label: "Researcher" } },
    { id: "agent2", position: { x: 250, y: 150 }, data: { label: "Writer" } },
    { id: "end", position: { x: 450, y: 100 }, data: { label: "End" }, type: 'output' },
];

const initialEdges = [
    { id: "e1", source: "start", target: "agent1", animated: true },
    { id: "e2", source: "start", target: "agent2", animated: true },
    { id: "e3", source: "agent1", target: "end" },
    { id: "e4", source: "agent2", target: "end" },
];

export default function WorkflowBuilder() {
    return (
        <div className="flex flex-col h-full bg-gray-900/50">
            <div className="p-4 border-b border-gray-800 flex justify-between items-center bg-gray-900/80">
                <div>
                    <h2 className="text-xl font-bold text-white">Workflow Editor</h2>
                    <p className="text-sm text-gray-400">Design complex reasoning paths for your agents.</p>
                </div>
                <div className="flex gap-2">
                    <button className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm transition-colors">Save Workflow</button>
                </div>
            </div>
            <div className="flex-1 w-full bg-gray-900 relative">
                <ReactFlow nodes={initialNodes} edges={initialEdges} fitView className="bg-gray-900">
                    <Background color="#333" gap={16} />
                    <Controls className="bg-gray-800 border-gray-700 fill-white" />
                </ReactFlow>
            </div>
        </div>
    );
}
