"use client";

import React from 'react';
import { Database, Server } from 'lucide-react';

export default function ToolsManager() {
    return (
        <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <div className="bg-gray-800 p-6 rounded-full mb-4">
                <Database size={64} className="text-blue-500" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">MCP & Tools Registry</h2>
            <p className="max-w-md text-center">
                Manage your Model Context Protocol servers and available tools here.
                Connect to external APIs, local databases, and more.
            </p>
            <button className="mt-8 bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-lg transition-colors flex items-center gap-2">
                <Server size={18} />
                Connect New MCP Server
            </button>
        </div>
    );
}
