"use client";

import { useState, useEffect, useRef } from "react";
import { Send } from "lucide-react";

export default function ChatInterface() {
    const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
    const [input, setInput] = useState("");
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        ws.current = new WebSocket("ws://localhost:8000/ws/chat");
        ws.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === "update") {
                setMessages((prev) => [...prev, { role: "agent", content: `[${data.node}] ${data.data}` }]);
            } else if (data.type === "complete") {
                setMessages((prev) => [...prev, { role: "system", content: "--- Task Complete ---" }]);
            }
        };
        return () => ws.current?.close();
    }, []);

    const sendMessage = () => {
        if (!input.trim() || !ws.current) return;
        setMessages((prev) => [...prev, { role: "user", content: input }]);
        ws.current.send(JSON.stringify({ message: input }));
        setInput("");
    };

    return (
        <div className="flex flex-col h-full bg-gray-900 text-white p-4 rounded-lg">
            <div className="flex-1 overflow-y-auto space-y-2 mb-4">
                {messages.map((msg, i) => (
                    <div key={i} className={`p-2 rounded ${msg.role === "user" ? "bg-blue-600 self-end" : "bg-gray-700 self-start"}`}>
                        <span className="font-bold text-xs block mb-1">{msg.role.toUpperCase()}</span>
                        {msg.content}
                    </div>
                ))}
            </div>
            <div className="flex gap-2">
                <input
                    className="flex-1 bg-gray-800 p-2 rounded border border-gray-700"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                    placeholder="Type a command..."
                />
                <button onClick={sendMessage} className="bg-blue-500 p-2 rounded hover:bg-blue-600">
                    <Send size={20} />
                </button>
            </div>
        </div>
    );
}
