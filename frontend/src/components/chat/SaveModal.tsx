import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Save, X } from "lucide-react";
import { apiService } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface SaveModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSaveSuccess?: (sessionName: string) => void;
  messages: any[];
}

export const SaveModal = ({ open, onOpenChange, onSaveSuccess, messages }: SaveModalProps) => {
  const { toast } = useToast();
  const [sessionName, setSessionName] = useState("");
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    if (!sessionName.trim()) {
      toast({
        title: "Name Required",
        description: "Please enter a name for your chat session.",
        variant: "destructive",
      });
      return;
    }

    setSaving(true);
    try {
      const result = await apiService.saveChat(sessionName, messages);
      
      toast({
        title: "Save Successful",
        description: `Chat session "${sessionName}" saved successfully!`,
      });
      
      setSessionName("");
      onOpenChange(false);
      onSaveSuccess?.(sessionName);
    } catch (error) {
      console.error('Save error:', error);
      toast({
        title: "Save Failed",
        description: "Failed to save chat session. Please try again.",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setSessionName("");
    onOpenChange(false);
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in">
      <div className="glass-panel rounded-lg p-6 w-full max-w-md mx-4 shadow-elegant animate-scale-in">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Save Chat Session</h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleCancel}
            className="h-8 w-8 p-0"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
        
        <div className="space-y-4">
          <div>
            <label htmlFor="session-name" className="block text-sm font-medium mb-2">
              Session Name
            </label>
            <input
              id="session-name"
              type="text"
              value={sessionName}
              onChange={(e) => setSessionName(e.target.value)}
              placeholder="Enter a name for this chat session..."
              className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleSave();
                } else if (e.key === 'Escape') {
                  handleCancel();
                }
              }}
              autoFocus
            />
          </div>

          <div className="flex gap-2 pt-2">
            <Button
              onClick={handleSave}
              disabled={saving || !sessionName.trim()}
              className="flex-1"
            >
              <Save className="mr-2 h-4 w-4" />
              {saving ? 'Saving...' : 'Save Session'}
            </Button>
            <Button
              variant="outline"
              onClick={handleCancel}
              disabled={saving}
            >
              Cancel
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
