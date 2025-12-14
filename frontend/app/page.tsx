import ChatInterface from "@/components/ChatInterface";
import WorkflowGraph from "@/components/visualizer/WorkflowGraph";
import SystemHealth from "@/components/dashboard/SystemHealth";

export default function Home() {
  return (
    <main className="flex h-screen bg-[#050505] text-white p-6 gap-6 overflow-hidden bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-gray-900 via-black to-black">
      {/* Left Column: Interaction & Logs */}
      <div className="w-1/3 h-full flex flex-col gap-6">
        <div className="flex-1 glass-panel rounded-2xl overflow-hidden shadow-2xl">
          <ChatInterface />
        </div>
      </div>

      {/* Right Column: Visualization & Status */}
      <div className="w-2/3 h-full flex flex-col gap-6">
        {/* Top Row: Health Status */}
        <SystemHealth />

        {/* Middle Row: Graph Viz */}
        <div className="flex-1 flex flex-col gap-4">
          <WorkflowGraph />

          {/* Bottom Row / Metric Placeholder (Future: Logs) */}
          <div className="h-48 glass-panel rounded-xl p-4 overflow-y-auto">
            <h3 className="text-xs font-mono text-gray-400 mb-2">// SYSTEM LOGS</h3>
            <div className="font-mono text-xs space-y-1 text-green-400/80">
              <p>[INFO] Forgery Agent System initialized...</p>
              <p>[INFO] Connected to Neo4j (bolt://localhost:7687)</p>
              <p>[INFO] Connected to Qdrant (http://localhost:6333)</p>
              <p>[WAIT] Waiting for user input...</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
