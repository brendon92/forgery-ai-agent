export const config = {
    apiBaseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
    wsBaseUrl: process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000",

    // Helper to constructing full API paths
    api: (path: string) => `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}${path.startsWith('/') ? path : '/' + path}`,

    // Helper for WS paths
    ws: (path: string) => `${process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"}${path.startsWith('/') ? path : '/' + path}`
};
