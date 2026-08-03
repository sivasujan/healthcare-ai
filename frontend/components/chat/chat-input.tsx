"use client";

import { useRef, useState } from "react";
import { ImagePlus, Mic, Send, Square } from "lucide-react";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

interface ChatInputProps {
  disabled?: boolean;
  streaming?: boolean;
  onSend: (text: string) => void;
  onStop: () => void;
}

const MAX_CHARS = 4000;

export function ChatInput({ disabled, streaming, onSend, onStop }: ChatInputProps) {
  const [text, setText] = useState("");
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef<{ stop: () => void } | null>(null);

  const submit = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText("");
  };

  const toggleVoice = () => {
    const SpeechRecognition =
      (window as unknown as Record<string, unknown>).SpeechRecognition ??
      (window as unknown as Record<string, unknown>).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      toast.error("Voice input is not supported in this browser");
      return;
    }

    if (listening) {
      recognitionRef.current?.stop();
      setListening(false);
      return;
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const recognition: any = new (SpeechRecognition as any)();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = true;

    let interim = "";
    recognition.onresult = (event: { resultIndex: number; results: { length: number; [i: number]: { isFinal: boolean; [j: number]: { transcript: string } } } }) => {
      interim = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          setText((prev) => {
            const next = (prev + " " + event.results[i][0].transcript).trim().slice(0, MAX_CHARS);
            return next;
          });
        } else {
          interim += event.results[i][0].transcript;
        }
      }
    };
    recognition.onend = () => setListening(false);
    recognition.onerror = () => {
      setListening(false);
      toast.error("Voice input failed — please try again");
    };

    recognitionRef.current = recognition;
    recognition.start();
    setListening(true);
    toast.info("Listening… speak now", { duration: 3000 });
    void interim;
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-end gap-2 rounded-2xl border bg-card p-2 shadow-sm focus-within:border-primary/50 focus-within:ring-2 focus-within:ring-primary/20">
        <button
          type="button"
          onClick={() => toast.info("Image input is coming soon")}
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          aria-label="Attach image"
        >
          <ImagePlus className="h-4.5 w-4.5" />
        </button>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value.slice(0, MAX_CHARS))}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          placeholder="Describe your symptoms, ask about a medicine, or chat with the assistant…"
          rows={Math.min(5, Math.max(1, text.split("\n").length))}
          className="max-h-40 min-h-9 flex-1 resize-none bg-transparent py-1.5 text-sm outline-none placeholder:text-muted-foreground"
          disabled={disabled}
        />
        <button
          type="button"
          onClick={toggleVoice}
          className={cn(
            "flex h-9 w-9 shrink-0 items-center justify-center rounded-xl transition-colors",
            listening
              ? "animate-pulse bg-red-500 text-white"
              : "text-muted-foreground hover:bg-muted hover:text-foreground"
          )}
          aria-label="Voice input"
        >
          <Mic className="h-4.5 w-4.5" />
        </button>
        {streaming ? (
          <button
            type="button"
            onClick={onStop}
            className="flex h-9 shrink-0 items-center gap-1.5 rounded-xl bg-destructive px-3.5 text-sm font-medium text-destructive-foreground transition-colors hover:bg-destructive/90"
          >
            <Square className="h-3.5 w-3.5 fill-current" /> Stop
          </button>
        ) : (
          <button
            type="button"
            onClick={submit}
            disabled={!text.trim() || disabled}
            className="flex h-9 shrink-0 items-center gap-1.5 rounded-xl bg-primary px-3.5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Send className="h-3.5 w-3.5" />
          </button>
        )}
      </div>
      <p className="text-center text-[10px] text-muted-foreground">
        AI responses are generated for informational purposes and are not a substitute for professional
        medical advice.
      </p>
    </div>
  );
}
