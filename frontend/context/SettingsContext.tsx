"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

import { config } from '../lib/config';

// Types (Mirroring Backend models)
type AgentConfig = {
    reflection_threshold: number;
    max_retries: number;
    system_prompt: string;
};

type ApiKeys = {
    openai_api_key?: string;
    langfuse_public_key?: string;
    langfuse_secret_key?: string;
    qdrant_api_key?: string;
};

type ModelSelection = {
    llm_model: string;
    embedding_model: string;
    temperature: number;
};

type ServiceEndpoints = {
    neo4j_uri: string;
    qdrant_url: string;
    langfuse_host: string;
};

type Settings = {
    agent_config: AgentConfig;
    api_keys: ApiKeys;
    model_selection: ModelSelection;
    service_endpoints: ServiceEndpoints;
};

// Agent Types
export type Agent = {
    id?: string;
    name: string;
    role: string;
    goal: string;
    backstory: string;
    tools: string[];
    enabled: boolean;
};

export type Crew = {
    id?: string;
    name: string;
    description: string;
    agent_ids: string[];
    process: string;
};


interface SettingsContextType {
    settings: Settings | null;
    isLoading: boolean;
    updateSettings: (newSettings: Settings) => Promise<void>;

    // Agent Management
    agents: Agent[];
    refreshAgents: () => Promise<void>;
    saveAgent: (agent: Agent) => Promise<void>;
    deleteAgent: (id: string) => Promise<void>;

    // Crew Management
    crews: Crew[];
    refreshCrews: () => Promise<void>;
    saveCrew: (crew: Crew) => Promise<void>;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export function SettingsProvider({ children }: { children: ReactNode }) {
    const [settings, setSettings] = useState<Settings | null>(null);
    const [agents, setAgents] = useState<Agent[]>([]);
    const [crews, setCrews] = useState<Crew[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const API_BASE = config.apiBaseUrl;

    // --- Settings Operations ---
    const fetchSettings = async () => {
        try {
            const res = await fetch(`${API_BASE}/settings`);
            if (res.ok) {
                setSettings(await res.json());
            }
        } catch (e) {
            console.error("Fetch settings failed", e);
        }
    };

    const updateSettings = async (newSettings: Settings) => {
        try {
            const res = await fetch(`${API_BASE}/settings`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(newSettings)
            });
            if (res.ok) {
                setSettings(await res.json());
            }
        } catch (e) {
            console.error("Update settings failed", e);
        }
    };

    // --- Agent Operations ---
    const refreshAgents = async () => {
        try {
            const res = await fetch(`${API_BASE}/agents`);
            if (res.ok) setAgents(await res.json());
        } catch (e) { console.error("Fetch agents failed", e); }
    };

    const saveAgent = async (agent: Agent) => {
        try {
            const method = agent.id ? "PUT" : "POST";
            const url = agent.id ? `${API_BASE}/agents/${agent.id}` : `${API_BASE}/agents`;

            const res = await fetch(url, {
                method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(agent)
            });
            if (res.ok) await refreshAgents();
        } catch (e) { console.error("Save agent failed", e); }
    };

    const deleteAgent = async (id: string) => {
        try {
            await fetch(`${API_BASE}/agents/${id}`, { method: "DELETE" });
            await refreshAgents();
        } catch (e) { console.error("Delete agent failed", e); }
    };

    // --- Crew Operations ---
    const refreshCrews = async () => {
        try {
            const res = await fetch(`${API_BASE}/crews`);
            if (res.ok) setCrews(await res.json());
        } catch (e) { console.error("Fetch crews failed", e); }
    };

    const saveCrew = async (crew: Crew) => {
        try {
            const url = `${API_BASE}/crews`; // Only POST for now
            const res = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(crew)
            });
            if (res.ok) await refreshCrews();
        } catch (e) { console.error("Save crew failed", e); }
    };


    useEffect(() => {
        setIsLoading(true);
        Promise.all([fetchSettings(), refreshAgents(), refreshCrews()])
            .finally(() => setIsLoading(false));
    }, []);

    return (
        <SettingsContext.Provider value={{
            settings,
            isLoading,
            updateSettings,
            agents,
            refreshAgents,
            saveAgent,
            deleteAgent,
            crews,
            refreshCrews,
            saveCrew
        }}>
            {children}
        </SettingsContext.Provider>
    );
}

export function useSettings() {
    const context = useContext(SettingsContext);
    if (context === undefined) {
        throw new Error('useSettings must be used within a SettingsProvider');
    }
    return context;
}
