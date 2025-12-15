"use client";

import { useState } from "react";
import ChatInterface from "@/components/ChatInterface";
import WorkflowGraph from "@/components/GraphVisualizer";
import SystemHealth from "@/components/dashboard/SystemHealth";
import Sidebar from "@/components/Sidebar";
import SettingsPanel from "@/components/SettingsPanel";

export default function Home() {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  return (
    <div className="flex h-screen w-screen bg-black text-white overflow-hidden font-sans">

      {/* 1. Left Sidebar */}
      <Sidebar onOpenSettings={() => setIsSettingsOpen(true)} />

      {/* 2. Main Content Area (Chat & Graph) */}
      <main className="flex-1 flex flex-col h-full overflow-hidden relative">
        <div className="flex-1 flex relative">
          {/* Chat takes center stage */}
          <div className="flex-1 flex flex-col min-w-0 bg-gray-900/30">
            <ChatInterface />
          </div>
        </div>
      </main>

      {/* 3. Right Panel (Context/Health) */}
      <aside className="w-80 border-l border-gray-800 bg-gray-900/50 flex flex-col">
        <div className="flex-1 overflow-hidden flex flex-col">
          <div className="h-1/2 border-b border-gray-800 relative">
            <WorkflowGraph />
          </div>
          <div className="h-1/2 p-4">
            <SystemHealth />
          </div>
        </div>
      </aside>

      {/* Modals */}
      {isSettingsOpen && <SettingsPanel onClose={() => setIsSettingsOpen(false)} />}
    </div>
  );
}
