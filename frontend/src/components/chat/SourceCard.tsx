import { ExternalLink, FileText } from "lucide-react";
import { cn } from "@/lib/utils";

export interface SourceCardProps {
  title: string;
  url?: string;
  score?: number;
  type?: "pdf" | "web" | "doc";
}

export const SourceCard = ({ title, url, score, type = "web" }: SourceCardProps) => {
  return (
    <article
      className={cn(
        "group glass-panel rounded-lg border p-3 transition-all duration-200 hover:-translate-y-1 hover:shadow-elegant"
      )}
    >
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <FileText className="h-4 w-4" aria-hidden />
        <span className="uppercase tracking-wide">{type}</span>
        {typeof score === "number" && (
          <span className="ml-auto text-xs">Relevance: {Math.round(score * 100)}%</span>
        )}
      </div>
      <h3 className="mt-2 truncate text-sm text-foreground">{title}</h3>
      {url && (
        <a
          href={url}
          target="_blank"
          rel="noreferrer"
          className="mt-2 inline-flex items-center gap-1 text-sm text-primary hover:underline"
        >
          Open source <ExternalLink className="h-3.5 w-3.5" />
        </a>
      )}
    </article>
  );
};
