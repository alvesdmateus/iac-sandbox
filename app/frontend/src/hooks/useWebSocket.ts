'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import type { WSEvent } from '@/types/websocket';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

interface UseWebSocketOptions {
  autoConnect?: boolean;
  reconnect?: boolean;
  reconnectInterval?: number;
}

interface UseWebSocketReturn {
  socket: Socket | null;
  isConnected: boolean;
  subscribe: (callback: (event: WSEvent) => void) => () => void;
  subscribeToStack: (stackName: string) => void;
  subscribeToDeployment: (deploymentId: string) => void;
  emit: (event: string, data: any) => void;
  connect: () => void;
  disconnect: () => void;
}

export function useWebSocket(
  options: UseWebSocketOptions = {}
): UseWebSocketReturn {
  const {
    autoConnect = true,
    reconnect = true,
    reconnectInterval = 5000,
  } = options;

  const socketRef = useRef<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const listenersRef = useRef<Set<(event: WSEvent) => void>>(new Set());
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  const connect = useCallback(() => {
    if (socketRef.current?.connected) {
      return;
    }

    console.log('[WebSocket] Connecting to:', WS_URL);

    const socket = io(WS_URL, {
      path: '/ws/socket.io',
      transports: ['websocket', 'polling'],
      reconnection: reconnect,
      reconnectionDelay: reconnectInterval,
      reconnectionAttempts: Infinity,
    });

    socket.on('connect', () => {
      console.log('[WebSocket] Connected:', socket.id);
      setIsConnected(true);
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    });

    socket.on('disconnect', (reason) => {
      console.log('[WebSocket] Disconnected:', reason);
      setIsConnected(false);

      if (reconnect && reason === 'io server disconnect') {
        // Server disconnected, try to reconnect
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, reconnectInterval);
      }
    });

    socket.on('connect_error', (error) => {
      console.error('[WebSocket] Connection error:', error);
      setIsConnected(false);
    });

    socket.on('connection:confirmed', (data) => {
      console.log('[WebSocket] Connection confirmed:', data);
    });

    socket.on('subscription:confirmed', (data) => {
      console.log('[WebSocket] Subscription confirmed:', data);
    });

    // Listen to all events and broadcast to subscribers
    socket.onAny((eventName: string, data: any) => {
      const event: WSEvent = {
        type: eventName,
        timestamp: new Date().toISOString(),
        data: data,
      };

      listenersRef.current.forEach((callback) => {
        try {
          callback(event);
        } catch (error) {
          console.error('[WebSocket] Error in listener:', error);
        }
      });
    });

    socketRef.current = socket;
  }, [reconnect, reconnectInterval]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (socketRef.current) {
      console.log('[WebSocket] Disconnecting');
      socketRef.current.disconnect();
      socketRef.current = null;
      setIsConnected(false);
    }
  }, []);

  const subscribe = useCallback((callback: (event: WSEvent) => void) => {
    listenersRef.current.add(callback);

    // Return unsubscribe function
    return () => {
      listenersRef.current.delete(callback);
    };
  }, []);

  const subscribeToStack = useCallback((stackName: string) => {
    if (socketRef.current?.connected) {
      console.log('[WebSocket] Subscribing to stack:', stackName);
      socketRef.current.emit('subscribe_stack', { stackName });
    }
  }, []);

  const subscribeToDeployment = useCallback((deploymentId: string) => {
    if (socketRef.current?.connected) {
      console.log('[WebSocket] Subscribing to deployment:', deploymentId);
      socketRef.current.emit('subscribe_deployment', { deploymentId });
    }
  }, []);

  const emit = useCallback((event: string, data: any) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit(event, data);
    } else {
      console.warn('[WebSocket] Cannot emit, not connected');
    }
  }, []);

  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    socket: socketRef.current,
    isConnected,
    subscribe,
    subscribeToStack,
    subscribeToDeployment,
    emit,
    connect,
    disconnect,
  };
}

export default useWebSocket;
