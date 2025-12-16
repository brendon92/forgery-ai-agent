"use client";

import React, { useState } from 'react';
import { useWorkspace } from '../context/WorkspaceContext';
import FileExplorer from './FileExplorer';
import { Plus, Trash2, MessageSquare } from 'lucide-react';

export default function WorkspaceSidebar() {
    const {
        workspaces,
        currentWorkspace,
        setCurrentWorkspace,
        conversations,
        currentConversation,
        setCurrentConversation,
        createConversation,
        createWorkspace,
        deleteWorkspace
    } = useWorkspace();

    const [isCreatingWorkspace, setIsCreatingWorkspace] = useState(false);
    const [newWorkspaceTitle, setNewWorkspaceTitle] = useState("");

    const handleCreateWorkspace = async () => {
        if (!newWorkspaceTitle.trim()) return;
        await createWorkspace(newWorkspaceTitle);
        setNewWorkspaceTitle("");
        setIsCreatingWorkspace(false);
    };

    const handleDeleteWorkspace = async () => {
        if (currentWorkspace && confirm(`Delete workspace "${currentWorkspace.title}"?`)) {
            await deleteWorkspace(currentWorkspace.id);
        }
    };

    return (
        <div className="w-80 h-full bg-black/40 border-r border-gray-800 flex flex-col font-sans">
            {/* 1. Workspace Selector */}
            <div className="p-3 border-b border-gray-800 bg-gray-900/30">
                {isCreatingWorkspace ? (
                    <div className="flex flex-col gap-2 animate-in fade-in slide-in-from-top-1">
                        <input
                            type="text"
                            className="bg-gray-800 text-white px-2 py-1 rounded text-sm w-full outline-none focus:ring-1 focus:ring-blue-500 border border-gray-700"
                            placeholder="Workspace Name"
                            value={newWorkspaceTitle}
                            onChange={(e) => setNewWorkspaceTitle(e.target.value)}
                            autoFocus
                            onKeyDown={(e) => e.key === 'Enter' && handleCreateWorkspace()}
                        />
                        <div className="flex gap-2 text-xs justify-end">
                            <button onClick={handleCreateWorkspace} className="text-blue-400 hover:text-blue-300">Save</button>
                            <button onClick={() => setIsCreatingWorkspace(false)} className="text-gray-500 hover:text-gray-400">Cancel</button>
                        </div>
                    </div>
                ) : (
                    <div className="flex items-center gap-2">
                        <div className="flex-1 relative">
                            <select
                                className="w-full bg-gray-800/50 hover:bg-gray-800 text-white text-sm rounded-lg pl-3 pr-8 py-2 outline-none focus:ring-1 focus:ring-blue-500 appearance-none transition-colors cursor-pointer border border-gray-700"
                                value={currentWorkspace?.id || ""}
                                onChange={(e) => setCurrentWorkspace(workspaces.find(w => w.id === e.target.value) || null)}
                            >
                                {workspaces.map(ws => (
                                    <option key={ws.id} value={ws.id}>{ws.title}</option>
                                ))}
                                {workspaces.length === 0 && <option disabled>No Workspaces</option>}
                            </select>
                            <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none text-gray-400">
                                <ChevronDown size={14} />
                            </div>
                        </div>
                        <button
                            onClick={() => setIsCreatingWorkspace(true)}
                            className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-md transition-colors"
                            title="New Workspace"
                        >
                            <Plus size={18} />
                        </button>
                        {currentWorkspace && (
                            <button
                                onClick={handleDeleteWorkspace}
                                className="p-2 text-gray-500 hover:text-red-400 hover:bg-gray-800 rounded-md transition-colors"
                                title="Delete Workspace"
                            >
                                <Trash2 size={16} />
                            </button>
                        )}
                    </div>
                )}
            </div>

            {/* 2. File Explorer (Contextual for Workspace) */}
            <div className="flex-1 min-h-0 border-b border-gray-800">
                <FileExplorer />
            </div>

            {/* 3. Conversation List */}
            <div className="h-1/3 flex flex-col min-h-[200px] bg-gray-900/20">
                <div className="px-3 py-2 flex items-center justify-between border-b border-gray-800 bg-gray-900/50">
                    <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Chats</span>
                    <button
                        onClick={() => createConversation(`Chat ${conversations.length + 1}`)}
                        className="text-gray-400 hover:text-white"
                        title="New Chat"
                        disabled={!currentWorkspace}
                    >
                        <Plus size={14} />
                    </button>
                </div>
                <div className="flex-1 overflow-y-auto p-2 space-y-1">
                    {conversations.length === 0 && currentWorkspace && (
                        <p className="text-center text-xs text-gray-600 mt-4">No conversations</p>
                    )}
                    {conversations.map(conv => (
                        <button
                            key={conv.id}
                            onClick={() => setCurrentConversation(conv)}
                            className={`w-full text-left px-3 py-2 rounded-md text-sm truncate flex items-center gap-2 transition-all ${currentConversation?.id === conv.id
                                    ? "bg-blue-600/20 text-blue-200 border border-blue-500/30"
                                    : "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
                                }`}
                        >
                            <MessageSquare size={14} className={currentConversation?.id === conv.id ? "text-blue-400" : "text-gray-600"} />
                            <span className="truncate">{conv.title}</span>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}

// Helper for the custom select arrow
function ChevronDown({ size }: { size: number }) {
    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <polyline points="6 9 12 15 18 9" />
        </svg>
    );
}
