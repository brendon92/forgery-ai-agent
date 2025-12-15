"use client";

import React, { useState } from 'react';
import { useSettings, Crew } from '../context/SettingsContext';

export default function CrewBuilder() {
    const { crews, saveCrew, agents } = useSettings();
    const [editingCrew, setEditingCrew] = useState<Partial<Crew> | null>(null);

    const handleSave = async () => {
        if (!editingCrew || !editingCrew.name) return;

        await saveCrew({
            name: editingCrew.name,
            description: editingCrew.description || "",
            agent_ids: editingCrew.agent_ids || [],
            process: editingCrew.process || "sequential"
        });
        setEditingCrew(null);
    };

    const toggleAgent = (agentId: string) => {
        if (!editingCrew) return;
        const currentIds = editingCrew.agent_ids || [];
        const newIds = currentIds.includes(agentId)
            ? currentIds.filter(id => id !== agentId)
            : [...currentIds, agentId];
        setEditingCrew({ ...editingCrew, agent_ids: newIds });
    };

    return (
        <div className="flex flex-col h-full">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-white">Crew Builder</h3>
                {!editingCrew && (
                    <button
                        onClick={() => setEditingCrew({ name: "", description: "", agent_ids: [], process: "sequential" })}
                        className="bg-purple-600 hover:bg-purple-500 text-white px-3 py-1 rounded text-sm"
                    >
                        + New Crew
                    </button>
                )}
            </div>

            {editingCrew ? (
                <div className="flex flex-col gap-3 bg-gray-800 p-4 rounded animate-in fade-in h-full overflow-hidden">
                    <input
                        placeholder="Crew Name"
                        className="bg-gray-700 p-2 rounded text-white text-sm"
                        value={editingCrew.name}
                        onChange={e => setEditingCrew({ ...editingCrew, name: e.target.value })}
                    />
                    <textarea
                        placeholder="Description"
                        className="bg-gray-700 p-2 rounded text-white text-sm h-16"
                        value={editingCrew.description}
                        onChange={e => setEditingCrew({ ...editingCrew, description: e.target.value })}
                    />

                    <div className="flex-1 overflow-hidden flex flex-col">
                        <label className="text-xs text-gray-400 mb-1">Select Agents:</label>
                        <div className="flex-1 overflow-y-auto bg-gray-700/50 rounded p-2 space-y-1">
                            {agents.map(agent => (
                                <div
                                    key={agent.id}
                                    onClick={() => agent.id && toggleAgent(agent.id)}
                                    className={`p-2 rounded cursor-pointer text-sm flex justify-between items-center ${editingCrew.agent_ids?.includes(agent.id!) ? "bg-purple-900/50 border border-purple-500" : "bg-gray-700 hover:bg-gray-600"}`}
                                >
                                    <span>{agent.name}</span>
                                    <span className="text-xs text-gray-400">{agent.role}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="flex gap-2 justify-end mt-2">
                        <button onClick={() => setEditingCrew(null)} className="text-gray-400 hover:text-white px-3 py-1 text-sm">Cancel</button>
                        <button onClick={handleSave} className="bg-green-600 hover:bg-green-500 text-white px-3 py-1 rounded text-sm">Save Crew</button>
                    </div>
                </div>
            ) : (
                <div className="flex-1 overflow-y-auto space-y-2">
                    {crews.map(crew => (
                        <div key={crew.id} className="bg-gray-800/50 p-3 rounded hover:bg-gray-800 transition">
                            <div className="font-medium text-white">{crew.name}</div>
                            <div className="text-xs text-gray-400">{crew.description}</div>
                            <div className="flex gap-2 mt-2">
                                <span className="text-xs bg-gray-700 px-2 py-0.5 rounded text-gray-300">{crew.agent_ids.length} Agents</span>
                                <span className="text-xs bg-gray-700 px-2 py-0.5 rounded text-gray-300 capitalize">{crew.process} Process</span>
                            </div>
                        </div>
                    ))}
                    {crews.length === 0 && <p className="text-gray-500 text-sm text-center py-4">No crews configured.</p>}
                </div>
            )}
        </div>
    );
}
