import ChatInterface from "@/components/ChatInterface";
import GraphVisualizer from "@/components/GraphVisualizer";

export default function Home() {
  return (
    <main className="flex h-screen bg-black text-white p-4 gap-4">
      <div className="w-1/3 h-full">
        <ChatInterface />
      </div>
      <div className="w-2/3 h-full">
        <GraphVisualizer />
      </div>
    </main>
  );
}
