import { ExternalLink, FileText, BookOpen, Shield, Gavel, MapPin, Calendar, Hash, Download } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { apiService } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

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
  filename?: string;
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
  source_number,
  filename
}: SourceCardProps) => {
  const { toast } = useToast();

  const isValidDownloadableFile = (filename: string | undefined): boolean => {
    if (!filename) return false;
    
    // Check if filename has a proper file extension
    const hasValidExtension = /\.(pdf|doc|docx|txt|html|md)$/i.test(filename);
    
    // Check if filename contains invalid patterns that indicate it's not a real file
    const invalidPatterns = [
      'CHAPTER',
      'SECTION', 
      'STATUTE',
      'WISCONSIN STATUTES',
      'Unknown Document',
      'Source ',
      'Document Type',
      'Jurisdiction'
    ];
    
    const hasInvalidPattern = invalidPatterns.some(pattern => 
      filename.toUpperCase().includes(pattern.toUpperCase())
    );
    
    return hasValidExtension && !hasInvalidPattern;
  };

  const handleDownload = async () => {
    if (!filename || !isValidDownloadableFile(filename)) {
      toast({
        title: "Download Error",
        description: "No file available for download",
        variant: "destructive",
      });
      return;
    }

    console.log('SourceCard: Starting download for filename:', filename);

    try {
      await apiService.downloadDocument(filename);
      toast({
        title: "Download Started",
        description: `Downloading ${filename}`,
      });
    } catch (error) {
      console.error('SourceCard: Download error:', error);
      toast({
        title: "Download Failed",
        description: error instanceof Error ? error.message : "Failed to download document",
        variant: "destructive",
      });
    }
  };
  // Get appropriate icon based on document type
  const getIcon = (docType: string) => {
    switch (docType?.toLowerCase()) {
      case 'case_law':
      case 'case_law_section':
        return <Gavel className="h-3.5 w-3.5" />;
      case 'training_module':
        return <BookOpen className="h-3.5 w-3.5" />;
      case 'policy':
      case 'policy_document':
      case 'policy_section':
        return <Shield className="h-3.5 w-3.5" />;
      default:
        return <FileText className="h-3.5 w-3.5" />;
    }
  };

  // Get icon color based on document type
  const getIconColor = (docType: string) => {
    switch (docType?.toLowerCase()) {
      case 'case_law':
      case 'case_law_section':
        return 'text-blue-500 bg-blue-50 dark:bg-blue-950';
      case 'training_module':
        return 'text-green-600 bg-green-50 dark:bg-green-950';
      case 'policy':
      case 'policy_document':
      case 'policy_section':
        return 'text-purple-500 bg-purple-50 dark:bg-purple-950';
      default:
        return 'text-gray-600 bg-gray-50 dark:bg-gray-800';
    }
  };

  // Get badge color based on relevance score
  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900 dark:text-green-200 dark:border-green-800';
    if (score >= 0.6) return 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900 dark:text-yellow-200 dark:border-yellow-800';
    return 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-700';
  };

  return (
    <article
      className={cn(
        "group relative rounded-lg border bg-card p-3 transition-all duration-200",
        "hover:shadow-md hover:border-border/60 hover:bg-card/80",
        "focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary/40"
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-2.5">
        <div className="flex items-center gap-2.5">
          <div className={cn(
            "flex h-7 w-7 items-center justify-center rounded-md border",
            getIconColor(type)
          )}>
            {getIcon(type)}
          </div>
          <div className="flex flex-col">
            <span className="text-xs font-medium text-muted-foreground capitalize">
              {type?.replace(/_/g, ' ')}
            </span>
            {source_number && (
              <span className="text-xs text-muted-foreground/60">#{source_number}</span>
            )}
          </div>
        </div>
        
        {typeof score === "number" && (
          <Badge 
            variant="outline"
            className={cn(
              "text-xs font-medium px-2 py-0.5 border",
              getScoreColor(score)
            )}
          >
            {Math.round(score * 100)}%
          </Badge>
        )}
      </div>

      {/* Title */}
      <h3 className="mb-2.5 text-sm font-semibold leading-tight text-foreground line-clamp-2 group-hover:text-primary transition-colors">
        {title}
      </h3>

      {/* Metadata */}
      <div className="mb-2.5 space-y-1.5">
        {section && section !== 'General' && (
          <div className="flex items-center gap-1.5 text-xs">
            <Hash className="h-3 w-3 text-muted-foreground/60" />
            <span className="text-muted-foreground/80">{section}</span>
          </div>
        )}
        {jurisdiction && jurisdiction !== 'unknown' && (
          <div className="flex items-center gap-1.5 text-xs">
            <MapPin className="h-3 w-3 text-muted-foreground/60" />
            <Badge variant="outline" className="text-xs px-1.5 py-0.5 font-medium capitalize border-muted-foreground/30">
              {jurisdiction}
            </Badge>
          </div>
        )}
        {status && status !== 'current' && (
          <div className="flex items-center gap-1.5 text-xs">
            <Calendar className="h-3 w-3 text-muted-foreground/60" />
            <Badge 
              variant="outline" 
              className="text-xs px-1.5 py-0.5 font-medium capitalize border-muted-foreground/30"
            >
              {status}
            </Badge>
          </div>
        )}
      </div>

      {/* Content preview */}
      {content_preview && (
        <div className="mb-2">
          <p className="text-xs leading-relaxed text-muted-foreground/70 line-clamp-2 group-hover:text-muted-foreground/90 transition-colors">
            {content_preview}
          </p>
        </div>
      )}

      {/* Action buttons */}
      {(url && url !== '#') || (filename && isValidDownloadableFile(filename)) ? (
        <div className="flex items-center justify-between pt-2 border-t border-border/40">
          <div className="flex items-center gap-2">
            {url && url !== '#' && (
              <a
                href={url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-xs font-medium text-primary/80 transition-all hover:text-primary hover:gap-1.5"
              >
                View source
                <ExternalLink className="h-3 w-3" />
              </a>
            )}
            {filename && isValidDownloadableFile(filename) && (
              <button
                onClick={handleDownload}
                className="inline-flex items-center gap-1 text-xs font-medium text-primary/80 transition-all hover:text-primary hover:gap-1.5"
              >
                Download
                <Download className="h-3 w-3" />
              </button>
            )}
          </div>
        </div>
      ) : null}
    </article>
  );
};
