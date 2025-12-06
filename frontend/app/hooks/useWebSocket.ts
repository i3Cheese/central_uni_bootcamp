/**
 * WebSocket hook for real-time board updates
 */

import { useEffect, useRef, useCallback, useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

// Convert HTTP URL to WebSocket URL
const getWsUrl = (httpUrl: string): string => {
  if (httpUrl.startsWith('https://')) {
    return httpUrl.replace('https://', 'wss://');
  }
  if (httpUrl.startsWith('http://')) {
    return httpUrl.replace('http://', 'ws://');
  }
  // If no protocol, assume same origin
  if (typeof window !== 'undefined') {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.host}`;
  }
  return httpUrl;
};

// Event types from backend
export type WSEventType = 
  | 'connected'
  | 'sticker_created'
  | 'sticker_updated'
  | 'sticker_deleted'
  | 'board_updated'
  | 'board_deleted'
  | 'user_joined'
  | 'user_left'
  | 'pong';

export interface WSMessage {
  type: WSEventType;
  data: any;
}

export interface StickerWSData {
  stickerId: number;
  boardId: number;
  x: number;
  y: number;
  width: number;
  height: number;
  color: string;
  text: string;
  layerLevel: number;
  createdBy: number;
  createdAt: string;
  updatedAt: string;
}

export interface BoardWSData {
  boardId: number;
  title: string;
  description: string;
  ownerId: number;
  ownerName: string;
  backgroundColor: string;
  createdAt: string;
  updatedAt: string;
}

export interface UserWSData {
  userId: number;
  userLogin: string;
  connectionCount: number;
}

export interface UseWebSocketOptions {
  boardId: string | number;
  onStickerCreated?: (sticker: StickerWSData) => void;
  onStickerUpdated?: (sticker: StickerWSData) => void;
  onStickerDeleted?: (data: { stickerId: number; boardId: number }) => void;
  onBoardUpdated?: (board: BoardWSData) => void;
  onBoardDeleted?: (data: { boardId: number }) => void;
  onUserJoined?: (user: UserWSData) => void;
  onUserLeft?: (user: UserWSData) => void;
  onConnected?: (data: { boardId: number; userId: number; permission: string; connectionCount: number }) => void;
  onError?: (error: Event) => void;
}

export interface UseWebSocketReturn {
  isConnected: boolean;
  connectionCount: number;
  connect: () => void;
  disconnect: () => void;
}

export function useWebSocket(options: UseWebSocketOptions): UseWebSocketReturn {
  const {
    boardId,
    onStickerCreated,
    onStickerUpdated,
    onStickerDeleted,
    onBoardUpdated,
    onBoardDeleted,
    onUserJoined,
    onUserLeft,
    onConnected,
    onError,
  } = options;

  const wsRef = useRef<WebSocket | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionCount, setConnectionCount] = useState(0);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  const clearTimers = useCallback(() => {
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  const disconnect = useCallback(() => {
    clearTimers();
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, [clearTimers]);

  const connect = useCallback(() => {
    // Don't reconnect if already connected
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const token = localStorage.getItem('token');
    if (!token || !boardId) {
      console.warn('WebSocket: No token or boardId available');
      return;
    }

    const wsBaseUrl = getWsUrl(API_URL);
    const wsUrl = `${wsBaseUrl}/api/v1/ws/boards/${boardId}?token=${encodeURIComponent(token)}`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected to board', boardId);
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;

        // Start ping interval to keep connection alive
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000); // Ping every 30 seconds
      };

      ws.onmessage = (event) => {
        try {
          const message: WSMessage = JSON.parse(event.data);
          
          switch (message.type) {
            case 'connected':
              setConnectionCount(message.data.connectionCount);
              onConnected?.(message.data);
              break;
            case 'sticker_created':
              onStickerCreated?.(message.data);
              break;
            case 'sticker_updated':
              onStickerUpdated?.(message.data);
              break;
            case 'sticker_deleted':
              onStickerDeleted?.(message.data);
              break;
            case 'board_updated':
              onBoardUpdated?.(message.data);
              break;
            case 'board_deleted':
              onBoardDeleted?.(message.data);
              break;
            case 'user_joined':
              setConnectionCount(message.data.connectionCount);
              onUserJoined?.(message.data);
              break;
            case 'user_left':
              setConnectionCount(message.data.connectionCount);
              onUserLeft?.(message.data);
              break;
            case 'pong':
              // Heartbeat response, no action needed
              break;
            default:
              console.log('Unknown WebSocket message type:', message.type);
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        onError?.(error);
      };

      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        setIsConnected(false);
        clearTimers();

        // Attempt to reconnect if not a normal closure
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
          console.log(`WebSocket reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current + 1})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            connect();
          }, delay);
        }
      };
    } catch (err) {
      console.error('Failed to create WebSocket:', err);
    }
  }, [boardId, onStickerCreated, onStickerUpdated, onStickerDeleted, onBoardUpdated, onBoardDeleted, onUserJoined, onUserLeft, onConnected, onError, clearTimers]);

  // Connect on mount and when boardId changes
  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, [boardId]); // Only reconnect when boardId changes

  return {
    isConnected,
    connectionCount,
    connect,
    disconnect,
  };
}

