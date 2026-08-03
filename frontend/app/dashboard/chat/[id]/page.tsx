"use client";

import { useParams } from "next/navigation";
import { ChatInterface } from "@/components/chat/chat-interface";

export default function ChatDetailPage() {
  const params = useParams<{ id: string }>();
  const chatId = Number(params.id);
  return <ChatInterface key={chatId} chatId={Number.isFinite(chatId) ? chatId : undefined} />;
}
