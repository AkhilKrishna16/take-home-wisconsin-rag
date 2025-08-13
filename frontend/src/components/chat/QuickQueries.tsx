import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { 
  Shield, 
  Car, 
  Search, 
  AlertTriangle, 
  FileText, 
  Users,
  Zap,
  ChevronDown,
  ChevronUp
} from "lucide-react";
import { apiService } from "@/lib/api";

interface QuickQuery {
  id: string;
  title: string;
  question: string;
  category: string;
  icon: string;
}

interface QuickQueriesProps {
  onQuerySelect: (question: string) => void;
  disabled?: boolean;
}

const iconMap: Record<string, any> = {
  shield: Shield,
  car: Car,
  search: Search,
  'alert-triangle': AlertTriangle,
  'file-text': FileText,
  users: Users,
};

export const QuickQueries = ({ onQuerySelect, disabled = false }: QuickQueriesProps) => {
  const [queries, setQueries] = useState<QuickQuery[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    const loadQueries = async () => {
      try {
        const quickQueries = await apiService.getQuickQueries();
        setQueries(quickQueries);
      } catch (error) {
        console.error('Error loading quick queries:', error);
        // Fallback to default queries if API fails
        setQueries([
          {
            id: 'miranda_rights',
            title: 'Miranda Rights',
            question: 'What are Miranda rights and when must they be read?',
            category: 'Criminal Law',
            icon: 'shield'
          },
          {
            id: 'traffic_stops',
            title: 'Traffic Stops',
            question: 'What are the legal requirements for traffic stops in Wisconsin?',
            category: 'Traffic Law',
            icon: 'car'
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    loadQueries();
  }, []);

  const handleQueryClick = (query: QuickQuery) => {
    onQuerySelect(query.question);
  };

  const getIcon = (iconName: string) => {
    const IconComponent = iconMap[iconName] || Zap;
    return <IconComponent className="h-4 w-4" />;
  };

  if (loading) {
    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium">Quick Queries</h3>
          <div className="h-4 w-4 bg-gray-200 rounded animate-pulse" />
        </div>
        <div className="space-y-2">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="h-10 bg-gray-200 rounded animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">Quick Queries</h3>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setExpanded(!expanded)}
          className="h-6 w-6 p-0"
        >
          {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </Button>
      </div>

      {expanded && (
        <div className="space-y-2">
          {queries.map((query) => (
            <Button
              key={query.id}
              variant="outline"
              size="sm"
              className="w-full justify-start text-left h-auto p-3"
              onClick={() => handleQueryClick(query)}
              disabled={disabled}
            >
              <div className="flex items-start gap-2 w-full">
                <div className="mt-0.5 text-muted-foreground">
                  {getIcon(query.icon)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm">{query.title}</div>
                  <div className="text-xs text-muted-foreground truncate">
                    {query.question}
                  </div>
                </div>
              </div>
            </Button>
          ))}
        </div>
      )}
    </div>
  );
};
