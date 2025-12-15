"use client";

import React, { useState } from 'react';
import { useWorkspace } from '../context/WorkspaceContext';
import { useSettings } from '../context/SettingsContext';

interface SidebarProps {
    onOpenSettings: () => void;
}

export default function Sidebar({ onOpenSettings }: SidebarProps) {
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

    const handleWorkspaceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const ws = workspaces.find(w => w.id === e.target.value);
        setCurrentWorkspace(ws || null);
    };

    const handleCreateConversation = async () => {
        const title = `New Chat ${conversations.length + 1}`;
        await createConversation(title);
    };

    const handleCreateWorkspace = async () => {
        if (!newWorkspaceTitle.trim()) return;
        await createWorkspace(newWorkspaceTitle);
        setNewWorkspaceTitle("");
        setIsCreatingWorkspace(false);
    }

    const handleDeleteWorkspace = async () => {
        if (currentWorkspace && confirm(`Delete workspace "${currentWorkspace.title}"?`)) {
            await deleteWorkspace(currentWorkspace.id);
        }
    }

    return (
        <div className="w-64 h-full bg-gray-900 border-r border-gray-800 flex flex-col">
            {/* Header / Workspace Selector */}
            <div className="p-4 border-b border-gray-800">
                <div className="flex items-center justify-between mb-2">
                    <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Workspace</h2>
                </div>

                {isCreatingWorkspace ? (
                    <div className="flex flex-col gap-2">
                        <input
                            type="text"
                            className="bg-gray-800 text-white px-2 py-1 rounded text-sm w-full outline-none focus:ring-1 focus:ring-blue-500"
                            placeholder="Workspace Name"
                            value={newWorkspaceTitle}
                            onChange={(e) => setNewWorkspaceTitle(e.target.value)}
                            autoFocus
                            onKeyDown={(e) => e.key === 'Enter' && handleCreateWorkspace()}
                        />
                        <div className="flex gap-2 text-xs">
                            <button onClick={handleCreateWorkspace} className="text-blue-400 hover:text-blue-300">Save</button>
                            <button onClick={() => setIsCreatingWorkspace(false)} className="text-gray-500 hover:text-gray-400">Cancel</button>
                        </div>
                    </div>
                ) : (
                    <div className="flex gap-2">
                        <select
                            className="bg-gray-800 text-white text-sm rounded px-2 py-1 flex-1 outline-none focus:ring-1 focus:ring-blue-500 truncate appearance-none cursor-pointer hover:bg-gray-700 transition"
                            value={currentWorkspace?.id || ""}
                            onChange={handleWorkspaceChange}
                        >
                            {workspaces.map(ws => (
                                <option key={ws.id} value={ws.id}>{ws.title}</option>
                            ))}
                            {workspaces.length === 0 && <option disabled>No Workspaces</option>}
                        </select>
                        <button
                            onClick={() => setIsCreatingWorkspace(true)}
                            className="text-gray-400 hover:text-white px-1"
                            title="New Workspace"
                        >
                            +
                        </button>
                        {currentWorkspace && (
                            <button
                                onClick={handleDeleteWorkspace}
                                className="text-red-900 hover:text-red-500 px-1"
                                title="Delete Workspace"
                            >
                                ×
                            </button>
                        )}
                    </div>
                )}
            </div>

            {/* Conversation List */}
            <div className="flex-1 overflow-y-auto p-2">
                <div className="mb-2 px-2">
                    <button
                        onClick={handleCreateConversation}
                        className="w-full bg-blue-600 hover:bg-blue-500 text-white text-sm py-2 px-4 rounded transition flex items-center justify-center gap-2"
                        disabled={!currentWorkspace}
                    >
                        <span>+</span> New Chat
                    </button>
                </div>

                <div className="flex flex-col gap-1 mt-4">
                    {conversations.length === 0 && currentWorkspace && (
                        <p className="text-xs text-gray-600 text-center mt-4">No conversations yet.</p>
                    )}

                    {conversations.map(conv => (
                        <button
                            key={conv.id}
                            onClick={() => setCurrentConversation(conv)}
                            className={`text-left px-3 py-2 rounded text-sm truncate transition ${currentConversation?.id === conv.id
                                    ? "bg-gray-800 text-white"
                                    : "text-gray-400 hover:bg-gray-800/50 hover:text-gray-200"
                                }`}
                        >
                            {conv.title}
                        </button>
                    ))}
                </div>
            </div>

            {/* Footer / Settings */}
            <div className="p-4 border-t border-gray-800">
                <button
                    onClick={onOpenSettings}
                    className="flex items-center gap-2 text-gray-400 hover:text-white transition w-full px-2 py-1 rounded hover:bg-gray-800"
                >
                    <span className="text-xl">⚙️</span>
                    <span className="text-sm">Settings</span>
                </button>
            </div>
        </div>
    );
}
