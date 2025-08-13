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

// Helper function to format text with bullet points
const formatTextWithBullets = (text: string): string => {
  // Convert **xxx** patterns to bullet points
  return text.replace(/\*\*([^*]+)\*\*/g, '• $1');
};

// Helper function to generate intelligent chat names
const generateChatName = (messages: Message[]): string => {
  if (messages.length <= 1) return 'New Chat';

  const userMessages = messages.filter(m => m.role === 'user').slice(0, 3); // Take first 3 questions
  const questions = userMessages.map(m => m.content.toLowerCase());
  
  const legalKeywords = [
    { keyword: 'miranda rights', weight: 10 },
    { keyword: 'use of force', weight: 10 },
    { keyword: 'probable cause', weight: 9 },
    { keyword: 'search warrant', weight: 9 },
    { keyword: 'domestic violence', weight: 8 },
    { keyword: 'traffic stop', weight: 8 },
    { keyword: 'excessive force', weight: 8 },
    { keyword: 'reasonable suspicion', weight: 7 },
    { keyword: 'evidence admissibility', weight: 7 },
    { keyword: 'juvenile law', weight: 7 },
    
    // Medium priority - general legal terms
    { keyword: 'arrest', weight: 6 },
    { keyword: 'assault', weight: 6 },
    { keyword: 'theft', weight: 6 },
    { keyword: 'burglary', weight: 6 },
    { keyword: 'dui', weight: 6 },
    { keyword: 'drug possession', weight: 6 },
    { keyword: 'weapon', weight: 6 },
    { keyword: 'firearm', weight: 6 },
    { keyword: 'statutes', weight: 5 },
    { keyword: 'laws', weight: 5 },
    { keyword: 'procedures', weight: 5 },
    { keyword: 'training', weight: 5 },
    { keyword: 'policy', weight: 5 },
    { keyword: 'jurisdiction', weight: 5 },
    
    // Low priority - locations and general terms
    { keyword: 'wisconsin', weight: 4 },
    { keyword: 'madison', weight: 4 },
    { keyword: 'milwaukee', weight: 4 },
    { keyword: 'dane county', weight: 4 },
    { keyword: 'property tax', weight: 4 },
    { keyword: 'boundaries', weight: 3 },
    { keyword: 'citations', weight: 3 },
    { keyword: 'county', weight: 3 }
  ];
  
  // Find keywords in questions with weights
  const foundKeywords: { keyword: string; weight: number }[] = [];
  questions.forEach(question => {
    legalKeywords.forEach(({ keyword, weight }) => {
      if (question.includes(keyword) && !foundKeywords.some(fk => fk.keyword === keyword)) {
        foundKeywords.push({ keyword, weight });
      }
    });
  });
  
  // Sort by weight and take top keywords
  foundKeywords.sort((a, b) => b.weight - a.weight);
  const topKeywords = foundKeywords.slice(0, 3);
  
  // Generate name based on found keywords
  if (topKeywords.length > 0) {
    const keywords = topKeywords.map(k => k.keyword.split(' ').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' '));
    return keywords.join(' ');
  }
  
  // Fallback: extract meaningful words from first question
  if (questions.length > 0) {
    const firstQuestion = questions[0];
    // Remove common words and extract meaningful terms
    const commonWords = ['what', 'how', 'when', 'where', 'why', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall'];
    const words = firstQuestion.split(' ')
      .filter(word => word.length > 3 && !commonWords.includes(word.toLowerCase()))
      .slice(0, 3);
    
    if (words.length >= 2) {
      return words.map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
    }
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

  // Check connection and load document count on mount
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
          // Load document count with timeout
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
            // Don't show error toast for document count, just log it
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

    // Cleanup abort controller on unmount
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

    // Validate input
    if (!text.trim()) {
      toast({
        title: "Empty Message",
        description: "Please enter a question to ask",
        variant: "destructive",
      });
      return;
    }

    // Create new abort controller for this request
    const controller = new AbortController();
    setAbortController(controller);

    setMessages((m) => [...m, { role: "user", content: text }]);
    setLoading(true);
    
          // Auto-save the chat after adding user message
      if (autoSaveEnabled) {
        setTimeout(() => autoSaveChat(), 100); // Small delay to ensure message is added
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
          
          // Auto-save after assistant responds
          if (autoSaveEnabled) {
            setTimeout(() => autoSaveChat(), 500); // Delay to ensure all data is processed
          }

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
              filename: doc.original_file_name || doc.file_name, // Add filename for download
            }));
            setCurrentSources(responseSources);
          }
          setLoading(false);
          setAbortController(null); // Clean up abort controller
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
          setAbortController(null); // Clean up abort controller
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
      setAbortController(null); // Clean up abort controller
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
    setCurrentChatId(undefined); // Reset chat ID to start fresh
    
    // Auto-save the cleared chat state
    if (autoSaveEnabled) {
      setTimeout(() => autoSaveChat('New Chat'), 100);
    }
  };

  const handleQuickQuery = (question: string) => {
    onSend(question);
  };

  const handleSaveChat = () => {
    setShowSaveModal(true);
  };

  const autoSaveChat = async (sessionName?: string) => {
    if (!autoSaveEnabled || messages.length <= 1) return;
    
    try {
      // Generate intelligent name if no session name provided
      let displayName = sessionName;
      if (!displayName) {
        if (currentSessionName && !currentSessionName.startsWith('Auto_Save_')) {
          // Keep existing intelligent name
          displayName = currentSessionName;
        } else {
          // Generate new intelligent name
          displayName = generateChatName(messages);
        }
      }
      
      // If we have a current chat ID, we're updating an existing chat
      // If not, we're creating a new chat
      const isUpdating = !!currentChatId;
      
      if (isUpdating) {
        // Update existing chat - delete the old one and create new with same name
        try {
          // Get the list of saved chats to find the current one
          const savedChats = await apiService.listSavedChats();
          const currentChat = savedChats.find(chat => chat.filename === currentChatId);
          
          if (currentChat) {
            // Delete the old chat file
            await apiService.deleteSavedChat(currentChatId);
          }
        } catch (error) {
          console.error('Error deleting old chat:', error);
        }
      }
      
      // Save the chat (this will create a new file)
      const response = await apiService.saveChat(displayName);
      
      if (response.success) {
        // Update current session name and chat ID
        setCurrentSessionName(displayName);
        setCurrentChatId(response.filename); // Store the new filename as current chat ID
        
        console.log('Auto-saved chat:', displayName, 'as', response.filename, isUpdating ? '(updated)' : '(new)');
      }
    } catch (error) {
      console.error('Auto-save failed:', error);
    }
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
    console.log('Loading chat data:', chatData);
    
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

        // Add assistant message with proper metadata
        const assistantMessage: Message = {
          role: "assistant",
          content: formatTextWithBullets(exchange.answer || "No answer available"),
        };

        // Try to extract sources from context if available
        if (exchange.context) {
          // Parse context to extract source information
          const contextLines = exchange.context.split('\n');
          const sources: any[] = [];
          let currentSource: any = {};
          
          contextLines.forEach((line: string) => {
            if (line.startsWith('Source ')) {
              if (currentSource.id) {
                sources.push(currentSource);
              }
              
              // Extract source number and relevance score
              const sourceMatch = line.match(/Source (\d+) \(Relevance: ([\d.]+)\)/);
              const sourceNumber = sourceMatch ? parseInt(sourceMatch[1]) : 1;
              const relevanceScore = sourceMatch ? parseFloat(sourceMatch[2]) : 0.8;
              
              currentSource = {
                id: sourceNumber.toString(),
                title: 'Unknown Document',
                content_preview: '',
                score: relevanceScore,
                type: 'document',
                jurisdiction: 'unknown',
                status: 'current',
                section: 'General',
                citations: [],
                url: '#',
                source_number: sourceNumber
              };
            } else if (line.includes('Document Type:')) {
              currentSource.type = line.split(':')[1]?.trim() || 'document';
            } else if (line.includes('Jurisdiction:')) {
              currentSource.jurisdiction = line.split(':')[1]?.trim() || 'unknown';
            } else if (line.includes('Content:')) {
              const content = line.split('Content:')[1]?.trim() || '';
              currentSource.content_preview = content.substring(0, 150) + (content.length > 150 ? '...' : '');
              
              // Try to extract a better title from the content
              if (content) {
                const lines = content.split('\n');
                for (const line of lines) {
                  const trimmedLine = line.trim();
                  if (trimmedLine && trimmedLine.length > 0 && trimmedLine.length < 100) {
                    // Look for meaningful titles (not just numbers or short text)
                    if (trimmedLine.match(/^[A-Z][A-Z\s\d\.]+$/) || // All caps titles
                        trimmedLine.match(/^[A-Z][a-z\s]+$/) || // Proper case titles
                        trimmedLine.includes('CHAPTER') ||
                        trimmedLine.includes('SECTION') ||
                        trimmedLine.includes('STATUTE') ||
                        trimmedLine.includes('SOVEREIGNTY') ||
                        trimmedLine.includes('JURISDICTION') ||
                        trimmedLine.includes('WISCONSIN STATUTES')) {
                      currentSource.title = trimmedLine;
                      break;
                    }
                  }
                }
                
                // If no good title found, try to extract from the first meaningful line
                if (currentSource.title === `Source ${currentSource.source_number}`) {
                  for (const line of lines) {
                    const trimmedLine = line.trim();
                    if (trimmedLine && trimmedLine.length > 5 && trimmedLine.length < 80) {
                      // Skip lines that are just numbers or very short
                      if (!trimmedLine.match(/^\d+$/) && !trimmedLine.match(/^[A-Z\s]+$/)) {
                        currentSource.title = trimmedLine;
                        break;
                      }
                    }
                  }
                }
              }
            } else if (line.includes('Citations:')) {
              const citations = line.split('Citations:')[1]?.trim() || '';
              currentSource.citations = citations.split(',').map(c => c.trim()).filter(c => c);
            }
          });
          
          if (currentSource.id) {
            sources.push(currentSource);
          }
          
          assistantMessage.sources = sources;
        }

        // Add metadata if available
        if (exchange.confidence_score !== undefined || exchange.safety_warnings) {
          assistantMessage.metadata = {
            confidence_score: exchange.confidence_score,
            safety_warnings: exchange.safety_warnings,
          };
        }

        loadedMessages.push(assistantMessage);
      });
    }

    console.log('Loaded messages:', loadedMessages);
    setMessages(loadedMessages);
    setCurrentSessionName(chatData.session_name);
    
    // Enable auto-save for loaded chats
    setAutoSaveEnabled(true);
    
    // Restore sources from the most recent exchange
    if (chatData.history && chatData.history.length > 0) {
      const lastExchange = chatData.history[chatData.history.length - 1];
      if (lastExchange.context) {
        // Parse context to extract source information for the right panel
        const contextLines = lastExchange.context.split('\n');
        const sources: any[] = [];
        let currentSource: any = {};
        
        contextLines.forEach((line: string) => {
          if (line.startsWith('Source ')) {
            if (currentSource.id) {
              sources.push(currentSource);
            }
            
            // Extract source number and relevance score
            const sourceMatch = line.match(/Source (\d+) \(Relevance: ([\d.]+)\)/);
            const sourceNumber = sourceMatch ? parseInt(sourceMatch[1]) : 1;
            const relevanceScore = sourceMatch ? parseFloat(sourceMatch[2]) : 0.8;
            
            currentSource = {
              id: sourceNumber.toString(),
              title: `Source ${sourceNumber}`,
              content_preview: '',
              score: relevanceScore,
              type: 'document',
              jurisdiction: 'unknown',
              status: 'current',
              section: 'General',
              citations: [],
              url: '#',
              source_number: sourceNumber
            };
          } else if (line.includes('Document Type:')) {
            currentSource.type = line.split(':')[1]?.trim() || 'document';
          } else if (line.includes('Jurisdiction:')) {
            currentSource.jurisdiction = line.split(':')[1]?.trim() || 'unknown';
          } else if (line.includes('Content:')) {
            const content = line.split('Content:')[1]?.trim() || '';
            currentSource.content_preview = content.substring(0, 150) + (content.length > 150 ? '...' : '');
          } else if (line.includes('Citations:')) {
            const citations = line.split('Citations:')[1]?.trim() || '';
            currentSource.citations = citations.split(',').map(c => c.trim()).filter(c => c);
          }
        });
        
        if (currentSource.id) {
          sources.push(currentSource);
        }
        
        setCurrentSources(sources);
        console.log('Restored sources:', sources);
      } else {
        setCurrentSources([]); // Clear sources if no context
      }
    } else {
      setCurrentSources([]); // Clear sources if no history
    }
    
    setShowHistoryPanel(false); // Close the history panel
    
    // Show success toast
    toast({
      title: "Chat Loaded",
      description: `Successfully loaded "${chatData.session_name}" with ${chatData.history?.length || 0} exchanges and ${chatData.history && chatData.history.length > 0 ? 'restored sources' : 'no sources'}. Auto-save enabled.`,
    });
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
            
            {/* Primary Actions */}
            <div className="flex items-center gap-1">
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
            </div>
            
            {/* Chat Management */}
            <div className="flex items-center gap-1">
              <Button 
                variant="outline" 
                size="sm"
                className={`hover-scale ${autoSaveEnabled ? 'bg-green-600' : ''}`}
                onClick={() => setAutoSaveEnabled(!autoSaveEnabled)}
                disabled={!isConnected}
                title={autoSaveEnabled ? "Auto-save enabled" : "Auto-save disabled"}
              >
                <Save className="mr-2 h-4 w-4" /> 
                {autoSaveEnabled ? "Auto-Save" : "Manual"}
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
        </div>
      </header>

      <div className={`grid gap-4 md:gap-6 lg:gap-8 flex-1 ${
        showHistoryPanel 
          ? 'grid-cols-1 lg:grid-cols-[300px_1fr_300px] xl:grid-cols-[320px_1fr_320px]'
          : 'grid-cols-1 md:grid-cols-[1fr_250px] lg:grid-cols-[1fr_300px] xl:grid-cols-[1fr_320px]'
      }`}>
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
          <div className="border-t p-4 md:p-6">
            <ChatInput 
              onSend={onSend} 
              onStop={stopGeneration}
              disabled={loading || !isConnected} 
              isGenerating={loading}
            />
          </div>
        </section>

        <aside aria-label="Sidebar" className="space-y-4 md:space-y-6">
          {/* Quick Queries */}
          <div className="rounded-xl border bg-card p-4 md:p-6">
            <QuickQueries onQuerySelect={handleQuickQuery} disabled={loading || !isConnected} />
          </div>

          {/* Context Sources */}
          <div className="rounded-xl border bg-card p-4 md:p-6">
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-primary"></div>
                <h2 className="text-sm font-semibold">Context Sources</h2>
              </div>
              <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded-full">
                {currentSources.length} sources
              </span>
            </div>
            
            {currentSources.length > 0 ? (
              <div className="space-y-2">
                {currentSources.map((s, i) => (
                  <SourceCard key={i} {...s} />
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
