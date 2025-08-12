import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Paperclip, Send } from "lucide-react";

interface ChatInputProps {
  onSend: (text: string) => void;
}

export const ChatInput = ({ onSend }: ChatInputProps) => {
  const [value, setValue] = useState("");

  const submit = () => {
    const text = value.trim();
    if (!text) return;
    onSend(text);
    setValue("");
  };

  return (
    <div className="group relative rounded-xl border bg-background p-3 shadow-sm focus-within:ring-2 focus-within:ring-primary/60">
      <div className="pointer-events-none absolute inset-0 -z-10 rounded-xl opacity-0 transition-opacity duration-300 group-focus-within:opacity-100" style={{ background: "var(--gradient-primary)" }} />
      <div className="flex items-end gap-2">
        <button
          type="button"
          className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-border text-muted-foreground hover:bg-accent/50"
          aria-label="Attach"
        >
          <Paperclip className="h-4 w-4" />
        </button>
        <Textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Ask anything… your knowledge base is RAG-augmented"
          className="min-h-[60px] flex-1 resize-none border-0 bg-transparent focus-visible:ring-0"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
        />
        <Button onClick={submit} className="hover-scale" aria-label="Send message">
          <Send className="mr-2 h-4 w-4" /> Send
        </Button>
      </div>
      <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
        <span>Shift + Enter for newline</span>
        <span>Press Enter to send</span>
      </div>
    </div>
  );
};
