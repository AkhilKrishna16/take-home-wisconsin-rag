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
import { Plus, Upload, Save, Download, History, Menu, FileText, Link, ChevronDown, ChevronUp } from "lucide-react";
import { apiService, ChatMessage as ApiChatMessage, SourceDocument } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

const formatTextWithBullets = (text: string): string => {
  return text.replace(/\*\*([^*]+)\*\*/g, '• $1');
};

const generateChatName = async (firstQuery: string): Promise<string> => {
  const words = firstQuery.split(' ');
  const meaningfulWords = words.filter(word => 
    word.length > 3 && 
    !['what', 'how', 'when', 'where', 'why', 'tell', 'about', 'explain'].includes(word.toLowerCase())
  );
  
  if (meaningfulWords.length >= 2) {
    return meaningfulWords.slice(0, 3).map(w => 
      w.charAt(0).toUpperCase() + w.slice(1)
    ).join(' ');
  }
  
  return 'Legal Inquiry';
};

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

  const filterConversationMessages = (messages: Message[]): Message[] => {
    return messages.filter(msg => {
      if (msg.role === 'assistant' && msg.content.includes("Hi! I'm your Wisconsin Statutes RAG assistant")) {
        return false;
      }
      return true;
    });
  };
  const [loading, setLoading] = useState(false);
  const [currentSources, setCurrentSources] = useState<SourceDocument[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [documentCount, setDocumentCount] = useState(0);
  const [showHistoryPanel, setShowHistoryPanel] = useState(false);
  const [currentSessionName, setCurrentSessionName] = useState<string | undefined>();
  const [currentChatId, setCurrentChatId] = useState<string | undefined>();
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true);
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  const [showCrossReferencePanel, setShowCrossReferencePanel] = useState(false);
  const [crossReferenceResults, setCrossReferenceResults] = useState<(SourceDocument & { similarityScore: number })[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<SourceDocument | null>(null);
  const [contextSourcesExpanded, setContextSourcesExpanded] = useState(true);
  const [crossReferencesExpanded, setCrossReferencesExpanded] = useState(true);

  useEffect(() => {
    const checkConnection = async () => {
      try {
        const connected = await apiService.healthCheck();
        setIsConnected(connected);
        if (!connected) {
          toast({
            title: "Connection Error",
            description: "Unable to connect to the backend server. Please make sure it's running on localhost:5001",
            variant: "destructive",
          });
        } else {
          const timeoutPromise = new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Timeout')), 5000)
          );
          
                      try {
              const documents = await Promise.race([
                apiService.listDocuments(),
                timeoutPromise
              ]) as any[];
              setDocumentCount(documents.length);
            } catch (error) {
            console.error('Error loading document count:', error);
          }
        }
      } catch (error) {
        console.error('Connection check failed:', error);
        setIsConnected(false);
        toast({
          title: "Connection Error",
          description: "Unable to connect to the backend server",
          variant: "destructive",
        });
      }
    };
    checkConnection();
  }, [toast]);

  useEffect(() => {
    return () => {
      if (abortController) {
        abortController.abort();
      }
    };
  }, [abortController]);

  const stopGeneration = () => {
    if (abortController) {
      abortController.abort();
      setAbortController(null);
    }
    setLoading(false);
  };

  const onSend = async (text: string) => {
    if (!isConnected) {
      toast({
        title: "Not Connected",
        description: "Please ensure the backend server is running",
        variant: "destructive",
      });
      return;
    }

    if (!text.trim()) {
      toast({
        title: "Empty Message",
        description: "Please enter a question to ask",
        variant: "destructive",
      });
      return;
    }

    const controller = new AbortController();
    setAbortController(controller);

    setMessages((m) => [...m, { role: "user", content: text }]);
    setLoading(true);
    
    const userMessageCount = messages.filter(m => m.role === 'user').length;
    const isFirstUserMessage = userMessageCount === 0;
    
    if (isFirstUserMessage && autoSaveEnabled) {
      try {
        const chatName = await generateChatName(text);
        setCurrentSessionName(chatName);
        console.log('Generated chat name:', chatName);
      } catch (error) {
        console.error('Error generating chat name:', error);
        setCurrentSessionName('Legal Inquiry');
      }
    }

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
                lastMessage.content = formatTextWithBullets(currentResponse);
              } else {
                newMessages.push({
                  role: 'assistant',
                  content: formatTextWithBullets(currentResponse),
                });
              }
              return newMessages;
            });
          }
        },
        (completeResponse) => {
          
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
          
          if (autoSaveEnabled) {
            setTimeout(() => {
              setMessages(currentMessages => {
                const userMessageCount = currentMessages.filter(m => m.role === 'user').length;
                
                if (userMessageCount > 0) {
                  setTimeout(() => {
                    setCurrentSessionName(latestSessionName => {
                      autoSaveChat(latestSessionName, currentMessages);
                      return latestSessionName;
                    });
                  }, 50);
                }
                
                return currentMessages;
              });
            }, 100);
          }

          if (completeResponse?.metadata?.source_documents) {
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
              url: `http://localhost:5001/api/documents/download/${doc.original_file_name || doc.file_name || `${doc.source_number || index + 1}.pdf`}`,
              source_number: doc.source_number || index + 1,
              filename: doc.original_file_name || doc.file_name,
            }));
            console.log('Processed source documents:', responseSources.map(s => ({ title: s.title, filename: s.filename })));
            setCurrentSources(responseSources);
            
            // CRITICAL: Attach sources to the assistant message in the messages state
            setMessages((m) => {
              const newMessages = [...m];
              const lastMessage = newMessages[newMessages.length - 1];
              if (lastMessage && lastMessage.role === 'assistant') {
                lastMessage.sources = responseSources;
                console.log('Sources attached to assistant message:', responseSources.length, 'sources');
              }
              return newMessages;
            });
          }
          setLoading(false);
          setAbortController(null);
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
          setAbortController(null);
          toast({
            title: "Error",
            description: error,
            variant: "destructive",
          });
        },
        controller
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
      setAbortController(null);
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
    setCurrentChatId(undefined);
    setShowCrossReferencePanel(false);
    setSelectedDocument(undefined);
    setCrossReferenceResults([]);
    setContextSourcesExpanded(true);
    setCrossReferencesExpanded(true);
  };

  const handleQuickQuery = (question: string) => {
    onSend(question);
  };

  const handleCrossReference = async (document: SourceDocument) => {
    setSelectedDocument(document);
    setShowCrossReferencePanel(true);
    
    try {
      // Find similar documents from current sources
      const similarDocuments = findSimilarDocuments(document, currentSources);
      setCrossReferenceResults(similarDocuments);
    } catch (error) {
      console.error('Error finding cross-references:', error);
      setCrossReferenceResults([]);
    }
  };

  const findSimilarDocuments = (targetDoc: SourceDocument, allSources: SourceDocument[]): (SourceDocument & { similarityScore: number })[] => {
    // Filter out the target document itself
    const otherDocs = allSources.filter(doc => doc.id !== targetDoc.id);
    
    if (otherDocs.length === 0) return [];
    
    // Enhanced similarity scoring based on common factors
    const scoredDocs = otherDocs.map(doc => {
      let score = 0;
      
      // Same document type gets points
      if (doc.type === targetDoc.type) score += 3;
      
      // Same jurisdiction gets points
      if (doc.jurisdiction === targetDoc.jurisdiction) score += 2;
      
      // Same status gets points
      if (doc.status === targetDoc.status) score += 1;
      
      // Similar section names get points
      if (doc.section && targetDoc.section && 
          doc.section.toLowerCase().includes(targetDoc.section.toLowerCase()) ||
          targetDoc.section.toLowerCase().includes(doc.section.toLowerCase())) {
        score += 4;
      }
      
      // Common citations get points
      const commonCitations = doc.citations?.filter(citation => 
        targetDoc.citations?.includes(citation)
      ) || [];
      score += commonCitations.length * 3;
      
      // Similar content preview gets points
      if (doc.content_preview && targetDoc.content_preview) {
        const targetWords = targetDoc.content_preview.toLowerCase().split(' ');
        const docWords = doc.content_preview.toLowerCase().split(' ');
        const commonWords = targetWords.filter(word => 
          word.length > 3 && docWords.includes(word)
        );
        score += commonWords.length * 0.5;
      }
      
      // Similar filenames get points
      if (doc.filename && targetDoc.filename) {
        const targetName = targetDoc.filename.toLowerCase();
        const docName = doc.filename.toLowerCase();
        if (targetName.includes(docName.substring(0, 8)) || docName.includes(targetName.substring(0, 8))) {
          score += 2;
        }
      }
      
      return { ...doc, similarityScore: score };
    });
    
    // Sort by similarity score and return all documents with score > 0, or top 10 if all have scores
    const sortedDocs = scoredDocs.sort((a, b) => b.similarityScore - a.similarityScore);
    
    // Return documents with similarity score > 0, or top 10, whichever is smaller
    const relevantDocs = sortedDocs.filter(doc => doc.similarityScore > 0);
    const maxDocs = Math.min(relevantDocs.length, 10);
    
    return relevantDocs.slice(0, maxDocs);
  };

  const getSimilarityScoreColor = (score: number) => {
    if (score >= 8) return 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900 dark:text-green-200 dark:border-green-800';
    if (score >= 5) return 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900 dark:text-yellow-200 dark:border-yellow-800';
    return 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-700';
  };

  const handleSaveChat = () => {
    setShowSaveModal(true);
  };

  const autoSaveChat = async (sessionName?: string, messagesToSave?: Message[]) => {
    const messagesToUse = messagesToSave;
    
    if (!autoSaveEnabled || !messagesToUse) {
      return;
    }
    
    const conversationMessages = filterConversationMessages(messagesToUse);
    
    // Debug: Check if messages have sources
    const messagesWithSources = conversationMessages.filter(m => m.sources && m.sources.length > 0);
    console.log('Auto-saving chat with', messagesWithSources.length, 'messages that have sources');
    messagesWithSources.forEach((msg, i) => {
      console.log(`Message ${i} sources:`, msg.sources?.map(s => s.title));
    });
    
    const userMessages = conversationMessages.filter(m => m.role === 'user');
    if (userMessages.length === 0) {
      return;
    }
    
    try {
      const displayName = sessionName || currentSessionName || 'Legal Inquiry';
      
      if (currentChatId) {
        try {
          await apiService.deleteSavedChat(currentChatId);
        } catch (error) {
        }
      }
      
      const response = await apiService.saveChat(displayName, conversationMessages);
      console.log("here");
      
      if (response.success) {
        setCurrentChatId(response.filename);
        
        toast({
          title: "Chat Auto-Saved",
          description: `Chat "${displayName}" has been automatically saved.`,
        });
      } else {
        toast({
          title: "Auto-Save Failed",
          description: response.error || "Failed to auto-save chat",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Auto-save failed:', error);
    }
  };

  const handleUploadComplete = async () => {
    setShowUploadModal(false);
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
    console.log('Loading chat data:', chatData);
    
    try {
      const loadedMessages: Message[] = [
        {
          role: "assistant",
          content: "Hi! I'm your Wisconsin Statutes RAG assistant. Ask me questions about legal documents and I'll cite the most relevant sources from your knowledge base.",
        }
      ];

      if (chatData.history && Array.isArray(chatData.history)) {
        chatData.history.forEach((exchange: any) => {
          // Add user message
          loadedMessages.push({
            role: "user",
            content: exchange.question || "Unknown question",
          });

          // Add assistant message
          const assistantMessage: Message = {
            role: "assistant",
            content: formatTextWithBullets(exchange.answer || "No answer available"),
          };

          // Handle sources - try new format first, then legacy
          if (exchange.sources && Array.isArray(exchange.sources)) {
            assistantMessage.sources = exchange.sources;
          } else if (exchange.metadata?.source_documents && Array.isArray(exchange.metadata.source_documents)) {
            assistantMessage.sources = exchange.metadata.source_documents;
          }

          // Add metadata if available
          if (exchange.metadata) {
            assistantMessage.metadata = {
              confidence_score: exchange.metadata.confidence_score,
              safety_warnings: exchange.metadata.safety_warnings,
            };
          }

          loadedMessages.push(assistantMessage);
        });
      }

      console.log('Loaded messages:', loadedMessages);
      setMessages(loadedMessages);
      setCurrentSessionName(chatData.chat_name || chatData.session_name);
      
      // Set current sources from the latest assistant message
      const lastAssistantMessage = loadedMessages.filter(m => m.role === 'assistant').pop();
      if (lastAssistantMessage && lastAssistantMessage.sources && lastAssistantMessage.sources.length > 0) {
        setCurrentSources(lastAssistantMessage.sources);
        console.log('Loaded sources for context panel:', lastAssistantMessage.sources.length, 'sources');
      } else {
        setCurrentSources([]);
      }
      
      setShowHistoryPanel(false);
      
      toast({
        title: "Chat Loaded",
        description: `Successfully loaded "${chatData.chat_name || chatData.session_name}" with ${chatData.history?.length || 0} exchanges.`,
      });
      
    } catch (error) {
      console.error('Error loading chat:', error);
      toast({
        title: "Load Failed",
        description: "Failed to load chat session. Please try again.",
        variant: "destructive",
      });
    }
  };

  const isValidDownloadableFile = (filename: string | undefined): boolean => {
    if (!filename) return false;
    
    const hasValidExtension = /\.(pdf|doc|docx|txt|html|md)$/i.test(filename);
    
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

  return (
    <div className="mx-auto w-full max-w-6xl px-4 md:px-6 py-4 md:py-6 h-full flex flex-col">
      <header className="mb-4 md:mb-6 lg:mb-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-xl md:text-2xl">Wisconsin Legal Chatbot</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Find your answers in the Wisconsin Statutes
              {autoSaveEnabled && (
                <span className="ml-2 inline-flex items-center gap-1 text-xs text-green-600">
                  <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
                  auto-saving
                </span>
              )}
            </p>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <StatusBadge 
              label={isConnected ? "Connected" : "Disconnected"} 
              variant={isConnected ? "success" : "destructive"} 
            />
            
            {}
            <div className="flex items-center gap-1">
              <Button 
                variant="outline" 
                size="sm"
                className="hover-scale px-2" 
                onClick={() => setShowHistoryPanel(!showHistoryPanel)}
                disabled={!isConnected}
                title="View chat history and saved conversations"
              >
                <History className="mr-1 h-4 w-4" /> Hist
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                className="hover-scale px-2" 
                onClick={() => setShowUploadModal(true)}
                disabled={!isConnected}
                title="Upload legal documents to the knowledge base"
              >
                <Upload className="mr-1 h-4 w-4" /> Up
                {documentCount > 0 && (
                  <span className="ml-1 px-1 py-0.5 text-xs bg-primary text-primary-foreground rounded-full">
                    {documentCount}
                  </span>
                )}
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                className={`hover-scale px-2 ${showCrossReferencePanel ? 'bg-blue-600 text-white' : ''}`}
                onClick={() => setShowCrossReferencePanel(!showCrossReferencePanel)}
                disabled={!isConnected || currentSources.length === 0}
                title="Find cross-references and related documents"
              >
                <Link className="mr-1 h-4 w-4" /> Ref
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                className={`hover-scale px-2 ${autoSaveEnabled ? 'bg-green-600' : ''}`}
                onClick={() => setAutoSaveEnabled(!autoSaveEnabled)}
                disabled={!isConnected}
                title={autoSaveEnabled ? "Auto-save enabled - conversations are saved automatically" : "Auto-save disabled - conversations must be saved manually"}
              >
                <Save className="mr-1 h-4 w-4" /> 
                {autoSaveEnabled ? "Auto" : "Man"}
              </Button>
              {!autoSaveEnabled && messages.filter(m => m.role === 'user').length > 0 && (
                <Button 
                  variant="outline" 
                  size="sm"
                  className="hover-scale px-2" 
                  onClick={handleSaveChat}
                  disabled={!isConnected}
                  title="Save current chat conversation"
                >
                  <Save className="h-4 w-4" />
                </Button>
              )}
              <Button 
                variant="outline" 
                size="sm"
                className="hover-scale px-2" 
                onClick={() => setShowExportModal(true)}
                disabled={!isConnected || messages.length <= 1}
                title="Export chat conversation as text file"
              >
                <Download className="mr-1 h-4 w-4" /> Exp
              </Button>
              <Button 
                variant="secondary" 
                size="sm" 
                className="hover-scale px-2" 
                onClick={clearChat}
                title="Start a new chat conversation"
              >
                <Plus className="mr-1 h-4 w-4" /> New
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className={`grid gap-4 md:gap-6 lg:gap-8 flex-1 ${
        showHistoryPanel
          ? 'grid-cols-1 lg:grid-cols-[300px_1fr] xl:grid-cols-[320px_1fr]'
          : 'grid-cols-1 md:grid-cols-[1fr_250px] lg:grid-cols-[1fr_300px] xl:grid-cols-[1fr_320px]'
      }`}>
        {}
        {showHistoryPanel && (
          <aside aria-label="Chat History" className="rounded-xl border bg-card p-0">
            <ConversationHistory 
              onLoadChat={handleLoadChat}
              currentSessionName={currentSessionName}
              open={showHistoryPanel}
            />
          </aside>
        )}

        <section aria-label="Conversation" className="rounded-xl border bg-card p-0 flex flex-col">
          <ScrollArea className="flex-1 px-4 md:px-6 py-6 md:py-8 min-h-[300px] md:min-h-[400px] max-h-[60vh] md:max-h-[70vh]">
            <div className="flex flex-col gap-6">
              {messages.filter(m => m.content && m.content.trim()).map((m, i) => (
                <ChatMessage 
                  key={i} 
                  role={m.role} 
                  sources={m.role === 'assistant' ? currentSources.slice(0, 2) : undefined}
                  metadata={m.metadata}
                >
                  <div dangerouslySetInnerHTML={{ __html: m.content.replace(/\n/g, '<br/>') }} />
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
          <div className="border-t p-2 md:p-3">
            <ChatInput 
              onSend={onSend} 
              onStop={stopGeneration}
              disabled={loading || !isConnected} 
              isGenerating={loading}
            />
          </div>
        </section>

        <aside aria-label="Sidebar" className="space-y-4 md:space-y-6">
          {}
          <div className="rounded-xl border bg-card p-4 md:p-6">
            <QuickQueries onQuerySelect={handleQuickQuery} disabled={loading || !isConnected} />
          </div>

          {}
          <div className="rounded-xl border bg-card p-4 md:p-6">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-primary"></div>
                <h2 className="text-sm font-semibold">Context Sources</h2>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded-full">
                  {currentSources.length} sources
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setContextSourcesExpanded(!contextSourcesExpanded)}
                  className="h-6 w-6 p-0"
                >
                  {contextSourcesExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                </Button>
              </div>
            </div>
            
            {contextSourcesExpanded && (
              <>
                {currentSources.length > 0 ? (
                  <div className="space-y-2">
                    {currentSources.map((s, i) => (
                      <SourceCard 
                        key={i} 
                        {...s} 
                        onCrossReference={() => handleCrossReference(s)}
                        showCrossReferenceButton={true}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-6 text-muted-foreground">
                    <FileText className="h-6 w-6 mx-auto mb-2 opacity-50" />
                    <p className="text-xs">No sources yet</p>
                    <p className="text-xs">Ask a question to see relevant documents</p>
                  </div>
                )}
                
                <Separator className="my-3" />
                <div className="text-xs text-muted-foreground leading-relaxed">
                  Documents are semantically indexed and ranked by relevance to your query. 
                  Each source shows the most relevant sections from your knowledge base.
                </div>
              </>
            )}
          </div>

          {}
          {showCrossReferencePanel && selectedDocument && (
            <div className="rounded-xl border bg-card p-4 md:p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-blue-500"></div>
                  <h2 className="text-sm font-semibold">Cross-References</h2>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded-full">
                    {crossReferenceResults.length} similar
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setCrossReferencesExpanded(!crossReferencesExpanded)}
                    className="h-6 w-6 p-0"
                  >
                    {crossReferencesExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowCrossReferencePanel(false)}
                    className="h-6 w-6 p-0"
                    title="Close cross-references"
                  >
                    <Plus className="h-3 w-3 rotate-45" />
                  </Button>
                </div>
              </div>
              
              {crossReferencesExpanded && (
                <>
                  <div className="mb-4 p-3 bg-muted/50 rounded-lg border">
                    <p className="text-xs text-muted-foreground mb-2 font-medium">Similar to:</p>
                    <div className="text-xs">
                      <strong className="text-foreground">{selectedDocument.title}</strong>
                      <br />
                      <span className="text-muted-foreground">{selectedDocument.section}</span>
                    </div>
                  </div>
                  
                  {crossReferenceResults.length > 0 ? (
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {crossReferenceResults.map((doc, i) => (
                        <div key={i} className="group relative rounded-lg border border-border/50 bg-card/50 hover:bg-card/80 hover:border-border transition-all duration-200 p-4">
                          {/* Header with title and score */}
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex-1 min-w-0">
                              <h4 className="font-semibold text-sm text-foreground leading-tight line-clamp-2 group-hover:text-primary transition-colors">
                                {doc.title}
                              </h4>
                            </div>
                            <div className="flex items-center gap-2 ml-3 flex-shrink-0">
                              <div className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${getSimilarityScoreColor(doc.similarityScore)}`}>
                                {doc.similarityScore} pts
                              </div>
                              <span className="text-xs text-muted-foreground/60 bg-muted/50 px-2 py-1 rounded-md font-mono">
                                #{i + 1}
                              </span>
                            </div>
                          </div>

                          {/* Content preview */}
                          {doc.content_preview && (
                            <p className="text-xs text-muted-foreground/80 leading-relaxed mb-3 line-clamp-2">
                              {doc.content_preview}
                            </p>
                          )}

                          {/* Metadata row */}
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <span className="text-xs bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300 px-2 py-1 rounded-md font-medium">
                                {doc.type?.replace(/_/g, ' ')}
                              </span>
                              <span className="text-xs bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 px-2 py-1 rounded-md font-medium">
                                {doc.jurisdiction}
                              </span>
                              {doc.citations && doc.citations.length > 0 && (
                                <span className="text-xs bg-purple-50 text-purple-700 dark:bg-purple-950 dark:text-purple-300 px-2 py-1 rounded-md font-medium">
                                  {doc.citations.length} citations
                                </span>
                              )}
                            </div>
                            
                            {/* Download button */}
                            {doc.filename && isValidDownloadableFile(doc.filename) && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={async () => {
                                  try {
                                    if (doc.filename && isValidDownloadableFile(doc.filename)) {
                                      await apiService.downloadDocument(doc.filename);
                                      toast({
                                        title: "Download Started",
                                        description: `Downloading ${doc.filename}`,
                                      });
                                    } else {
                                      toast({
                                        title: "Download Error",
                                        description: "File not downloadable or invalid filename.",
                                        variant: "destructive",
                                      });
                                    }
                                  } catch (error) {
                                    console.error('Cross-reference download error:', error);
                                    toast({
                                      title: "Download Failed",
                                      description: error instanceof Error ? error.message : "Failed to download document",
                                      variant: "destructive",
                                    });
                                  }
                                }}
                                className="h-7 w-7 p-0 opacity-0 group-hover:opacity-100 transition-all duration-200 hover:bg-primary/10"
                                title="Download document"
                              >
                                <Download className="h-3.5 w-3.5" />
                              </Button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      <Link className="h-8 w-8 mx-auto mb-3 opacity-50" />
                      <p className="text-sm font-medium">No similar documents found</p>
                      <p className="text-xs">Try selecting a different document</p>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </aside>
      </div>

      {}
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

      {}
      <ExportModal 
        open={showExportModal} 
        onOpenChange={setShowExportModal} 
      />

      {}
      <SaveModal 
        open={showSaveModal} 
        onOpenChange={setShowSaveModal}
        messages={filterConversationMessages(messages)}
        onSaveSuccess={(sessionName) => setCurrentSessionName(sessionName)}
      />
    </div>
  );
};
