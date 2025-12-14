"use client";

import { ReactFlow, Background, Controls } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const initialNodes = [
    { id: "agent", position: { x: 250, y: 0 }, data: { label: "Agent" } },
    { id: "reflect", position: { x: 250, y: 150 }, data: { label: "Reflect" } },
    { id: "tools", position: { x: 0, y: 75 }, data: { label: "Tools" } },
];

const initialEdges = [
    { id: "e1-2", source: "agent", target: "reflect", animated: true },
    { id: "e2-1", source: "reflect", target: "agent", animated: true },
    { id: "e3-1", source: "tools", target: "agent" },
];

export default function GraphVisualizer() {
    return (
        <div className="h-full w-full bg-gray-900 rounded-lg border border-gray-700">
            <ReactFlow nodes={initialNodes} edges={initialEdges} fitView>
                <Background />
                <Controls />
            </ReactFlow>
        </div>
    );
}
