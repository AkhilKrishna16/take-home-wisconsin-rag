import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { SourceCard } from "./SourceCard";
import { StatusBadge } from "./StatusBadge";
import { DocumentUpload } from "./DocumentUpload";
import { QuickQueries } from "./QuickQueries";
import { ExportModal } from "./ExportModal";
import { SaveModal } from "./SaveModal";
import { ConversationHistory } from "./ConversationHistory";
import { Plus, Upload, Save, Download, History, Menu, FileText } from "lucide-react";
import { apiService, ChatMessage as ApiChatMessage, SourceDocument } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: SourceDocument[];
  metadata?: {
    confidence_score?: number;
    safety_warnings?: any;
  };
}

const demoSources: SourceDocument[] = [
  {
    id: "demo1",
    title: "RAG Best Practices – OpenAI Cookbook",
    url: "https://cookbook.openai.com/",
    score: 0.92,
    type: "web",
    jurisdiction: "federal",
    status: "current",
    section: "Best Practices",
    citations: [],
    content_preview: "RAG implementation guidelines...",
    source_number: 1,
  },
  {
    id: "demo2",
    title: "Vector DB Indexing Strategies (PDF)",
    url: "#",
    score: 0.86,
    type: "pdf",
    jurisdiction: "federal",
    status: "current",
    section: "Indexing",
    citations: [],
    content_preview: "Vector database optimization...",
    source_number: 2,
  },
  {
    id: "demo3",
    title: "Internal Knowledge: onboarding.md",
    url: "#",
    score: 0.81,
    type: "doc",
    jurisdiction: "federal",
    status: "current",
    section: "Onboarding",
    citations: [],
    content_preview: "Internal documentation...",
    source_number: 3,
  },
];

