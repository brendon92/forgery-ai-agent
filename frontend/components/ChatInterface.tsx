"use client";

import { useEffect, useState, useRef } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { useWorkspace } from "../context/WorkspaceContext";
import { config } from "../lib/config";

export default function ChatInterface() {
    const { currentConversation, conversations } = useWorkspace();
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState<any[]>([]);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const SOCKET_URL = config.ws("/ws/chat");
    const { sendMessage, lastMessage, readyState } = useWebSocket(SOCKET_URL, {
        shouldReconnect: (closeEvent) => true,
    });

    // Load history when conversation changes
    useEffect(() => {
        if (currentConversation) {
            // Fetch messages from API
            fetch(config.api(`/conversations/${currentConversation.id}/messages`))
                .then(res => res.json())
                .then(data => {
                    const uiMessages = data.map((m: any) => ({
                        type: m.role === 'user' ? 'user' : 'agent',
                        content: m.content
                    }));
                    setMessages(uiMessages);
                })
                .catch(err => console.error("Failed to load history:", err));
        } else {
            setMessages([]);
        }
    }, [currentConversation]);

    // Handle incoming WebSocket messages
    useEffect(() => {
        if (lastMessage !== null) {
            try {
                const data = JSON.parse(lastMessage.data);
                if (data.type === "update") {
                    // Intermediate updates (agent thinking)
                    // Currently opting to not display raw updates to keep UI clean
                } else if (data.type === "complete") {
                    // Reload history to get the full accurate response from DB
                    if (currentConversation) {
                        setTimeout(() => {
                            fetch(config.api(`/conversations/${currentConversation.id}/messages`))
                                .then(res => res.json())
                                .then(data => {
                                    const uiMessages = data.map((m: any) => ({
                                        type: m.role === 'user' ? 'user' : 'agent',
                                        content: m.content
                                    }));
                                    setMessages(uiMessages);
                                });
                        }, 500);
                    }
                }
            } catch (err) {
                console.error("Error parsing message:", err);
            }
        }
    }, [lastMessage, currentConversation]);

    const handleSend = () => {
        if (!input.trim()) return;

        // Optimistic add
        setMessages((prev) => [...prev, { type: "user", content: input }]);

        // Send to WS with conversation_id
        sendMessage(JSON.stringify({
            message: input,
            conversation_id: currentConversation?.id
        }));

        setInput("");
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // If no conversation selected, show placeholder
    if (!currentConversation) {
        return (
            <div className="flex items-center justify-center h-full text-gray-500">
                Select or create a conversation to start.
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-gray-900/50">
            {/* Header */}
            <div className="p-4 border-b border-gray-800 bg-gray-900/80 backdrop-blur">
                <h2 className="text-white font-medium">{currentConversation.title}</h2>
                <div className="text-xs text-green-400 flex items-center gap-1">
                    <span className={`w-2 h-2 rounded-full ${readyState === ReadyState.OPEN ? "bg-green-500" : "bg-red-500"}`}></span>
                    {readyState === ReadyState.OPEN ? "Connected" : "Disconnected"}
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg, idx) => (
                    <div
                        key={idx}
                        className={`p-3 rounded-lg max-w-[80%] ${msg.type === "user"
                                ? "bg-blue-600 ml-auto text-white"
                                : "bg-gray-800 text-gray-200 border border-gray-700"
                            }`}
                    >
                        <div className="text-xs opacity-50 mb-1 uppercase tracking-wider">
                            {msg.type === "user" ? "You" : "Forgery"}
                        </div>
                        <div className="whitespace-pre-wrap">{msg.content}</div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-gray-800 bg-gray-900/80 backdrop-blur">
                <div className="flex gap-2">
                    <input
                        type="text"
                        className="flex-1 bg-gray-800 text-white rounded-lg px-4 py-3 outline-none focus:ring-2 focus:ring-blue-500 transition border border-gray-700 placeholder-gray-500"
                        placeholder="Type your message..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleSend()}
                        disabled={readyState !== ReadyState.OPEN}
                    />
                    <button
                        onClick={handleSend}
                        disabled={readyState !== ReadyState.OPEN}
                        className="bg-blue-600 hover:bg-blue-500 text-white px-6 rounded-lg font-medium transition disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Send
                    </button>
                </div>
            </div>
        </div>
    );
}
