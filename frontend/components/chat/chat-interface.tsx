"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, MessageSquare, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { api, API_BASE_URL, errorMessage, tokenStore } from "@/lib/api";
import type { ChatDetail, ChatMessage as ApiChatMessage } from "@/types";
import { cn } from "@/lib/utils";
import { ChatInput } from "@/components/chat/chat-input";
import { ChatMessage, type LocalMessage } from "@/components/chat/chat-message";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface ChatInterfaceProps {
  chatId?: number;
}

function toLocal(apiMsg: ApiChatMessage): LocalMessage {
  return {
    id: `msg-${apiMsg.id}`,
    role: apiMsg.role,
    content: apiMsg.content,
    agent: apiMsg.agent ?? undefined,
    model: apiMsg.model ?? undefined,
  };
}

interface StreamEvent {
  type: string;
  token?: string;
  chat_id?: number;
  message_id?: number;
  agent?: string;
  model?: string;
  title?: string;
  content?: string;
  data?: Record<string, unknown> | null;
  message?: string;
}

export function ChatInterface({ chatId }: ChatInterfaceProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [messages, setMessages] = useState<LocalMessage[]>([]);
  const [streaming, setStreaming] = useState(false);
  const [loadedId, setLoadedId] = useState<number | undefined>(undefined);
  const [emergency, setEmergency] = useState<StreamEvent | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const { data: chats } = useQuery({
    queryKey: ["chats"],
    queryFn: async () => {
      const { data } = await api.get<{ data: ChatDetail[] }>("/chat");
      return data.data;
    },
  });

  useEffect(() => {
    if (chatId && chatId !== loadedId) {
      setLoadedId(chatId);
      setMessages([]);
      api
        .get<{ data: ChatDetail }>(`/chat/${chatId}`)
        .then(({ data }) => {
          const msgs = data.data.messages.map(toLocal);
          setMessages(msgs);
        })
        .catch((err) => {
          toast.error(errorMessage(err));
          router.replace("/dashboard/chat");
        });
    } else if (!chatId) {
      setMessages([]);
      setLoadedId(undefined);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chatId]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const finalizeStream = useCallback(
    (streamEvent: StreamEvent, pending: LocalMessage) => {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === pending.id
            ? {
                ...m,
                streaming: false,
                content:
                  streamEvent.content !== undefined
                    ? streamEvent.content
                    : m.content,
                agent: streamEvent.agent ?? m.agent,
                model: streamEvent.model ?? m.model,
                data: streamEvent.data ?? m.data,
              }
            : m
        )
      );
    },
    []
  );

  const streamReader = async (
    res: Response,
    handle: (event: string, payload: StreamEvent) => void
  ) => {
    const reader = res.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let idx: number;
      while ((idx = buffer.indexOf("\n\n")) !== -1) {
        const raw = buffer.slice(0, idx);
        buffer = buffer.slice(idx + 2);
        const eventMatch = raw.match(/^event: (.+)$/m);
        const dataMatch = raw.match(/^data: (.+)$/m);
        if (!eventMatch || !dataMatch) continue;
        let payload: StreamEvent;
        try {
          payload = JSON.parse(dataMatch[1]);
        } catch {
          continue;
        }
        handle(eventMatch[1], payload);
      }
    }
  };

  const send = useCallback(
    async (text: string) => {
      setStreaming(true);
      setEmergency(null);
      const controller = new AbortController();
      abortRef.current = controller;

      const assistantId = `assistant-${Date.now()}`;
      const placeholder: LocalMessage = {
        id: assistantId,
        role: "assistant",
        content: "",
        streaming: true,
      };
      setMessages((prev) => [...prev, placeholder]);

      const handle = (event: string, payload: StreamEvent) => {
        if (event === "token" && payload.token) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, content: m.content + payload.token! } : m
            )
          );
        } else if (event === "emergency") {
          setEmergency(payload);
        } else if (event === "done") {
          finalizeStream(payload, { id: assistantId, role: "assistant", content: "" });
          queryClient.invalidateQueries({ queryKey: ["chats"] });
          if (payload.chat_id && payload.chat_id !== chatId) {
            router.replace(`/dashboard/chat/${payload.chat_id}`, { scroll: false });
            setLoadedId(payload.chat_id);
          }
        } else if (event === "error") {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? {
                    ...m,
                    streaming: false,
                    error: true,
                    content: payload.message ?? "Something went wrong while streaming.",
                  }
                : m
            )
          );
        }
      };

      try {
        let access = tokenStore.getAccess();
        const res = await fetch(`${API_BASE_URL}/chat/stream`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${access}`,
          },
          body: JSON.stringify({ message: text, chat_id: chatId ?? undefined }),
          signal: controller.signal,
        });

        if (res.status === 401) {
          const { data } = await api.post("/auth/refresh", {
            refresh_token: tokenStore.getRefresh(),
          });
          access = data.data.access_token;
          const retry = await fetch(`${API_BASE_URL}/chat/stream`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${access}`,
            },
            body: JSON.stringify({ message: text, chat_id: chatId ?? undefined }),
            signal: controller.signal,
          });
          if (!retry.ok || !retry.body) throw new Error("Stream failed");
          await streamReader(retry, handle);
        } else if (!res.ok || !res.body) {
          throw new Error(`Request failed (${res.status})`);
        } else {
          await streamReader(res, handle);
        }
      } catch (err) {
        if ((err as Error).name === "AbortError") return;
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? {
                  ...m,
                  streaming: false,
                  error: true,
                  content: errorMessage(err),
                }
              : m
          )
        );
      } finally {
        setStreaming(false);
      }
    },
    [chatId, finalizeStream, queryClient, router]
  );

  const onSend = useCallback(
    (text: string) => {
      const userMsg: LocalMessage = {
        id: `user-${Date.now()}`,
        role: "user",
        content: text,
      };
      setMessages((prev) => [...prev, userMsg]);
      void send(text);
    },
    [send]
  );

  const onRegenerate = useCallback(() => {
    const lastUser = [...messages].reverse().find((m) => m.role === "user");
    if (!lastUser || streaming) return;
    setMessages((prev) => prev.filter((m) => m.role === "assistant"));
    void send(lastUser.content);
  }, [messages, send, streaming]);

  const onStop = useCallback(() => {
    abortRef.current?.abort();
    setStreaming(false);
    setMessages((prev) =>
      prev.map((m) => (m.streaming ? { ...m, streaming: false } : m))
    );
  }, []);

  const onClear = useCallback(async () => {
    if (!loadedId) {
      setMessages([]);
      return;
    }
    try {
      await api.delete(`/chat/${loadedId}`);
      queryClient.invalidateQueries({ queryKey: ["chats"] });
      setMessages([]);
      router.replace("/dashboard/chat");
    } catch (err) {
      toast.error(errorMessage(err));
    }
  }, [loadedId, queryClient, router]);

  const onNewChat = useCallback(() => {
    if (streaming) abortRef.current?.abort();
    router.push("/dashboard/chat");
  }, [router, streaming]);

  return (
    <div className="flex h-[calc(100dvh-8.5rem)] gap-4 lg:h-[calc(100dvh-10rem)]">
      <div className="hidden w-60 shrink-0 flex-col gap-2 rounded-2xl border bg-card p-2 md:flex">
        <Button
          variant={loadedId ? "outline" : "default"}
          className="justify-start gap-2"
          onClick={onNewChat}
        >
          <Plus className="h-4 w-4" /> New chat
        </Button>
        <div className="flex-1 space-y-1 overflow-y-auto">
          {chats?.map((c) => (
            <button
              key={c.id}
              onClick={() => router.push(`/dashboard/chat/${c.id}`)}
              className={cn(
                "flex w-full items-center gap-2 rounded-lg px-2.5 py-2 text-left text-sm transition-colors hover:bg-muted",
                loadedId === c.id && "bg-primary/10 text-primary hover:bg-primary/10"
              )}
            >
              <MessageSquare className="h-3.5 w-3.5 shrink-0" />
              <span className="truncate">{c.title}</span>
            </button>
          ))}
          {chats && chats.length === 0 && (
            <p className="px-2.5 py-3 text-xs text-muted-foreground">No chats yet</p>
          )}
        </div>
        {loadedId && (
          <Button variant="ghost" size="sm" className="justify-start gap-2 text-muted-foreground" onClick={onClear}>
            <Trash2 className="h-3.5 w-3.5" /> Clear chat
          </Button>
        )}
      </div>

      <div className="flex min-w-0 flex-1 flex-col rounded-2xl border bg-card">
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 sm:px-6">
          {messages.length === 0 && (
            <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                <MessageSquare className="h-7 w-7" />
              </div>
              <div>
                <p className="font-semibold">How can I help you today?</p>
                <p className="mt-1 text-sm text-muted-foreground">
                  Ask about symptoms, medicines, doctors, appointments, or anything else.
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-2">
                {[
                  "I have a headache and fever since 2 days",
                  "Tell me about paracetamol",
                  "Find me a cardiologist nearby",
                  "Book an appointment for tomorrow",
                ].map((s) => (
                  <button
                    key={s}
                    onClick={() => onSend(s)}
                    className="rounded-full border bg-background px-3.5 py-1.5 text-xs transition-colors hover:border-primary/50 hover:bg-primary/5"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((m) => (
            <ChatMessage key={m.id} message={m} />
          ))}
          {!streaming && messages.length > 1 && messages[messages.length - 1].role === "assistant" && !messages[messages.length - 1].error && (
            <div className="flex justify-end pb-4">
              <Button variant="outline" size="sm" onClick={onRegenerate}>
                Regenerate response
              </Button>
            </div>
          )}
        </div>

        {emergency && (
          <div className="mx-4 mb-2 flex items-center gap-3 rounded-xl border-2 border-red-500 bg-red-50 p-3 text-sm dark:bg-red-950/30">
            <AlertTriangle className="h-5 w-5 shrink-0 text-red-600" />
            <p className="text-red-800 dark:text-red-200">
              Possible emergency indicators detected — seek medical help immediately.
            </p>
            <button
              onClick={() => setEmergency(null)}
              className="ml-auto text-xs font-medium text-red-600 underline"
            >
              Dismiss
            </button>
          </div>
        )}

        <div className="border-t p-3 sm:p-4">
          <ChatInput
            disabled={false}
            streaming={streaming}
            onSend={onSend}
            onStop={onStop}
          />
        </div>
      </div>

      {emergency && (
        <div className="pointer-events-none fixed bottom-4 right-4 z-50">
          <Badge variant="danger" className="pointer-events-auto animate-pulse px-3 py-1.5">
            <AlertTriangle className="mr-1 h-3.5 w-3.5" /> Emergency detected
          </Badge>
        </div>
      )}
    </div>
  );
}
