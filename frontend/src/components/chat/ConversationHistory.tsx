import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { MessageSquare, Clock, Trash2, Loader2 } from "lucide-react";
import { apiService } from "@/lib/api";

const API_BASE_URL = 'http://localhost:5001/api';
import { useToast } from "@/hooks/use-toast";

interface SavedChat {
  session_name: string;
  created_at: string;
  total_exchanges: number;
  filename: string;
}

interface ConversationHistoryProps {
  onLoadChat: (chatData: any) => void;
  currentSessionName?: string;
  open?: boolean;
}

export const ConversationHistory = ({ onLoadChat, currentSessionName, open }: ConversationHistoryProps) => {
  const { toast } = useToast();
  const [savedChats, setSavedChats] = useState<SavedChat[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingChat, setLoadingChat] = useState<string | null>(null);

  const loadSavedChats = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/chat/list-saved`);
      console.log('Response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Saved chats data:', data);
        
        if (data.status === 'success' && data.data && data.data.chats) {
          setSavedChats(data.data.chats);
        } else {
          console.error('Unexpected response format:', data);
          setSavedChats([]);
        }
      } else {
        console.error('Failed to load saved chats:', response.status, response.statusText);
        setSavedChats([]);
      }
    } catch (error) {
      console.error('Error loading saved chats:', error);
      setSavedChats([]);
    } finally {
      setLoading(false);
    }
  };

  const loadChat = async (filename: string) => {
    setLoadingChat(filename);
    try {
      const response = await fetch(`${API_BASE_URL}/chat/load/${encodeURIComponent(filename)}`);
      if (response.ok) {
        const chatData = await response.json();
        onLoadChat(chatData);
        toast({
          title: "Chat Loaded",
          description: `Loaded chat session: ${chatData.session_name}`,
        });
      } else {
        throw new Error('Failed to load chat');
      }
    } catch (error) {
      console.error('Error loading chat:', error);
      toast({
        title: "Load Failed",
        description: "Failed to load chat session. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoadingChat(null);
    }
  };

  const deleteChat = async (filename: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/delete/${encodeURIComponent(filename)}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        setSavedChats(prev => prev.filter(chat => chat.filename !== filename));
        toast({
          title: "Chat Deleted",
          description: "Chat session deleted successfully.",
        });
      } else {
        throw new Error('Failed to delete chat');
      }
    } catch (error) {
      console.error('Error deleting chat:', error);
      toast({
        title: "Delete Failed",
        description: "Failed to delete chat session. Please try again.",
        variant: "destructive",
      });
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  useEffect(() => {
    loadSavedChats();
  }, []);

  // Refresh when component becomes visible
  useEffect(() => {
    if (open !== undefined) {
      loadSavedChats();
    }
  }, [open]);

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between p-4 border-b">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <MessageSquare className="h-5 w-5" />
          Chat History
        </h2>
        <Button
          variant="ghost"
          size="sm"
          onClick={loadSavedChats}
          disabled={loading}
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Refresh"}
        </Button>
      </div>

      <ScrollArea className="flex-1 p-4">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span className="ml-2">Loading chats...</span>
          </div>
        ) : savedChats.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <MessageSquare className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>No saved chats yet</p>
            <p className="text-sm">Save a chat to see it here</p>
          </div>
        ) : (
          <div className="space-y-2">
            {savedChats.map((chat) => (
              <div
                key={chat.filename}
                className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                  currentSessionName === chat.session_name
                    ? 'bg-primary/10 border-primary'
                    : 'hover:bg-muted/50 border-border'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-sm truncate">
                      {chat.session_name}
                    </h3>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                      <Clock className="h-3 w-3" />
                      <span>{formatDate(chat.created_at)}</span>
                      <span>•</span>
                      <span>{chat.total_exchanges} exchanges</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 ml-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        loadChat(chat.filename);
                      }}
                      disabled={loadingChat === chat.filename}
                      className="h-6 w-6 p-0"
                    >
                      {loadingChat === chat.filename ? (
                        <Loader2 className="h-3 w-3 animate-spin" />
                      ) : (
                        <MessageSquare className="h-3 w-3" />
                      )}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteChat(chat.filename);
                      }}
                      className="h-6 w-6 p-0 text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  );
};
