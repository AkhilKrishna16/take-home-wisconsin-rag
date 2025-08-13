import { cn } from "@/lib/utils";
import { ReactNode } from "react";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, AlertTriangle, CheckCircle } from "lucide-react";

export interface ChatMessageProps {
  role: "user" | "assistant";
  children: ReactNode;
  sources?: Array<{ title: string; url?: string }>;
  metadata?: {
    confidence_score?: number;
    safety_warnings?: any;
  };
}

export const ChatMessage = ({ role, children, sources, metadata }: ChatMessageProps) => {
  const isUser = role === "user";
  return (
    <div className={cn("flex w-full", isUser ? "justify-end" : "justify-start")} role="article" aria-label={isUser ? "User message" : "Assistant message"}>
      <div className={cn("max-w-[85%] rounded-lg border p-4 shadow-sm animate-fade-in transition-all duration-200 hover:shadow-md", isUser ? "bg-primary/10 border-primary/20" : "bg-card border-border")}>
        {/* Confidence Indicator for Assistant Messages */}
        {!isUser && metadata?.confidence_score !== undefined && (
          <div className="mb-3 flex items-center gap-2">
            <Badge 
              variant={metadata.confidence_score >= 0.8 ? "default" : metadata.confidence_score >= 0.6 ? "secondary" : "destructive"}
              className="text-xs"
            >
              {metadata.confidence_score >= 0.8 ? (
                <CheckCircle className="mr-1 h-3 w-3" />
              ) : metadata.confidence_score >= 0.6 ? (
                <TrendingUp className="mr-1 h-3 w-3" />
              ) : (
                <AlertTriangle className="mr-1 h-3 w-3" />
              )}
              Match Score: {Math.round(metadata.confidence_score * 100)}%
            </Badge>
          </div>
        )}
        
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
