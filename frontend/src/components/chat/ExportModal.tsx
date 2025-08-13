import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Download, FileText, FileJson, File } from "lucide-react";
import { apiService } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface ExportModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const ExportModal = ({ open, onOpenChange }: ExportModalProps) => {
  const { toast } = useToast();
  const [format, setFormat] = useState<'txt' | 'json' | 'pdf'>('txt');
  const [includeSources, setIncludeSources] = useState(true);
  const [exporting, setExporting] = useState(false);

  const handleExport = async () => {
    setExporting(true);
    try {
      const result = await apiService.exportChat(format, includeSources);
      
      if (format === 'txt' || format === 'json') {
        // Create and download file
        const blob = new Blob([result.data.content || JSON.stringify(result.data, null, 2)], {
          type: format === 'txt' ? 'text/plain' : 'application/json'
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = result.data.filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } else {
        // For PDF, show content in new window for printing
        const newWindow = window.open('', '_blank');
        if (newWindow) {
          newWindow.document.write(`
            <html>
              <head>
                <title>Chat Report</title>
                <style>
                  body { font-family: Arial, sans-serif; margin: 20px; }
                  pre { white-space: pre-wrap; }
                </style>
              </head>
              <body>
                <pre>${result.data.content}</pre>
              </body>
            </html>
          `);
          newWindow.document.close();
        }
      }

      toast({
        title: "Export Successful",
        description: `Chat exported as ${format.toUpperCase()}`,
      });
      
      onOpenChange(false);
    } catch (error) {
      console.error('Export error:', error);
      toast({
        title: "Export Failed",
        description: "Failed to export chat. Please try again.",
        variant: "destructive",
      });
    } finally {
      setExporting(false);
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-background rounded-lg p-6 w-full max-w-md mx-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Export Chat Report</h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onOpenChange(false)}
            className="h-8 w-8 p-0"
          >
            ×
          </Button>
        </div>
        
        <div className="space-y-6">
          {/* Format Selection */}
          <div className="space-y-3">
            <label className="text-sm font-medium">Export Format</label>
            <div className="space-y-2">
              {[
                { value: 'txt', label: 'Text File (.txt)', icon: FileText, description: 'Simple text format' },
                { value: 'json', label: 'JSON File (.json)', icon: FileJson, description: 'Structured data format' },
                { value: 'pdf', label: 'PDF Report', icon: File, description: 'Formatted report for printing' }
              ].map((option) => {
                const IconComponent = option.icon;
                return (
                  <div key={option.value} className="flex items-center space-x-2">
                    <input
                      type="radio"
                      id={option.value}
                      name="format"
                      value={option.value}
                      checked={format === option.value}
                      onChange={(e) => setFormat(e.target.value as any)}
                      className="h-4 w-4"
                    />
                    <label htmlFor={option.value} className="flex items-center gap-2 cursor-pointer">
                      <IconComponent className="h-4 w-4" />
                      <div>
                        <div className="font-medium text-sm">{option.label}</div>
                        <div className="text-xs text-muted-foreground">{option.description}</div>
                      </div>
                    </label>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Options */}
          <div className="space-y-3">
            <label className="text-sm font-medium">Options</label>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="include-sources"
                checked={includeSources}
                onChange={(e) => setIncludeSources(e.target.checked)}
                className="h-4 w-4"
              />
              <label htmlFor="include-sources" className="text-sm">
                Include source documents and citations
              </label>
            </div>
          </div>

          {/* Export Button */}
          <Button
            onClick={handleExport}
            disabled={exporting}
            className="w-full"
          >
            <Download className="mr-2 h-4 w-4" />
            {exporting ? 'Exporting...' : 'Export Report'}
          </Button>
        </div>
      </div>
    </div>
  );
};
