"use client";

import { useEffect, useRef, useCallback, useState } from "react";

export type WSReadyState = "connecting" | "open" | "closing" | "closed";

interface UseWebSocketOptions {
  onMessage?: (event: MessageEvent) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (event: Event) => void;
  /** Reconnect on unexpected close. Default: true */
  autoReconnect?: boolean;
  /** Initial backoff in ms. Doubles each attempt, capped at maxDelay. Default: 1000 */
  baseDelay?: number;
  /** Max backoff in ms. Default: 30000 */
  maxDelay?: number;
  /** Max reconnect attempts before giving up. Default: 10 */
  maxAttempts?: number;
}

/**
 * Auto-reconnecting WebSocket hook with exponential backoff.
 * Returns a stable `sendMessage` function and the current connection state.
 */
export function useWebSocket(url: string | null, options: UseWebSocketOptions = {}) {
  const {
    onMessage,
    onOpen,
    onClose,
    onError,
    autoReconnect = true,
    baseDelay = 1000,
    maxDelay = 30_000,
    maxAttempts = 10,
  } = options;

  const wsRef = useRef<WebSocket | null>(null);
  const attemptsRef = useRef(0);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  const onMessageRef = useRef(onMessage);
  const onOpenRef = useRef(onOpen);
  const onCloseRef = useRef(onClose);
  const onErrorRef = useRef(onError);

  // Keep callbacks up-to-date without re-running connect effect
  onMessageRef.current = onMessage;
  onOpenRef.current = onOpen;
  onCloseRef.current = onClose;
  onErrorRef.current = onError;

  const [readyState, setReadyState] = useState<WSReadyState>("closed");

  const connect = useCallback(() => {
    if (!url || !mountedRef.current) return;

    if (wsRef.current) {
      wsRef.current.onopen = null;
      wsRef.current.onmessage = null;
      wsRef.current.onclose = null;
      wsRef.current.onerror = null;
      wsRef.current.close();
    }

    setReadyState("connecting");
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      if (!mountedRef.current) return;
      attemptsRef.current = 0;
      setReadyState("open");
      onOpenRef.current?.();
    };

    ws.onmessage = (event) => {
      if (!mountedRef.current) return;
      onMessageRef.current?.(event);
    };

    ws.onerror = (event) => {
      if (!mountedRef.current) return;
      onErrorRef.current?.(event);
    };

    ws.onclose = (event) => {
      if (!mountedRef.current) return;
      setReadyState("closed");
      onCloseRef.current?.();

      // Don't reconnect on intentional close (code 1000) or if disabled
      if (!autoReconnect || event.code === 1000 || attemptsRef.current >= maxAttempts) return;

      const delay = Math.min(baseDelay * 2 ** attemptsRef.current, maxDelay);
      attemptsRef.current += 1;

      timerRef.current = setTimeout(() => {
        if (mountedRef.current) connect();
      }, delay);
    };
  }, [url, autoReconnect, baseDelay, maxDelay, maxAttempts]);

  useEffect(() => {
    mountedRef.current = true;
    if (url) connect();

    return () => {
      mountedRef.current = false;
      if (timerRef.current) clearTimeout(timerRef.current);
      if (wsRef.current) {
        wsRef.current.onclose = null;
        wsRef.current.close(1000, "component unmounted");
      }
    };
  }, [url, connect]);

  const sendMessage = useCallback((data: string | object) => {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return false;
    ws.send(typeof data === "string" ? data : JSON.stringify(data));
    return true;
  }, []);

  return { readyState, sendMessage };
}
