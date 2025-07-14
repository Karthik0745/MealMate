import { useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import { useAuth } from '../contexts/AuthContext';
import { SocketEvent } from '../types';

export const useSocket = () => {
  const socketRef = useRef<Socket | null>(null);
  const { user, isAuthenticated } = useAuth();

  useEffect(() => {
    if (!isAuthenticated || !user) {
      // Disconnect if not authenticated
      if (socketRef.current) {
        socketRef.current.disconnect();
        socketRef.current = null;
      }
      return;
    }

    // Connect to socket server
    const token = localStorage.getItem('mealmate_token');
    socketRef.current = io(process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000', {
      auth: { token },
      transports: ['websocket', 'polling']
    });

    const socket = socketRef.current;

    socket.on('connect', () => {
      console.log('Connected to server');
      socket.emit('join_user_room', { token });
    });

    socket.on('disconnect', () => {
      console.log('Disconnected from server');
    });

    socket.on('connect_error', (error) => {
      console.error('Socket connection error:', error);
    });

    return () => {
      if (socket) {
        socket.disconnect();
      }
    };
  }, [isAuthenticated, user]);

  const on = <K extends keyof SocketEvent>(
    event: K,
    callback: (data: SocketEvent[K]) => void
  ) => {
    if (socketRef.current) {
      socketRef.current.on(event, callback);
    }
  };

  const off = <K extends keyof SocketEvent>(
    event: K,
    callback?: (data: SocketEvent[K]) => void
  ) => {
    if (socketRef.current) {
      if (callback) {
        socketRef.current.off(event, callback);
      } else {
        socketRef.current.off(event);
      }
    }
  };

  const emit = (event: string, data?: any) => {
    if (socketRef.current) {
      socketRef.current.emit(event, data);
    }
  };

  return { on, off, emit, isConnected: !!socketRef.current?.connected };
};