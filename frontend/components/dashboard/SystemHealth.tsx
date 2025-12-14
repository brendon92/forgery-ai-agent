"use client";

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Activity, Database, Server, Cpu } from 'lucide-react';

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

export default function SystemHealth() {
    // Mock initial state
    const [status, setStatus] = useState<SystemStatus>({
        neo4j: { status: 'ok', latency: 45 },
        qdrant: { status: 'ok', latency: 12 },
        system: { cpu: 12, memory: 45 }
    });

    useEffect(() => {
        // Mock socket listener for 'health_tick'
        const handleHealthUpdate = (event: CustomEvent) => {
            const data = event.detail;
            // setStatus(data); // In real app
        };
        // window.addEventListener('health_tick', handleHealthUpdate as EventListener);
        // return () => window.removeEventListener('health_tick', handleHealthUpdate as EventListener);
    }, []);

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <HealthCard
                title="Knowledge Graph"
                icon={<Database className="w-5 h-5 text-purple-400" />}
                status={status.neo4j.status}
                value={`${status.neo4j?.latency || 0}ms`}
                label="Neo4j"
            />
            <HealthCard
                title="Vector Memory"
                icon={<Server className="w-5 h-5 text-blue-400" />}
                status={status.qdrant.status}
                value={`${status.qdrant?.latency || 0}ms`}
                label="Qdrant"
            />
            <HealthCard
                title="System Load"
                icon={<Cpu className="w-5 h-5 text-green-400" />}
                status="ok"
                value={`${status.system.cpu}% / ${status.system.memory}%`}
                label="CPU / RAM"
            />
        </div>
    );
}

function HealthCard({ title, icon, status, value, label }: any) {
    const isOk = status === 'ok';
    return (
        <motion.div
            className="glass-panel p-4 rounded-xl flex items-center justify-between"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ scale: 1.02 }}
        >
            <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${isOk ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
                    {icon}
                </div>
                <div>
                    <h4 className="text-sm font-medium text-gray-300">{title}</h4>
                    <p className="text-xs text-gray-500">{label}</p>
                </div>
            </div>

            <div className="text-right">
                <p className={`text-lg font-bold font-mono ${isOk ? 'text-green-400' : 'text-red-400'}`}>
                    {value}
                </p>
                <div className="flex items-center justify-end gap-1 mt-1">
                    <motion.div
                        className={`w-2 h-2 rounded-full ${isOk ? 'bg-green-500' : 'bg-red-500'}`}
                        animate={{ opacity: [1, 0.5, 1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                    />
                    <span className="text-[10px] uppercase tracking-wider text-gray-500">
                        {status.toUpperCase()}
                    </span>
                </div>
            </div>
        </motion.div>
    );
}
