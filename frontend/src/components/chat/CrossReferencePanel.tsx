import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { 
  Link, 
  Map, 
  TrendingUp, 
  FileText, 
  MapPin, 
  Calendar,
  User,
  BookOpen,
  ExternalLink,
  RefreshCw
} from "lucide-react";
import { apiService } from "@/lib/api";

interface CrossReference {
  document_id: string;
  file_name: string;
  section: string;
  similarity_score: number;
  relevance_score: number;
  common_entities: {
    locations: string[];
    citations: string[];
    keywords: string[];
    names: string[];
  };
  why_relevant?: string;
  metadata?: any;
}

interface CrossReferencePanelProps {
  documentId?: string;
  content?: string;
  query?: string;
  onDocumentSelect?: (documentId: string) => void;
}

export const CrossReferencePanel: React.FC<CrossReferencePanelProps> = ({
  documentId,
  content,
  query,
  onDocumentSelect
}) => {
  const [crossReferences, setCrossReferences] = useState<CrossReference[]>([]);
  const [loading, setLoading] = useState(false);
  const [patterns, setPatterns] = useState<any>(null);
  const [relationshipMap, setRelationshipMap] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'references' | 'patterns' | 'map'>('references');

  const findCrossReferences = async () => {
    if (!content && !query) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${apiService.API_BASE_URL}/cross-reference/find`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_id: documentId,
          content,
          query,
          threshold: 0.1
        }),
      });

      const data = await response.json();
      if (data.success && data.count > 0) {
        setCrossReferences(data.cross_references);
      } else {
        setCrossReferences([]);
        if (activeTab === 'patterns') {
          analyzePatterns();
        }
      }
    } catch (error) {
      console.error('Error finding cross-references:', error);
    } finally {
      setLoading(false);
    }
  };

  const analyzePatterns = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiService.API_BASE_URL}/cross-reference/patterns`);
      const data = await response.json();
      if (data.success) {
        setPatterns(data.patterns);
      }
    } catch (error) {
      console.error('Error analyzing patterns:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateRelationshipMap = async () => {
    if (!documentId) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${apiService.API_BASE_URL}/cross-reference/relationship-map/${documentId}`);
      const data = await response.json();
      if (data.success) {
        setRelationshipMap(data.relationship_map);
      }
    } catch (error) {
      console.error('Error generating relationship map:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'references' && (content || query)) {
      findCrossReferences();
    } else if (activeTab === 'patterns') {
      analyzePatterns();
    } else if (activeTab === 'map' && documentId) {
      generateRelationshipMap();
    }
  }, [activeTab, content, query, documentId]);

  const getSimilarityColor = (score: number) => {
    if (score >= 0.7) return 'bg-green-500';
    if (score >= 0.5) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const renderEntityBadges = (entities: any) => {
    const badges = [];
    
    if (entities.locations?.length > 0) {
      badges.push(
        <Badge key="locations" variant="outline" className="text-xs">
          <MapPin className="w-3 h-3 mr-1" />
          {entities.locations.length} locations
        </Badge>
      );
    }
    
    if (entities.citations?.length > 0) {
      badges.push(
        <Badge key="citations" variant="outline" className="text-xs">
          <BookOpen className="w-3 h-3 mr-1" />
          {entities.citations.length} citations
        </Badge>
      );
    }
    
    if (entities.keywords?.length > 0) {
      badges.push(
        <Badge key="keywords" variant="outline" className="text-xs">
          <FileText className="w-3 h-3 mr-1" />
          {entities.keywords.length} topics
        </Badge>
      );
    }
    
    if (entities.names?.length > 0) {
      badges.push(
        <Badge key="names" variant="outline" className="text-xs">
          <User className="w-3 h-3 mr-1" />
          {entities.names.length} names
        </Badge>
      );
    }
    
    return badges;
  };

  const renderPatterns = () => {
    if (!patterns) return <div className="text-muted-foreground">No patterns available</div>;
    
    return (
      <div className="space-y-4">
        <div>
          <h4 className="font-semibold mb-2">Most Connected Documents</h4>
          <div className="space-y-2">
            {patterns.most_connected_documents?.slice(0, 5).map((doc: any, i: number) => (
              <div key={i} className="flex justify-between items-center p-2 bg-muted rounded">
                <span className="text-sm">{doc[0]}</span>
                <Badge variant="secondary">{doc[1]} connections</Badge>
              </div>
            ))}
          </div>
        </div>
        
        <Separator />
        
        <div>
          <h4 className="font-semibold mb-2">Common Locations</h4>
          <div className="flex flex-wrap gap-1">
            {Object.entries(patterns.common_locations || {}).slice(0, 10).map(([location, count]: any) => (
              <Badge key={location} variant="outline" className="text-xs">
                {location} ({count})
              </Badge>
            ))}
          </div>
        </div>
        
        <Separator />
        
        <div>
          <h4 className="font-semibold mb-2">Common Legal Topics</h4>
          <div className="flex flex-wrap gap-1">
            {Object.entries(patterns.common_keywords || {}).slice(0, 10).map(([keyword, count]: any) => (
              <Badge key={keyword} variant="outline" className="text-xs">
                {keyword} ({count})
              </Badge>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderRelationshipMap = () => {
    if (!relationshipMap) return <div className="text-muted-foreground">No relationship map available</div>;
    
    const renderConnections = (connections: any, depth = 0) => {
      return Object.entries(connections).map(([docId, data]: any) => (
        <div key={docId} className={`ml-${depth * 4} border-l-2 border-muted pl-2 mb-2`}>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${getSimilarityColor(data.similarity)}`} />
            <span className="text-sm font-medium">{docId}</span>
            <Badge variant="outline" className="text-xs">
              {Math.round(data.similarity * 100)}%
            </Badge>
          </div>
          {Object.keys(data.connections).length > 0 && (
            <div className="mt-1">
              {renderConnections(data.connections, depth + 1)}
            </div>
          )}
        </div>
      ));
    };
    
    return (
      <div>
        <h4 className="font-semibold mb-2">Document Relationships</h4>
        <div className="space-y-2">
          {renderConnections(relationshipMap.relationships)}
        </div>
      </div>
    );
  };

  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Link className="w-5 h-5" />
            Cross-References
          </CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              if (activeTab === 'references') findCrossReferences();
              else if (activeTab === 'patterns') analyzePatterns();
              else if (activeTab === 'map') generateRelationshipMap();
            }}
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
        
        <div className="flex gap-1">
          <Button
            variant={activeTab === 'references' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setActiveTab('references')}
          >
            <FileText className="w-4 h-4 mr-1" />
            References
          </Button>
          <Button
            variant={activeTab === 'patterns' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setActiveTab('patterns')}
          >
            <TrendingUp className="w-4 h-4 mr-1" />
            Patterns
          </Button>
          <Button
            variant={activeTab === 'map' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setActiveTab('map')}
          >
            <Map className="w-4 h-4 mr-1" />
            Map
          </Button>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <ScrollArea className="h-[400px]">
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <RefreshCw className="w-6 h-6 animate-spin" />
            </div>
          ) : activeTab === 'references' ? (
            <div className="space-y-3">
              {crossReferences.length === 0 ? (
                <div className="text-center text-muted-foreground py-8">
                  <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>No cross-references found</p>
                  <p className="text-xs">Try adjusting the similarity threshold</p>
                </div>
              ) : (
                crossReferences.map((ref, index) => (
                  <Card key={index} className="p-3 hover:bg-muted/50 transition-colors">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <h4 className="font-medium text-sm">{ref.file_name}</h4>
                        <p className="text-xs text-muted-foreground">Section: {ref.section}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full ${getSimilarityColor(ref.similarity_score)}`} />
                        <span className="text-xs font-medium">
                          {Math.round(ref.similarity_score * 100)}%
                        </span>
                      </div>
                    </div>
                    
                    {ref.why_relevant && (
                      <p className="text-xs text-muted-foreground mb-2">
                        {ref.why_relevant}
                      </p>
                    )}
                    
                    <div className="flex flex-wrap gap-1 mb-2">
                      {renderEntityBadges(ref.common_entities)}
                    </div>
                    
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onDocumentSelect?.(ref.document_id)}
                        className="text-xs"
                      >
                        <ExternalLink className="w-3 h-3 mr-1" />
                        View
                      </Button>
                    </div>
                  </Card>
                ))
              )}
            </div>
          ) : activeTab === 'patterns' ? (
            renderPatterns()
          ) : (
            renderRelationshipMap()
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
};
