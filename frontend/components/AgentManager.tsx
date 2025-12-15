"use client";

import React, { useState } from 'react';
import { useSettings, Agent } from '../context/SettingsContext';

export default function AgentManager() {
    const { agents, saveAgent, deleteAgent, isLoading } = useSettings();
    const [editingAgent, setEditingAgent] = useState<Partial<Agent> | null>(null);

    const handleSave = async () => {
        if (!editingAgent || !editingAgent.name || !editingAgent.role) return;

        await saveAgent({
            id: editingAgent.id,
            name: editingAgent.name,
            role: editingAgent.role,
            goal: editingAgent.goal || "",
            backstory: editingAgent.backstory || "",
            tools: editingAgent.tools || [],
            enabled: editingAgent.enabled ?? true
        });
        setEditingAgent(null);
    };

    const startEdit = (agent?: Agent) => {
        setEditingAgent(agent || {
            name: "", role: "", goal: "", backstory: "", tools: [], enabled: true
        });
    };

    return (
        <div className="flex flex-col h-full">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-white">Agent Personas</h3>
                {!editingAgent && (
                    <button
                        onClick={() => startEdit()}
                        className="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1 rounded text-sm"
                    >
                        + New Agent
                    </button>
                )}
            </div>

            {editingAgent ? (
                <div className="flex flex-col gap-3 bg-gray-800 p-4 rounded animate-in fade-in">
                    <div className="grid grid-cols-2 gap-2">
                        <input
                            placeholder="Name"
                            className="bg-gray-700 p-2 rounded text-white text-sm"
                            value={editingAgent.name}
                            onChange={e => setEditingAgent({ ...editingAgent, name: e.target.value })}
                        />
                        <input
                            placeholder="Role"
                            className="bg-gray-700 p-2 rounded text-white text-sm"
                            value={editingAgent.role}
                            onChange={e => setEditingAgent({ ...editingAgent, role: e.target.value })}
                        />
                    </div>
                    <textarea
                        placeholder="Goal"
                        className="bg-gray-700 p-2 rounded text-white text-sm h-20"
                        value={editingAgent.goal}
                        onChange={e => setEditingAgent({ ...editingAgent, goal: e.target.value })}
                    />
                    <textarea
                        placeholder="Backstory"
                        className="bg-gray-700 p-2 rounded text-white text-sm h-24"
                        value={editingAgent.backstory}
                        onChange={e => setEditingAgent({ ...editingAgent, backstory: e.target.value })}
                    />
                    {/* Tool selection could be more advanced */}
                    <div className="flex gap-2 justify-end mt-2">
                        <button onClick={() => setEditingAgent(null)} className="text-gray-400 hover:text-white px-3 py-1 text-sm">Cancel</button>
                        <button onClick={handleSave} className="bg-green-600 hover:bg-green-500 text-white px-3 py-1 rounded text-sm">Save</button>
                    </div>
                </div>
            ) : (
                <div className="flex-1 overflow-y-auto space-y-2">
                    {agents.map(agent => (
                        <div key={agent.id} className="bg-gray-800/50 p-3 rounded hover:bg-gray-800 transition flex justify-between items-start group">
                            <div>
                                <div className="font-medium text-white">{agent.name}</div>
                                <div className="text-xs text-blue-400">{agent.role}</div>
                                <div className="text-xs text-gray-400 mt-1 line-clamp-2">{agent.goal}</div>
                            </div>
                            <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition">
                                <button onClick={() => startEdit(agent)} className="text-gray-400 hover:text-blue-400 text-xs">Edit</button>
                                <button onClick={() => agent.id && deleteAgent(agent.id)} className="text-gray-400 hover:text-red-400 text-xs">Delete</button>
                            </div>
                        </div>
                    ))}
                    {agents.length === 0 && <p className="text-gray-500 text-sm text-center py-4">No agents configured.</p>}
                </div>
            )}
        </div>
    );
}
