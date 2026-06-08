"use client";

import { useCallback, useRef, useState } from "react";
import { toast } from "sonner";

// ── Event payload types ───────────────────────────────────────────────────────

export interface WSConnectedEvent {
  type: "connected";
  tenant_id: string;
}

export interface WSStockoutAlertEvent {
  type: "stockout_alert";
  severity: "critical" | "warning";
  product_name: string;
  days_remaining: number;
}

export interface WSInventoryAlertEvent {
  type: "inventory_alert";
  severity: "critical" | "warning";
  sku: string;
  product_name: string;
  days_remaining: number;
  qty_on_hand: number;
}

export interface WSOpportunityEvent {
  type: "opportunity_found";
  product_title: string;
  opportunity_score: number;
}

export interface WSAgentUpdateEvent {
  type: "agent_update";
  agent: string;
  finding: string;
}

export interface WSAgentStartedEvent {
  type: "agent_started";
  agent: string;
  run_id: string;
  task: string;
}

export interface WSAgentCompletedEvent {
  type: "agent_completed";
  agent: string;
  run_id: string;
  status: string;
  findings_count: number;
  summary: string;
}

export interface WSPriceAlertEvent {
  type: "price_alert";
  asin: string;
  competitor: string;
  old_price: number;
  new_price: number;
  change_percent: number;
}

export interface WSTrendEvent {
  type: "trend_detected";
  topic: string;
  score: number;
  source: string;
}

export interface WSSystemEvent {
  type: "system";
  level: "info" | "warning" | "error";
  message: string;
}

export type WSEvent =
  | WSConnectedEvent
  | WSStockoutAlertEvent
  | WSInventoryAlertEvent
  | WSOpportunityEvent
  | WSAgentUpdateEvent
  | WSAgentStartedEvent
  | WSAgentCompletedEvent
  | WSPriceAlertEvent
  | WSTrendEvent
  | WSSystemEvent;

// ── Hook ─────────────────────────────────────────────────────────────────────

/**
 * Parses raw WebSocket messages, shows sonner toasts, and tracks the unread
 * notification count so the bell badge can react to live events.
 *
 * Usage:
 *   const { handleRawMessage, unreadCount, clearUnread } = useRealtimeEvents();
 *   useWebSocket(wsUrl, { onMessage: handleRawMessage });
 */
export function useRealtimeEvents() {
  const [unreadCount, setUnreadCount] = useState(0);
  const unreadRef = useRef(0);

  const bump = useCallback(() => {
    unreadRef.current += 1;
    setUnreadCount(unreadRef.current);
  }, []);

  const clearUnread = useCallback(() => {
    unreadRef.current = 0;
    setUnreadCount(0);
  }, []);

  const handleRawMessage = useCallback(
    (event: MessageEvent) => {
      let data: WSEvent;
      try {
        data = JSON.parse(event.data) as WSEvent;
      } catch {
        return;
      }

      switch (data.type) {
        case "connected":
          // Silent — connection confirmed, no toast needed
          break;

        case "stockout_alert":
        case "inventory_alert": {
          const name =
            data.type === "stockout_alert" ? data.product_name : data.product_name;
          const days =
            data.type === "stockout_alert" ? data.days_remaining : data.days_remaining;
          const sev = data.severity;
          const msg = `${name} — ${days}d of stock left`;
          if (sev === "critical") {
            toast.error(msg, {
              description: "Reorder immediately to avoid stockout.",
              action: { label: "View", onClick: () => { window.location.href = "/inventory"; } },
              duration: 8000,
            });
          } else {
            toast.warning(msg, {
              description: "Inventory running low.",
              action: { label: "View", onClick: () => { window.location.href = "/inventory"; } },
              duration: 6000,
            });
          }
          bump();
          break;
        }

        case "opportunity_found":
          toast.success(`New opportunity: ${data.product_title}`, {
            description: `Opportunity score ${data.opportunity_score.toFixed(0)}/100`,
            action: { label: "Explore", onClick: () => { window.location.href = "/products"; } },
            duration: 6000,
          });
          bump();
          break;

        case "agent_started":
          toast.info(`${data.agent} started`, {
            description: data.task || undefined,
            duration: 3000,
          });
          break;

        case "agent_completed":
          if (data.status === "failed") {
            toast.error(`${data.agent} failed`, { description: data.summary || undefined });
          } else {
            toast.success(`${data.agent} finished`, {
              description: data.summary || `${data.findings_count} finding(s)`,
              action: { label: "Results", onClick: () => { window.location.href = "/agents"; } },
              duration: 6000,
            });
          }
          bump();
          break;

        case "agent_update":
          // Quiet — intermediate progress; no toast, no badge increment
          break;

        case "price_alert":
          toast.warning(`Competitor price change on ${data.asin}`, {
            description: `${data.competitor}: $${data.old_price.toFixed(2)} → $${data.new_price.toFixed(2)} (${data.change_percent > 0 ? "+" : ""}${data.change_percent}%)`,
            action: { label: "View", onClick: () => { window.location.href = "/competitors"; } },
            duration: 7000,
          });
          bump();
          break;

        case "trend_detected":
          toast.success(`Trend: ${data.topic}`, {
            description: `Score ${data.score.toFixed(0)} via ${data.source}`,
            action: { label: "View", onClick: () => { window.location.href = "/trends"; } },
            duration: 6000,
          });
          bump();
          break;

        case "system":
          if (data.level === "error") toast.error(data.message);
          else if (data.level === "warning") toast.warning(data.message);
          else toast.info(data.message, { duration: 3000 });
          break;

        default:
          // Unknown event type — ignore silently
          break;
      }
    },
    [bump]
  );

  return { handleRawMessage, unreadCount, clearUnread };
}
