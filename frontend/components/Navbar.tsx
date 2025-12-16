"use client";

import React from 'react';
import { LayoutGrid, Users, Briefcase, Cpu, Database, Settings, GitBranch } from 'lucide-react';
import { motion } from 'framer-motion';

export type Tab = 'WORKSPACES' | 'AGENTS' | 'CREWS' | 'MODELS' | 'WORKFLOWS' | 'MCP_TOOLS' | 'SETTINGS';

interface NavbarProps {
    activeTab: Tab;
    onTabChange: (tab: Tab) => void;
}

export default function Navbar({ activeTab, onTabChange }: NavbarProps) {
    const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
        { id: 'WORKSPACES', label: 'Workspaces', icon: <LayoutGrid size={20} /> },
        { id: 'AGENTS', label: 'Agents', icon: <Users size={20} /> },
        { id: 'CREWS', label: 'Crews', icon: <Briefcase size={20} /> },
        { id: 'MODELS', label: 'Models', icon: <Cpu size={20} /> },
        { id: 'WORKFLOWS', label: 'Workflows', icon: <GitBranch size={20} /> },
        { id: 'MCP_TOOLS', label: 'MCP / Tools', icon: <Database size={20} /> },
        { id: 'SETTINGS', label: 'Settings', icon: <Settings size={20} /> },
    ];

    return (
        <div className="fixed bottom-0 left-0 right-0 h-16 bg-gray-900/90 backdrop-blur-md border-t border-gray-800 flex items-center justify-center px-4 z-50">
            <div className="flex gap-2">
                {tabs.map((tab) => {
                    const isActive = activeTab === tab.id;
                    return (
                        <button
                            key={tab.id}
                            onClick={() => onTabChange(tab.id)}
                            className={`relative flex flex-col items-center justify-center px-6 py-1 rounded-lg transition-colors duration-200 ${isActive ? 'text-blue-400' : 'text-gray-500 hover:text-gray-300'
                                }`}
                        >
                            {isActive && (
                                <motion.div
                                    layoutId="activeTabBg"
                                    className="absolute inset-0 bg-gray-800 rounded-lg"
                                    initial={false}
                                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                                />
                            )}
                            <span className="relative z-10 mb-1">{tab.icon}</span>
                            <span className="relative z-10 text-[10px] font-medium tracking-wide">{tab.label.toUpperCase()}</span>
                        </button>
                    );
                })}
            </div>
        </div>
    );
}
