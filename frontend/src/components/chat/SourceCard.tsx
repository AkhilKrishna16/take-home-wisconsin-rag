import { ExternalLink, FileText, BookOpen, Shield, Gavel } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

export interface SourceCardProps {
  id: string;
  title: string;
  url?: string;
  score?: number;
  type?: string;
  jurisdiction?: string;
  status?: string;
  section?: string;
  citations?: string[];
  content_preview?: string;
  source_number?: number;
}

export const SourceCard = ({ 
  title, 
  url, 
  score, 
  type = "web", 
  jurisdiction,
  status,
  section,
  content_preview,
  source_number
}: SourceCardProps) => {
  // Get appropriate icon based on document type
  const getIcon = (docType: string) => {
    switch (docType?.toLowerCase()) {
      case 'case_law':
      case 'case_law_section':
        return <Gavel className="h-4 w-4 text-blue-500" />;
      case 'training_module':
        return <BookOpen className="h-4 w-4 text-green-500" />;
      case 'policy':
      case 'policy_document':
        return <Shield className="h-4 w-4 text-purple-500" />;
      default:
        return <FileText className="h-4 w-4 text-primary" />;
    }
  };

  // Get badge color based on relevance score
  const getScoreVariant = (score: number) => {
    if (score >= 0.8) return "default";
    if (score >= 0.6) return "secondary";
    return "outline";
  };

  return (
    <article
      className={cn(
        "group relative overflow-hidden rounded-xl border bg-gradient-to-br from-card via-card to-card/80 p-4 transition-all duration-300",
        "hover:shadow-lg hover:shadow-primary/10 hover:-translate-y-1 hover:border-primary/20",
        "backdrop-blur-sm animate-in fade-in-0 slide-in-from-bottom-2 duration-500"
      )}
    >
      {/* Header with type and relevance */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/20">
            {getIcon(type)}
          </div>
          <div className="flex flex-col">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              {type?.replace(/_/g, ' ')}
            </span>
            {source_number && (
              <span className="text-xs text-muted-foreground/70">Source #{source_number}</span>
            )}
          </div>
        </div>
        
        {typeof score === "number" && (
          <Badge 
            variant={getScoreVariant(score)}
            className="text-xs font-semibold px-2 py-1"
          >
            {Math.round(score * 100)}% match
          </Badge>
        )}
      </div>

      {/* Title */}
      <h3 className="mb-3 text-sm font-semibold leading-tight text-foreground line-clamp-2 group-hover:text-primary/90 transition-colors">
        {title}
      </h3>

      {/* Metadata grid */}
      <div className="mb-3 space-y-2">
        {section && (
          <div className="flex items-center gap-2 text-xs">
            <span className="text-muted-foreground/70 min-w-[60px]">Section:</span>
            <span className="font-medium text-foreground/90">{section}</span>
          </div>
        )}
        {jurisdiction && (
          <div className="flex items-center gap-2 text-xs">
            <span className="text-muted-foreground/70 min-w-[60px]">Jurisdiction:</span>
            <Badge variant="outline" className="text-xs px-1.5 py-0.5 font-medium capitalize">
              {jurisdiction}
            </Badge>
          </div>
        )}
        {status && (
          <div className="flex items-center gap-2 text-xs">
            <span className="text-muted-foreground/70 min-w-[60px]">Status:</span>
            <Badge 
              variant={status === 'current' ? 'default' : 'secondary'} 
              className="text-xs px-1.5 py-0.5 font-medium capitalize"
            >
              {status}
            </Badge>
          </div>
        )}
      </div>

      {/* Content preview */}
      {content_preview && (
        <div className="mb-3">
          <p className="text-xs leading-relaxed text-muted-foreground/80 line-clamp-3 group-hover:text-muted-foreground transition-colors">
            {content_preview}
          </p>
        </div>
      )}

      {/* Action button */}
      {url && url !== '#' && (
        <div className="flex items-center justify-between pt-2 border-t border-border/50">
          <a
            href={url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 text-xs font-medium text-primary transition-all hover:text-primary/80 hover:gap-2"
          >
            View source
            <ExternalLink className="h-3 w-3" />
          </a>
        </div>
      )}

      {/* Subtle gradient overlay on hover */}
      <div className="absolute inset-0 bg-gradient-to-t from-primary/5 via-transparent to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100 pointer-events-none" />
    </article>
  );
};
