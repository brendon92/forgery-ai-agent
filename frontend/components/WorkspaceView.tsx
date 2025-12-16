"use client";

import React from 'react';
import WorkspaceSidebar from './WorkspaceSidebar';
import ChatInterface from './ChatInterface';
import SystemHealth from './dashboard/SystemHealth';
import { useWorkspace } from '../context/WorkspaceContext';

export default function WorkspaceView() {
    const { currentConversation } = useWorkspace();

    return (
        <div className="flex h-full w-full overflow-hidden relative">
            {/* 1. Left Panel (File Explorer + Chats) */}
            <WorkspaceSidebar />

            {/* 2. Main Content (Chat or Empty State) */}
            <div className="flex-1 flex flex-col min-w-0 bg-gray-900/30 relative">
                {currentConversation ? (
                    <ChatInterface />
                ) : (
                    <div className="flex flex-col items-center justify-center h-full text-gray-500">
                        <p className="text-lg font-medium">Select a conversation or create a new one</p>
                        <p className="text-sm">Explore your workspace files on the left.</p>
                    </div>
                )}
            </div>

            {/* 3. System Health Panel - Top Right */}
            <div className="absolute top-4 right-0 z-10">
                <SystemHealth />
            </div>
        </div>
    );
}
