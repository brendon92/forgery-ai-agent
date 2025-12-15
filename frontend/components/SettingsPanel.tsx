"use client";

import React, { useState } from 'react';
import { useSettings } from '../context/SettingsContext';
import AgentManager from './AgentManager';
import CrewBuilder from './CrewBuilder';

interface SettingsPanelProps {
    onClose: () => void;
}

export default function SettingsPanel({ onClose }: SettingsPanelProps) {
    const { settings, updateSettings } = useSettings();
    const [activeTab, setActiveTab] = useState<'general' | 'agents' | 'crews'>('general');

    // Local state for General settings form
    const [apiKey, setApiKey] = useState(settings?.api_keys.openai_api_key || "");

    // Simple save handler for general
    const handleGeneralSave = async () => {
        if (!settings) return;
        await updateSettings({
            ...settings,
            api_keys: { ...settings.api_keys, openai_api_key: apiKey }
        });
        // Feedback?
    };

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center">
            <div className="bg-gray-900 border border-gray-700 w-[800px] h-[600px] rounded-xl shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
                {/* Header */}
                <div className="flex justify-between items-center p-4 border-b border-gray-800 bg-gray-900/50">
                    <h2 className="text-xl font-bold text-white">Settings</h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-white text-2xl leading-none">&times;</button>
                </div>

                {/* Tabs */}
                <div className="flex border-b border-gray-800">
                    <button
                        onClick={() => setActiveTab('general')}
                        className={`px-6 py-3 text-sm font-medium transition ${activeTab === 'general' ? "text-blue-400 border-b-2 border-blue-400 bg-gray-800/50" : "text-gray-400 hover:text-white hover:bg-gray-800"}`}
                    >
                        General
                    </button>
                    <button
                        onClick={() => setActiveTab('agents')}
                        className={`px-6 py-3 text-sm font-medium transition ${activeTab === 'agents' ? "text-blue-400 border-b-2 border-blue-400 bg-gray-800/50" : "text-gray-400 hover:text-white hover:bg-gray-800"}`}
                    >
                        Agents
                    </button>
                    <button
                        onClick={() => setActiveTab('crews')}
                        className={`px-6 py-3 text-sm font-medium transition ${activeTab === 'crews' ? "text-blue-400 border-b-2 border-blue-400 bg-gray-800/50" : "text-gray-400 hover:text-white hover:bg-gray-800"}`}
                    >
                        Crews
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 p-6 overflow-hidden">
                    {activeTab === 'general' && (
                        <div className="space-y-6 max-w-lg">
                            <div>
                                <label className="block text-sm text-gray-400 mb-2">OpenAI API Key</label>
                                <input
                                    type="password"
                                    className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-white focus:border-blue-500 outline-none"
                                    value={apiKey}
                                    onChange={(e) => setApiKey(e.target.value)}
                                    placeholder="sk-..."
                                />
                            </div>

                            {/* Other General Settings can go here */}

                            <div className="pt-4">
                                <button
                                    onClick={handleGeneralSave}
                                    className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded text-sm transition"
                                >
                                    Save Changes
                                </button>
                            </div>
                        </div>
                    )}

                    {activeTab === 'agents' && (
                        <div className="h-full">
                            <AgentManager />
                        </div>
                    )}

                    {activeTab === 'crews' && (
                        <div className="h-full">
                            <CrewBuilder />
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
