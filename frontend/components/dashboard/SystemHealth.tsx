"use client";

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Database, Server, Cpu, ChevronRight, ChevronLeft } from 'lucide-react';

interface HealthMetric {
    status: 'ok' | 'error' | 'warning';
    latency?: number;
    details?: string;
}

interface SystemStatus {
    neo4j: HealthMetric;
    qdrant: HealthMetric;
    system: {
        cpu: number;
        memory: number;
    };
}

// Calculate overall health status
function getOverallHealth(status: SystemStatus): 'ok' | 'warning' | 'error' {
    const statuses = [status.neo4j.status, status.qdrant.status];

    if (statuses.includes('error')) return 'error';
    if (statuses.includes('warning')) return 'warning';
    return 'ok';
}

function getHealthColor(health: 'ok' | 'warning' | 'error'): string {
    switch (health) {
        case 'ok': return 'bg-green-500';
        case 'warning': return 'bg-yellow-500';
        case 'error': return 'bg-red-500';
    }
}

export default function SystemHealth() {
    const [isMinimized, setIsMinimized] = useState(false);

    // Real health state (start with default values)
    const [status, setStatus] = useState<SystemStatus>({
        neo4j: { status: 'warning', latency: 0, details: 'Connecting...' },
        qdrant: { status: 'warning', latency: 0, details: 'Connecting...' },
        system: { cpu: 0, memory: 0 }
    });

    useEffect(() => {
        // Connect to WebSocket events endpoint for health updates
        const wsUrl = `ws://${window.location.hostname}:8000/ws/events/health-panel-${Date.now()}`;
        let ws: WebSocket | null = null;

        const connect = () => {
            try {
                ws = new WebSocket(wsUrl);

                ws.onopen = () => {
                    console.log('[SystemHealth] Connected to health updates');
                };

                ws.onmessage = (event) => {
                    try {
                        const message = JSON.parse(event.data);
                        if (message.type === 'health_tick') {
                            setStatus(message.data);
                        }
                    } catch (err) {
                        console.error('[SystemHealth] Failed to parse message:', err);
                    }
                };

                ws.onerror = (error) => {
                    console.error('[SystemHealth] WebSocket error:', error);
                };

                ws.onclose = () => {
                    console.log('[SystemHealth] Connection closed');
                };
            } catch (error) {
                console.error('[SystemHealth] Failed to connect:', error);
            }
        };

        connect();

        return () => {
            if (ws) {
                ws.close();
            }
        };
    }, []);

    const overallHealth = getOverallHealth(status);
    const healthColor = getHealthColor(overallHealth);

    return (
        <div className="flex items-start justify-end">
            <AnimatePresence mode="wait">
                {isMinimized ? (
                    // Minimized View - Just health indicator
                    <motion.button
                        key="minimized"
                        initial={{ x: 100, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        exit={{ x: 100, opacity: 0 }}
                        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                        onClick={() => setIsMinimized(false)}
                        className="glass-panel rounded-l-xl p-3 flex items-center gap-2 shadow-lg hover:pr-4 transition-all group"
                    >
                        <ChevronLeft className="w-4 h-4 text-gray-400 group-hover:text-gray-300" />
                        <motion.div
                            className={`w-3 h-3 rounded-full ${healthColor}`}
                            animate={{ opacity: [1, 0.6, 1] }}
                            transition={{ duration: 2, repeat: Infinity }}
                        />
                    </motion.button>
                ) : (
                    // Expanded View - Full panel
                    <motion.div
                        key="expanded"
                        initial={{ x: 100, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        exit={{ x: 100, opacity: 0 }}
                        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                        className="glass-panel rounded-xl p-4 space-y-3 w-80 shadow-lg"
                    >
                        {/* Header with minimize button */}
                        <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                                <Activity className="w-4 h-4 text-gray-400" />
                                <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                                    System Health
                                </h3>
                            </div>
                            <button
                                onClick={() => setIsMinimized(true)}
                                className="p-1 rounded hover:bg-gray-800/50 transition-colors"
                                title="Minimize"
                            >
                                <ChevronRight className="w-4 h-4 text-gray-500 hover:text-gray-300" />
                            </button>
                        </div>

                        <HealthRow
                            icon={<Database className="w-4 h-4 text-purple-400" />}
                            title="Knowledge Graph"
                            label="Neo4j"
                            status={status.neo4j.status}
                            value={`${status.neo4j?.latency || 0}ms`}
                        />
                        <HealthRow
                            icon={<Server className="w-4 h-4 text-blue-400" />}
                            title="Vector Memory"
                            label="Qdrant"
                            status={status.qdrant.status}
                            value={`${status.qdrant?.latency || 0}ms`}
                        />
                        <HealthRow
                            icon={<Cpu className="w-4 h-4 text-green-400" />}
                            title="System Load"
                            label="CPU / RAM"
                            status="ok"
                            value={`${status.system.cpu}% / ${status.system.memory}%`}
                        />
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

function HealthRow({ icon, title, label, status, value }: any) {
    const isOk = status === 'ok';
    return (
        <motion.div
            className="flex items-center justify-between p-3 rounded-lg bg-gray-800/30 hover:bg-gray-800/50 transition-colors"
            whileHover={{ x: 2 }}
        >
            <div className="flex items-center gap-3 flex-1">
                <div className={`p-2 rounded-lg ${isOk ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
                    {icon}
                </div>
                <div className="flex-1">
                    <div className="flex items-center gap-2">
                        <h4 className="text-sm font-medium text-gray-200">{title}</h4>
                        <motion.div
                            className={`w-1.5 h-1.5 rounded-full ${isOk ? 'bg-green-500' : 'bg-red-500'}`}
                            animate={{ opacity: [1, 0.5, 1] }}
                            transition={{ duration: 2, repeat: Infinity }}
                        />
                    </div>
                    <p className="text-xs text-gray-500">{label}</p>
                </div>
            </div>

            <div className="text-right ml-4">
                <p className={`text-sm font-bold font-mono ${isOk ? 'text-green-400' : 'text-red-400'}`}>
                    {value}
                </p>
                <span className="text-[9px] uppercase tracking-wider text-gray-600">
                    {status.toUpperCase()}
                </span>
            </div>
        </motion.div>
    );
}
