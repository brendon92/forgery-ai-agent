"use client";

import React, { useState, useEffect } from 'react';
import { useSettings } from '../context/SettingsContext';
import { config } from '../lib/config';

export default function SettingsView() {
    const { settings, updateSettings, isLoading } = useSettings();
    const [availableModels, setAvailableModels] = useState<any[]>([]);

    // Local state for forms
    const [apiKey, setApiKey] = useState("");
    const [defaultModel, setDefaultModel] = useState("");
    const [theme, setTheme] = useState("dark");

    useEffect(() => {
        if (settings) {
            setApiKey(settings.api_keys.openai_api_key || "");
            setDefaultModel(settings.model_selection.llm_model || "gpt-4o");
        }
    }, [settings]);

    useEffect(() => {
        // Fetch available models for dropdown
        fetch(`${config.apiBaseUrl}/models`)
            .then(res => res.json())
            .then(data => setAvailableModels(data))
            .catch(err => console.error("Failed to load models", err));
    }, []);

    const handleSave = async () => {
        if (!settings) return;
        await updateSettings({
            ...settings,
            api_keys: { ...settings.api_keys, openai_api_key: apiKey },
            model_selection: { ...settings.model_selection, llm_model: defaultModel }
        });
        alert("Settings Saved!");
    };

    if (isLoading || !settings) return <div className="p-10 text-white">Loading Settings...</div>;

    return (
        <div className="flex flex-col h-full items-center justify-start pt-10 bg-gray-900/50 overflow-y-auto">
            <div className="w-full max-w-3xl bg-gray-900 border border-gray-800 rounded-xl p-8 shadow-2xl mb-10">
                <h2 className="text-3xl font-bold text-white mb-8 border-b border-gray-800 pb-4">Global Settings</h2>

                <div className="space-y-8">
                    {/* API Keys Section */}
                    <div className="space-y-4">
                        <h3 className="text-xl font-semibold text-gray-200">API Configuration</h3>
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">OpenAI API Key</label>
                            <input
                                type="password"
                                className="w-full bg-black/40 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all"
                                value={apiKey}
                                onChange={(e) => setApiKey(e.target.value)}
                                placeholder="sk-..."
                            />
                            <p className="text-xs text-gray-500 mt-2">Required for default agents.</p>
                        </div>
                    </div>

                    {/* Model Selection */}
                    <div className="space-y-4">
                        <h3 className="text-xl font-semibold text-gray-200">Default Intelligence</h3>
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">Global Default Model</label>
                            <select
                                value={defaultModel}
                                onChange={(e) => setDefaultModel(e.target.value)}
                                className="w-full bg-black/40 border border-gray-700 rounded-lg px-4 py-3 text-white outline-none"
                            >
                                {availableModels.map(m => (
                                    <option key={m.id} value={m.name}>{m.name} ({m.provider})</option>
                                ))}
                                {/* Fallback options if API fails */}
                                {!availableModels.length && (
                                    <>
                                        <option value="gpt-4o">gpt-4o</option>
                                        <option value="qwen2.5:1.5b">qwen2.5:1.5b</option>
                                    </>
                                )}
                            </select>
                            <p className="text-xs text-gray-500 mt-2">This model is used when 'smart' reasoning is required, unless overridden by an agent.</p>
                        </div>
                    </div>

                    {/* Appearance Section */}
                    <div className="space-y-4">
                        <h3 className="text-xl font-semibold text-gray-200">Appearance</h3>
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">Theme</label>
                            <select
                                value={theme}
                                onChange={(e) => setTheme(e.target.value)}
                                className="w-full bg-black/40 border border-gray-700 rounded-lg px-4 py-3 text-white outline-none"
                            >
                                <option value="dark">Dark Mode</option>
                                <option value="light" disabled>Light Mode (Coming Soon)</option>
                            </select>
                        </div>
                    </div>

                    {/* System Actions */}
                    <div className="space-y-4 pt-4 border-t border-gray-800">
                        <h3 className="text-xl font-semibold text-gray-200">System Actions</h3>
                        <div>
                            <div className="bg-red-900/10 border border-red-900/30 rounded-lg p-4 flex items-center justify-between">
                                <p className="text-sm text-gray-400">
                                    Restore default agent personas (Financial Analyst, etc). This will create them if they are missing.
                                </p>
                                <button
                                    onClick={async () => {
                                        if (!confirm("Restore default agents? This will not delete your custom agents.")) return;
                                        try {
                                            const res = await fetch(`${config.apiBaseUrl}/agents/seed`, { method: "POST" });
                                            if (res.ok) alert("Agents restored!");
                                            else alert("Failed to restore.");
                                        } catch (e) { console.error(e); alert("Error restoring agents."); }
                                    }}
                                    className="bg-red-900/50 hover:bg-red-900/80 border border-red-700 text-red-100 px-4 py-2 rounded-lg font-medium transition text-sm whitespace-nowrap"
                                >
                                    Restore Defaults
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="pt-6 border-t border-gray-800 flex justify-end">
                        <button
                            onClick={handleSave}
                            className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-lg font-medium transition shadow-lg hover:shadow-blue-500/20"
                        >
                            Save Changes
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
