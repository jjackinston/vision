"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { Send, Bot, User, RefreshCw, Zap, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const NODE_LABELS: Record<string, { label: string; color: string }> = {
  product_research: { label: "Product Research Agent",    color: "text-violet-400" },
  trend:            { label: "Trend Detection Agent",     color: "text-blue-400" },
  competitor:       { label: "Competitor Analysis Agent", color: "text-amber-400" },
  inventory:        { label: "Inventory Planning Agent",  color: "text-red-400" },
  ppc:              { label: "PPC Optimization Agent",    color: "text-emerald-400" },
  supplier:         { label: "Supplier Intelligence Agent", color: "text-pink-400" },
  listing:          { label: "Listing Optimization Agent", color: "text-sky-400" },
};

const SUGGESTIONS = [
  "What products should I reorder this week?",
  "Which keywords have the best opportunity right now?",
  "Who are my most dangerous competitors and why?",
  "How can I reduce my ACoS below 20%?",
  "What trends should I be launching products for?",
];

interface Message {
  role: "user" | "assistant";
  content: string;
  node?: string;
  streaming?: boolean;
}

export function AgentChatPanel() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello! I'm your AI Agent Fleet. Ask me anything about your products, competitors, PPC, inventory, or strategy — I'll coordinate the right specialists to give you real insights.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [activeNode, setActiveNode] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = useCallback(async (text?: string) => {
    const userMsg = (text ?? input).trim();
    if (!userMsg || isStreaming) return;
    setInput("");
    setIsStreaming(true);
    setActiveNode(null);

    setMessages((prev) => [
      ...prev,
      { role: "user", content: userMsg },
      { role: "assistant", content: "", streaming: true },
    ]);

    try {
      // Get Clerk token if available (dev mode works without it)
      let token: string | null = null;
      try {
        token = await (window as any).__clerk?.session?.getToken();
      } catch {}

      const res = await fetch(
        `${API_BASE}/api/v1/agents/chat/stream?message=${encodeURIComponent(userMsg)}`,
        {
          method: "POST",
          headers: {
            Accept: "text/event-stream",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        }
      );

      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let accumulated = "";
      let currentNode = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const raw = line.slice(6).trim();
          if (raw === "[DONE]") break;
          try {
            const parsed = JSON.parse(raw);
            if (parsed.node && parsed.node !== currentNode) {
              currentNode = parsed.node;
              setActiveNode(currentNode);
            }
            if (parsed.content) {
              accumulated += parsed.content;
              const snap = accumulated;
              const nodeSnap = currentNode;
              setMessages((prev) => {
                const next = [...prev];
                const last = next[next.length - 1];
                if (last?.streaming) {
                  next[next.length - 1] = {
                    ...last,
                    content: snap,
                    node: nodeSnap,
                  };
                }
                return next;
              });
            }
          } catch {}
        }
      }
    } catch {
      setMessages((prev) => {
        const next = [...prev];
        const last = next[next.length - 1];
        if (last?.streaming) {
          next[next.length - 1] = {
            ...last,
            content:
              "I couldn't reach the agent fleet right now. Make sure the backend is running on port 8000.",
            streaming: false,
          };
        }
        return next;
      });
    } finally {
      // Finalize last message
      setMessages((prev) => {
        const next = [...prev];
        const last = next[next.length - 1];
        if (last?.streaming) {
          next[next.length - 1] = { ...last, streaming: false };
        }
        return next;
      });
      setIsStreaming(false);
      setActiveNode(null);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [input, isStreaming]);

  return (
    <div className="flex flex-col h-[620px] bg-[#111218] border border-white/5 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-3 px-5 py-3.5 border-b border-white/5 bg-gradient-to-r from-violet-500/8 to-transparent flex-shrink-0">
        <div className="w-8 h-8 rounded-lg bg-violet-500/20 flex items-center justify-center">
          <Bot className="w-4 h-4 text-violet-400" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-white">Agent Fleet Chat</p>
          <p className="text-[10px] text-white/30">
            {isStreaming && activeNode
              ? <span className="flex items-center gap-1">
                  <span className={cn("font-medium", NODE_LABELS[activeNode]?.color ?? "text-violet-400")}>
                    {NODE_LABELS[activeNode]?.label ?? activeNode}
                  </span>
                  <span className="text-white/20">is responding…</span>
                </span>
              : "Multi-agent LangGraph · 7 specialists"
            }
          </p>
        </div>
        <div className="flex items-center gap-1.5">
          <div className={cn(
            "w-1.5 h-1.5 rounded-full transition-colors",
            isStreaming ? "bg-amber-400 animate-pulse" : "bg-emerald-500"
          )} />
          <span className={cn("text-[10px]", isStreaming ? "text-amber-400" : "text-emerald-400")}>
            {isStreaming ? "Thinking…" : "Ready"}
          </span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
        {messages.map((msg, i) => {
          const nodeInfo = msg.node ? NODE_LABELS[msg.node] : null;
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.15 }}
              className={cn("flex gap-2.5", msg.role === "user" ? "flex-row-reverse" : "flex-row")}
            >
              {/* Avatar */}
              <div className={cn(
                "w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5",
                msg.role === "user" ? "bg-violet-500/20" : "bg-white/5"
              )}>
                {msg.role === "user"
                  ? <User className="w-3 h-3 text-violet-400" />
                  : <Bot className="w-3 h-3 text-white/40" />
                }
              </div>

              {/* Bubble */}
              <div className={cn("max-w-[82%] space-y-1", msg.role === "user" && "items-end flex flex-col")}>
                {nodeInfo && (
                  <p className={cn("text-[9px] flex items-center gap-1", nodeInfo.color)}>
                    <Zap className="w-2.5 h-2.5" />
                    {nodeInfo.label}
                  </p>
                )}
                <div className={cn(
                  "rounded-xl px-3.5 py-2.5 text-xs leading-relaxed whitespace-pre-wrap",
                  msg.role === "user"
                    ? "bg-violet-600/25 text-white border border-violet-500/20"
                    : "bg-white/5 text-white/80 border border-white/5"
                )}>
                  {msg.content
                    ? msg.content
                    : msg.streaming && (
                      <span className="flex items-center gap-1 py-0.5">
                        {[0, 1, 2].map((j) => (
                          <motion.span
                            key={j}
                            className="inline-block w-1.5 h-1.5 bg-white/30 rounded-full"
                            animate={{ opacity: [0.2, 0.9, 0.2] }}
                            transition={{ repeat: Infinity, duration: 1.4, delay: j * 0.25 }}
                          />
                        ))}
                      </span>
                    )
                  }
                </div>
              </div>
            </motion.div>
          );
        })}
        <div ref={bottomRef} />
      </div>

      {/* Suggestions — only show when no conversation yet */}
      {messages.length <= 1 && (
        <div className="px-4 pb-3 flex gap-2 overflow-x-auto flex-shrink-0">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => sendMessage(s)}
              className="flex-shrink-0 text-[10px] bg-white/5 hover:bg-violet-500/15 border border-white/8 hover:border-violet-500/30 text-white/40 hover:text-violet-300 px-2.5 py-1.5 rounded-lg transition-all max-w-[200px] text-left leading-tight"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="p-3 border-t border-white/5 flex-shrink-0">
        <div className="flex items-center gap-2">
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
            disabled={isStreaming}
            placeholder="Ask the agent fleet anything..."
            className="flex-1 bg-white/5 border border-white/8 rounded-lg px-3.5 py-2 text-sm text-white placeholder:text-white/20 outline-none focus:border-violet-500/40 disabled:opacity-40 transition-colors"
          />
          <Button
            onClick={() => sendMessage()}
            disabled={!input.trim() || isStreaming}
            size="icon"
            className="bg-violet-600 hover:bg-violet-500 h-9 w-9 flex-shrink-0 disabled:opacity-30"
          >
            {isStreaming
              ? <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              : <Send className="w-3.5 h-3.5" />
            }
          </Button>
        </div>
        <div className="flex items-center gap-1 mt-1.5 px-1">
          <Sparkles className="w-2.5 h-2.5 text-white/15" />
          <p className="text-[9px] text-white/15">
            Powered by LangGraph multi-agent orchestration · Enter to send
          </p>
        </div>
      </div>
    </div>
  );
}
