import { cn } from "@/lib/utils";
import { ReactNode } from "react";

export interface ChatMessageProps {
  role: "user" | "assistant";
  children: ReactNode;
  sources?: Array<{ title: string; url?: string }>;
}

export const ChatMessage = ({ role, children, sources }: ChatMessageProps) => {
  const isUser = role === "user";
  return (
    <div className={cn("flex w-full", isUser ? "justify-end" : "justify-start")} role="article" aria-label={isUser ? "User message" : "Assistant message"}>
      <div className={cn("max-w-[85%] rounded-2xl border p-4 shadow-sm animate-fade-in", isUser ? "bg-primary/10 border-primary/20" : "bg-card border-border")}>
        <div className="space-y-2 text-sm leading-relaxed">{children}</div>
        {sources && sources.length > 0 && (
          <div className="mt-3 flex flex-wrap items-center gap-2">
            {sources.map((s, i) => (
              <a
                key={i}
                href={s.url ?? "#"}
                target={s.url ? "_blank" : undefined}
                rel="noreferrer"
                className="rounded-full border border-border bg-background px-3 py-1 text-xs text-muted-foreground hover:bg-accent/50"
              >
                Source {i + 1}: {s.title}
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
