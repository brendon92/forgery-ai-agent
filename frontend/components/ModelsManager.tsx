"use client";

import React, { useState, useEffect } from 'react';
import { Cpu, Plus, Edit2, Trash2 } from 'lucide-react';
import { config } from '../lib/config';

type Model = {
    id: string;
    name: string;
    provider: 'openai' | 'anthropic' | 'grok' | 'ollama';
    baseUrl?: string;
    apiKey?: string; // In real app, never display this fully
    contextWindow: number;
};

export default function ModelsManager() {
    const [models, setModels] = useState<Model[]>([]);
    const [isEditing, setIsEditing] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [currentModel, setCurrentModel] = useState<Partial<Model>>({
        provider: 'ollama',
        contextWindow: 128000
    });

    const API_BASE = config.apiBaseUrl;

    const fetchModels = async () => {
        setIsLoading(true);
        try {
            const res = await fetch(`${API_BASE}/models`);
            if (res.ok) {
                setModels(await res.json());
            }
        } catch (e) {
            console.error("Fetch models failed", e);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchModels();
    }, []);

    const handleSave = async () => {
        setIsLoading(true);
        try {
            const method = currentModel.id ? 'PUT' : 'POST';
            const url = currentModel.id ? `${API_BASE}/models/${currentModel.id}` : `${API_BASE}/models`;

            const res = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(currentModel)
            });

            if (res.ok) {
                setIsEditing(false);
                setCurrentModel({ provider: 'ollama', contextWindow: 8192 });
                await fetchModels();
            }
        } catch (e) {
            console.error("Save failed", e);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm("Are you sure?")) return;
        try {
            await fetch(`${API_BASE}/models/${id}`, { method: 'DELETE' });
            await fetchModels();
        } catch (e) {
            console.error("Delete failed", e);
        }
    };

    const startEdit = (model: Model) => {
        setCurrentModel(model);
        setIsEditing(true);
    };

    const startNew = () => {
        setCurrentModel({ provider: 'ollama', contextWindow: 8192 });
        setIsEditing(true);
    };

    return (
        <div className="flex flex-col h-full bg-gray-900/50 p-6">
            <div className="flex justify-between items-center mb-8 border-b border-gray-800 pb-4">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                        <Cpu className="text-purple-500" />
                        Model Registry
                    </h2>
                    <p className="text-gray-400 text-sm mt-1">Configure AI models from various providers for your agents.</p>
                </div>
                <button
                    onClick={startNew}
                    className="bg-purple-600 hover:bg-purple-500 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
                >
                    <Plus size={18} />
                    Add Model
                </button>
            </div>

            {isLoading && models.length === 0 ? (
                <div className="text-white">Loading...</div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {models.map(model => (
                        <div key={model.id} className="bg-gray-800 border border-gray-700 rounded-xl p-4 hover:border-purple-500/50 transition-colors group">
                            <div className="flex justify-between items-start mb-2">
                                <span className={`text-xs font-bold px-2 py-0.5 rounded uppercase tracking-wide
                                ${model.provider === 'openai' ? 'bg-green-900/50 text-green-400' : ''}
                                ${model.provider === 'anthropic' ? 'bg-orange-900/50 text-orange-400' : ''}
                                ${model.provider === 'ollama' ? 'bg-blue-900/50 text-blue-400' : ''}
                                ${model.provider === 'grok' ? 'bg-gray-700 text-gray-300' : ''}
                             `}>
                                    {model.provider}
                                </span>
                                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button onClick={() => startEdit(model)} className="text-gray-400 hover:text-white"><Edit2 size={14} /></button>
                                    <button onClick={() => handleDelete(model.id)} className="text-gray-400 hover:text-red-400"><Trash2 size={14} /></button>
                                </div>
                            </div>
                            <h3 className="text-lg font-semibold text-white mb-1">{model.name}</h3>
                            <div className="text-xs text-gray-500 space-y-1">
                                <p>Context: {model.contextWindow.toLocaleString()} tokens</p>
                                {model.baseUrl && <p className="truncate">Url: {model.baseUrl}</p>}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {isEditing && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
                    <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 w-full max-w-md">
                        <h3 className="text-xl font-bold text-white mb-4">{currentModel.id ? 'Edit Model' : 'Add New Model'}</h3>

                        <div className="space-y-4 mb-6">
                            <div>
                                <label className="text-xs text-gray-400">Name</label>
                                <input
                                    className="w-full bg-black/50 border border-gray-700 rounded p-2 text-white"
                                    value={currentModel.name || ''}
                                    onChange={e => setCurrentModel({ ...currentModel, name: e.target.value })}
                                    placeholder="e.g. gpt-4o or llama3.2"
                                />
                            </div>
                            <div>
                                <label className="text-xs text-gray-400">Provider</label>
                                <select
                                    className="w-full bg-black/50 border border-gray-700 rounded p-2 text-white"
                                    value={currentModel.provider || 'ollama'}
                                    onChange={e => setCurrentModel({ ...currentModel, provider: e.target.value as any })}
                                >
                                    <option value="ollama">Ollama</option>
                                    <option value="openai">OpenAI</option>
                                    <option value="anthropic">Anthropic</option>
                                </select>
                            </div>
                            <div>
                                <label className="text-xs text-gray-400">Base URL (Optional)</label>
                                <input
                                    className="w-full bg-black/50 border border-gray-700 rounded p-2 text-white"
                                    value={currentModel.baseUrl || ''}
                                    onChange={e => setCurrentModel({ ...currentModel, baseUrl: e.target.value })}
                                    placeholder="http://localhost:11434"
                                />
                            </div>
                            <div>
                                <label className="text-xs text-gray-400">Context Window</label>
                                <input
                                    type="number"
                                    className="w-full bg-black/50 border border-gray-700 rounded p-2 text-white"
                                    value={currentModel.contextWindow || 8192}
                                    onChange={e => setCurrentModel({ ...currentModel, contextWindow: parseInt(e.target.value) })}
                                />
                            </div>
                        </div>

                        <div className="flex justify-end gap-2">
                            <button onClick={() => setIsEditing(false)} className="text-gray-400 hover:text-white px-4 py-2">Cancel</button>
                            <button onClick={handleSave} className="bg-purple-600 text-white px-4 py-2 rounded-lg">Save</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
