"use client";

import { useState } from "react";
import { Bot, Check, Copy, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { Markdown } from "@/components/shared/markdown";
import { Badge } from "@/components/ui/badge";
import { AgentResults } from "@/components/chat/agent-results";

export interface LocalMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  agent?: string;
  model?: string;
  data?: Record<string, unknown> | null;
  streaming?: boolean;
  error?: boolean;
}

const AGENT_LABELS: Record<string, string> = {
  general_chat: "General Assistant",
  symptom_analysis: "Symptom Analysis Agent",
  medicine: "Medicine Information Agent",
  doctor: "Doctor Recommendation Agent",
  emergency: "Emergency Detection Agent",
  appointment: "Appointment Agent",
};

export function agentLabel(agent?: string) {
  if (!agent) return "AI Assistant";
  return AGENT_LABELS[agent] ?? agent.replace(/_/g, " ");
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };
  return (
    <button
      onClick={copy}
      className="flex h-7 w-7 items-center justify-center rounded-md text-muted-foreground opacity-0 transition-opacity hover:bg-muted hover:text-foreground group-hover:opacity-100"
      aria-label="Copy message"
    >
      {copied ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
    </button>
  );
}

function TypingIndicator() {
  return (
    <span className="flex h-5 items-center gap-1">
      <span className="typing-dot" />
      <span className="typing-dot" />
      <span className="typing-dot" />
    </span>
  );
}

export function ChatMessage({ message }: { message: LocalMessage }) {
  const isUser = message.role === "user";

  return (
    <div className={cn("group flex gap-3 py-4", isUser && "justify-end")}>
      {!isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
          <Bot className="h-4 w-4" />
        </div>
      )}

      <div className={cn("max-w-[85%] sm:max-w-[75%]", isUser && "order-first")}>
        {isUser ? (
          <div className="rounded-2xl rounded-br-sm bg-primary px-4 py-2.5 text-sm text-primary-foreground">
            {message.content}
          </div>
        ) : (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="text-[10px]">
                {agentLabel(message.agent)}
              </Badge>
              {message.model && (
                <span className="text-[10px] text-muted-foreground">{message.model}</span>
              )}
            </div>
            {message.streaming && !message.content ? (
              <div className="rounded-2xl rounded-bl-sm border bg-card px-4 py-3">
                <TypingIndicator />
              </div>
            ) : (
              <div className="rounded-2xl rounded-bl-sm border bg-card px-4 py-3">
                {message.data && <AgentResults data={message.data} />}
                {message.content && <Markdown content={message.content} />}
                {message.error && (
                  <p className="text-sm text-destructive">{message.content}</p>
                )}
              </div>
            )}
          </div>
        )}
        {!isUser && !message.streaming && message.content && <CopyButton text={message.content} />}
      </div>

      {isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary text-secondary-foreground">
          <User className="h-4 w-4" />
        </div>
      )}
    </div>
  );
}