export const ChatLayout = () => {
  const { toast } = useToast();
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi! I'm your Wisconsin Statutes RAG assistant. Ask me questions about legal documents and I'll cite the most relevant sources from your knowledge base.",
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [currentSources, setCurrentSources] = useState<SourceDocument[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [documentCount, setDocumentCount] = useState(0);
  const [showHistoryPanel, setShowHistoryPanel] = useState(false);
  const [currentSessionName, setCurrentSessionName] = useState<string | undefined>();

  // Check connection and load document count on mount
  useEffect(() => {
    const checkConnection = async () => {
      const connected = await apiService.healthCheck();
      setIsConnected(connected);
      if (!connected) {
        toast({
          title: "Connection Error",
          description: "Unable to connect to the backend server. Please make sure it's running on localhost:5001",
          variant: "destructive",
        });
      } else {
        // Load document count
        try {
          const documents = await apiService.listDocuments();
          setDocumentCount(documents.length);
        } catch (error) {
          console.error('Error loading document count:', error);
        }
      }
    };
    checkConnection();
  }, [toast]);

  const onSend = async (text: string) => {
    if (!isConnected) {
      toast({
        title: "Not Connected",
        description: "Please ensure the backend server is running",
        variant: "destructive",
      });
      return;
    }

    setMessages((m) => [...m, { role: "user", content: text }]);
    setLoading(true);

    let currentResponse = "";
    let responseSources: SourceDocument[] = [];

    try {
      await apiService.streamChat(
        text,
        (chunk) => {
          if (chunk.type === 'content' && chunk.content) {
            currentResponse += chunk.content;
            setMessages((m) => {
              const newMessages = [...m];
              const lastMessage = newMessages[newMessages.length - 1];
              if (lastMessage && lastMessage.role === 'assistant') {
                lastMessage.content = currentResponse;
              } else {
                newMessages.push({
                  role: 'assistant',
                  content: currentResponse,
                });
              }
              return newMessages;
            });
          }
        },
        (completeResponse) => {
          // Update the last assistant message with metadata
          setMessages((m) => {
            const newMessages = [...m];
            const lastMessage = newMessages[newMessages.length - 1];
            if (lastMessage && lastMessage.role === 'assistant') {
              lastMessage.metadata = {
                confidence_score: completeResponse?.confidence_score,
                safety_warnings: completeResponse?.safety_warnings,
              };
            }
            return newMessages;
          });

          if (completeResponse?.metadata?.source_documents) {
            // Transform backend source documents to frontend format
            responseSources = completeResponse.metadata.source_documents.map((doc: any, index: number) => ({
              id: doc.source_number?.toString() || index.toString(),
              title: doc.file_name || doc.module_title || `Source ${doc.source_number || index + 1}`,
              type: doc.document_type?.toLowerCase() || 'pdf',
              jurisdiction: doc.jurisdiction || 'federal',
              status: doc.law_status || 'current',
              score: doc.relevance_score || 0.8,
              section: doc.section || 'General',
              citations: doc.citations || [],
              content_preview: doc.content_preview || 'No preview available',
              url: '#', // We don't have URLs in the backend data
              source_number: doc.source_number || index + 1,
            }));
            setCurrentSources(responseSources);
          }
          setLoading(false);
        },
        (error) => {
          console.error('Streaming error:', error);
          setMessages((m) => [
            ...m,
            {
              role: "assistant",
              content: `Sorry, I encountered an error: ${error}`,
            },
          ]);
          setLoading(false);
          toast({
            title: "Error",
            description: error,
            variant: "destructive",
          });
        }
      );
    } catch (error) {
      console.error('Error in onSend:', error);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: "Sorry, I encountered an error while processing your request.",
        },
      ]);
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([
      {
        role: "assistant",
        content:
          "Hi! I'm your Wisconsin Statutes RAG assistant. Ask me questions about legal documents and I'll cite the most relevant sources from your knowledge base.",
      },
    ]);
    setCurrentSources([]);
    setCurrentSessionName(undefined);
  };

  const handleQuickQuery = (question: string) => {
    onSend(question);
  };

  const handleSaveChat = () => {
    setShowSaveModal(true);
  };

  const handleUploadComplete = async () => {
    setShowUploadModal(false);
    // Refresh document count
    try {
      const documents = await apiService.listDocuments();
      setDocumentCount(documents.length);
      toast({
        title: "Upload Complete",
        description: "Your documents have been processed and added to the knowledge base.",
      });
    } catch (error) {
      console.error('Error refreshing document count:', error);
    }
  };

  const handleLoadChat = (chatData: any) => {
    // Convert saved chat format to current message format
    const loadedMessages: Message[] = [
      {
        role: "assistant",
        content: "Hi! I'm your Wisconsin Statutes RAG assistant. Ask me questions about legal documents and I'll cite the most relevant sources from your knowledge base.",
      }
    ];

    // Add the saved conversation history
    if (chatData.history && Array.isArray(chatData.history)) {
      chatData.history.forEach((exchange: any) => {
        // Add user message
        loadedMessages.push({
          role: "user",
          content: exchange.question || "Unknown question",
        });

        // Add assistant message
        loadedMessages.push({
          role: "assistant",
          content: exchange.answer || "No answer available",
          sources: exchange.sources || [],
          metadata: {
            confidence_score: exchange.confidence_score,
            safety_warnings: exchange.safety_warnings,
          },
        });
      });
    }

    setMessages(loadedMessages);
    setCurrentSessionName(chatData.session_name);
    setCurrentSources([]); // Clear current sources
    setShowHistoryPanel(false); // Close the history panel
  };

  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-6 md:py-10">
      <header className="mb-6 md:mb-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-xl md:text-2xl">Wisconsin Statutes Chatbot</h1>
            <p className="mt-1 text-sm text-muted-foreground">Find your answers in the Wisconsin Statutes</p>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <StatusBadge 
              label={isConnected ? "Connected" : "Disconnected"} 
              variant={isConnected ? "success" : "destructive"} 
            />
            <Button 
              variant="outline" 
              size="sm"
              className="hover-scale" 
              onClick={() => setShowHistoryPanel(!showHistoryPanel)}
              disabled={!isConnected}
            >
              <History className="mr-2 h-4 w-4" /> History
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              className="hover-scale" 
              onClick={() => setShowUploadModal(true)}
              disabled={!isConnected}
            >
              <Upload className="mr-2 h-4 w-4" /> Upload
              {documentCount > 0 && (
                <span className="ml-2 px-2 py-0.5 text-xs bg-primary text-primary-foreground rounded-full">
                  {documentCount}
                </span>
              )}
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              className="hover-scale" 
              onClick={handleSaveChat}
              disabled={!isConnected || messages.length <= 1}
            >
              <Save className="mr-2 h-4 w-4" /> Save
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              className="hover-scale" 
              onClick={() => setShowExportModal(true)}
              disabled={!isConnected || messages.length <= 1}
            >
              <Download className="mr-2 h-4 w-4" /> Export
            </Button>
            <Button variant="secondary" size="sm" className="hover-scale" onClick={clearChat}>
              <Plus className="mr-2 h-4 w-4" /> New
            </Button>
          </div>
        </div>
      </header>

      <div className={`grid gap-6 ${showHistoryPanel ? 'grid-cols-1 lg:grid-cols-[350px_1fr_320px] xl:grid-cols-[350px_1fr_380px]' : 'grid-cols-1 lg:grid-cols-[1fr_320px] xl:grid-cols-[1fr_380px]'}`}>
        {/* History Panel */}
        {showHistoryPanel && (
          <aside aria-label="Chat History" className="rounded-xl border bg-card p-0">
            <ConversationHistory 
              onLoadChat={handleLoadChat}
              currentSessionName={currentSessionName}
              open={showHistoryPanel}
            />
          </aside>
        )}

        <section aria-label="Conversation" className="rounded-xl border bg-card p-0">
          <ScrollArea className="h-[56vh] px-4 py-4">
            <div className="flex flex-col gap-4">
              {messages.map((m, i) => (
                <ChatMessage 
                  key={i} 
                  role={m.role} 
                  sources={m.role === 'assistant' ? currentSources.slice(0, 2) : undefined}
                  metadata={m.metadata}
                >
                  <p>{m.content}</p>
                </ChatMessage>
              ))}

              {loading && (
                <div className="flex flex-col gap-3">
                  <div className="skeleton h-20 w-3/4 rounded-xl" />
                  <div className="skeleton h-6 w-1/2 rounded-md" />
                </div>
              )}
            </div>
          </ScrollArea>
          <div className="border-t p-4">
            <ChatInput onSend={onSend} disabled={loading || !isConnected} />
          </div>
        </section>

        <aside aria-label="Sidebar" className="space-y-4">
          {/* Quick Queries */}
          <div className="rounded-xl border bg-card p-4">
            <QuickQueries onQuerySelect={handleQuickQuery} disabled={loading || !isConnected} />
          </div>

          {/* Context Sources */}
          <div className="rounded-xl border bg-card p-4">
            <div className="mb-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-primary"></div>
                <h2 className="text-sm font-semibold">Context Sources</h2>
              </div>
              <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded-full">
                {currentSources.length} sources
              </span>
            </div>
            
            {currentSources.length > 0 ? (
              <div className="space-y-3">
                {currentSources.map((s, i) => (
                  <SourceCard key={i} {...s} />
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-xs">No sources yet</p>
                <p className="text-xs">Ask a question to see relevant documents</p>
              </div>
            )}
            
            <Separator className="my-4" />
            <div className="text-xs text-muted-foreground leading-relaxed">
              Documents are semantically indexed and ranked by relevance to your query. 
              Each source shows the most relevant sections from your knowledge base.
            </div>
          </div>
        </aside>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Upload Documents</h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowUploadModal(false)}
                className="h-8 w-8 p-0"
              >
                <Plus className="h-4 w-4 rotate-45" />
              </Button>
            </div>
            <DocumentUpload 
              onUploadComplete={handleUploadComplete}
            />
          </div>
        </div>
      )}

      {/* Export Modal */}
      <ExportModal 
        open={showExportModal} 
        onOpenChange={setShowExportModal} 
      />

      {/* Save Modal */}
      <SaveModal 
        open={showSaveModal} 
        onOpenChange={setShowSaveModal}
        onSaveSuccess={(sessionName) => setCurrentSessionName(sessionName)}
      />
    </div>
  );
};
