"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

import { config } from '../lib/config';

// Types
type Workspace = {
    id: string;
    title: string;
    goal?: string;
};

type Conversation = {
    id: string;
    workspace_id: string;
    title: string;
    updated_at: string;
};

interface WorkspaceContextType {
    workspaces: Workspace[];
    currentWorkspace: Workspace | null;
    conversations: Conversation[];
    currentConversation: Conversation | null;
    isLoading: boolean;

    // Actions
    setCurrentWorkspace: (ws: Workspace | null) => void;
    setCurrentConversation: (conv: Conversation | null) => void;
    refreshWorkspaces: () => Promise<void>;
    refreshConversations: () => Promise<void>;
    createWorkspace: (title: string, goal?: string) => Promise<void>;
    deleteWorkspace: (id: string) => Promise<void>;
    createConversation: (title: string) => Promise<void>;
}

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined);

export function WorkspaceProvider({ children }: { children: ReactNode }) {
    const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
    const [currentWorkspace, setCurrentWorkspace] = useState<Workspace | null>(null);
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const API_BASE = config.apiBaseUrl;

    const refreshWorkspaces = async () => {
        setIsLoading(true);
        try {
            const res = await fetch(`${API_BASE}/workspaces`);
            if (res.ok) {
                const data = await res.json();
                setWorkspaces(data);
                // Auto-select first if none selected
                if (!currentWorkspace && data.length > 0) {
                    setCurrentWorkspace(data[0]);
                }
            }
        } catch (error) {
            console.error("Failed to fetch workspaces:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const refreshConversations = async () => {
        if (!currentWorkspace) {
            setConversations([]);
            return;
        }
        setIsLoading(true);
        try {
            const res = await fetch(`${API_BASE}/workspaces/${currentWorkspace.id}/conversations`);
            if (res.ok) {
                const data = await res.json();
                setConversations(data);
            }
        } catch (error) {
            console.error("Failed to fetch conversations:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const createWorkspace = async (title: string, goal?: string) => {
        try {
            const res = await fetch(`${API_BASE}/workspaces/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ title, goal })
            });
            if (res.ok) {
                await refreshWorkspaces();
            }
        } catch (error) {
            console.error("Failed to create workspace:", error);
        }
    };

    const deleteWorkspace = async (id: string) => {
        try {
            const res = await fetch(`${API_BASE}/workspaces/${id}`, {
                method: "DELETE"
            });
            if (res.ok) {
                if (currentWorkspace?.id === id) setCurrentWorkspace(null);
                await refreshWorkspaces();
            }
        } catch (error) {
            console.error("Failed to delete workspace:", error);
        }
    };

    const createConversation = async (title: string) => {
        if (!currentWorkspace) return;
        try {
            const res = await fetch(`${API_BASE}/workspaces/${currentWorkspace.id}/conversations`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ title })
            });
            if (res.ok) {
                const newConv = await res.json();
                setConversations(prev => [...prev, newConv]);
                setCurrentConversation(newConv);
            }
        } catch (error) {
            console.error("Failed to create conversation:", error);
        }
    };

    // Effects
    useEffect(() => {
        refreshWorkspaces();
    }, []);

    useEffect(() => {
        if (currentWorkspace) {
            refreshConversations();
        } else {
            setConversations([]);
        }
    }, [currentWorkspace]);

    return (
        <WorkspaceContext.Provider value={{
            workspaces,
            currentWorkspace,
            conversations,
            currentConversation,
            isLoading,
            setCurrentWorkspace,
            setCurrentConversation,
            refreshWorkspaces,
            refreshConversations,
            createWorkspace,
            deleteWorkspace,
            createConversation
        }}>
            {children}
        </WorkspaceContext.Provider>
    );
}

export function useWorkspace() {
    const context = useContext(WorkspaceContext);
    if (context === undefined) {
        throw new Error('useWorkspace must be used within a WorkspaceProvider');
    }
    return context;
}
