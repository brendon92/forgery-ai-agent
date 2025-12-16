"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

// Components
import Navbar, { Tab } from "@/components/Navbar";
import WorkspaceView from "@/components/WorkspaceView";
import AgentManager from "@/components/AgentManager";
import CrewBuilder from "@/components/CrewBuilder";
import WorkflowBuilder from "@/components/WorkflowBuilder";
import ModelsManager from "@/components/ModelsManager";
import ToolsManager from "@/components/ToolsManager";
import SettingsView from "@/components/SettingsView";

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>('WORKSPACES');

  return (
    <div className="flex flex-col h-screen w-screen bg-black text-white overflow-hidden font-sans">

      {/* Main Content Area */}
      <main className="flex-1 relative overflow-hidden pb-16">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="h-full w-full"
          >
            {activeTab === 'WORKSPACES' && <WorkspaceView />}

            {activeTab === 'AGENTS' && (
              <div className="h-full p-4 max-w-7xl mx-auto">
                <AgentManager />
              </div>
            )}

            {activeTab === 'CREWS' && (
              <div className="h-full p-4 max-w-7xl mx-auto">
                <CrewBuilder />
              </div>
            )}

            {activeTab === 'MODELS' && <ModelsManager />}

            {activeTab === 'WORKFLOWS' && (
              <div className="h-full w-full">
                <WorkflowBuilder />
              </div>
            )}

            {activeTab === 'MCP_TOOLS' && <ToolsManager />}

            {activeTab === 'SETTINGS' && <SettingsView />}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Bottom Navigation */}
      <Navbar activeTab={activeTab} onTabChange={setActiveTab} />
    </div>
  );
}
