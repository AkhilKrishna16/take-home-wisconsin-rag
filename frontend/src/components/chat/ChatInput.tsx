import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send, Square } from "lucide-react";

interface ChatInputProps {
  onSend: (text: string) => void;
  onStop?: () => void;
  disabled?: boolean;
  isGenerating?: boolean;
}

export const ChatInput = ({ onSend, onStop, disabled = false, isGenerating = false }: ChatInputProps) => {
  const [value, setValue] = useState("");

  const submit = () => {
    const text = value.trim();
    if (!text || disabled) return;
    onSend(text);
    setValue("");
  };

  return (
    <div className="group relative rounded-xl border bg-background p-3 shadow-sm focus-within:ring-2 focus-within:ring-primary/60">
      <div className="pointer-events-none absolute inset-0 -z-10 rounded-xl opacity-0 transition-opacity duration-300 group-focus-within:opacity-100" style={{ background: "var(--gradient-primary)" }} />
      <div className="flex items-end gap-2">
        <Textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={disabled ? "Processing..." : "Ask anything… your knowledge base is RAG-augmented"}
          disabled={disabled}
          className="min-h-[60px] md:min-h-[60px] flex-1 resize-none border-0 bg-transparent focus-visible:ring-0 disabled:opacity-50 disabled:cursor-not-allowed"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          onTouchEnd={(e) => {
            // Mobile-friendly touch handling
            if (e.currentTarget.value.trim() && !disabled) {
              // Small delay to prevent accidental submissions
              setTimeout(() => {
                if (e.currentTarget.value.trim() === value.trim()) {
                  submit();
                }
              }, 100);
            }
          }}
        />
        {isGenerating ? (
          <Button 
            onClick={onStop} 
            variant="destructive"
            className="hover-scale" 
            aria-label="Stop generation"
          >
            <Square className="mr-2 h-4 w-4" /> Stop
          </Button>
        ) : (
          <Button onClick={submit} disabled={disabled} className="hover-scale disabled:opacity-50 disabled:cursor-not-allowed" aria-label="Send message">
            <Send className="mr-2 h-4 w-4" /> Send
          </Button>
        )}
      </div>
      <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
        <span>Shift + Enter for newline</span>
        <span>Press Enter to send</span>
      </div>
    </div>
  );
};
