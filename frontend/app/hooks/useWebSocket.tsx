import { useEffect, useRef, useState, useCallback } from 'react';

type WebSocketStatus = 'CONNECTING' | 'OPEN' | 'CLOSING' | 'CLOSED';

interface UseWebSocketOptions {
  onMessage?: (event: MessageEvent) => void;
  reconnectInterval?: number;
  maxRetries?: number;
}

export function useWebSocket(url: string, options: UseWebSocketOptions = {}) {
  const [status, setStatus] = useState<WebSocketStatus>('CLOSED');
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const retriesRef = useRef(0);

  const { onMessage, reconnectInterval = 3000, maxRetries = 5 } = options;

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    // Don't connect if empty url (e.g. initial render before hydration)
    if (!url) return;

    setStatus('CONNECTING');
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus('OPEN');
      retriesRef.current = 0;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
    };

    ws.onclose = () => {
      setStatus('CLOSED');
      wsRef.current = null;

      if (retriesRef.current < maxRetries) {
        reconnectTimeoutRef.current = setTimeout(() => {
          retriesRef.current += 1;
          connect();
        }, reconnectInterval);
      }
    };

    ws.onerror = (error) => {
      // Error will trigger close, which triggers reconnect
      console.error("WebSocket Error:", error);
    };

    ws.onmessage = (event) => {
      if (onMessage) {
        onMessage(event);
      }
    };

  }, [url, onMessage, reconnectInterval, maxRetries]);

  useEffect(() => {
    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  const sendMessage = useCallback((message: string | object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const payload = typeof message === 'string' ? message : JSON.stringify(message);
      wsRef.current.send(payload);
    } else {
      console.warn("WebSocket is not open. Message dropped.");
    }
  }, []);

  return { status, sendMessage };
}
