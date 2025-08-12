import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { SourceCard } from "./SourceCard";
import { StatusBadge } from "./StatusBadge";
import { Plus } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const demoSources = [
  {
    title: "RAG Best Practices – OpenAI Cookbook",
    url: "https://cookbook.openai.com/",
    score: 0.92,
    type: "web" as const,
  },
  {
    title: "Vector DB Indexing Strategies (PDF)",
    url: "#",
    score: 0.86,
    type: "pdf" as const,
  },
  {
    title: "Internal Knowledge: onboarding.md",
    url: "#",
    score: 0.81,
    type: "doc" as const,
  },
];

export const ChatLayout = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi! I’m your RAG assistant. Ask me questions and I’ll cite the most relevant sources from your knowledge base.",
    },
  ]);
  const [loading, setLoading] = useState(false);

  const onSend = (text: string) => {
    setMessages((m) => [...m, { role: "user", content: text }]);
    setLoading(true);
    setTimeout(() => {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content:
            "Here’s a concise answer based on your documents. I’ve included citations to the most relevant sources.",
        },
      ]);
      setLoading(false);
    }, 900);
  };

  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-10">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl">Wisconsin Statutes Chatbot</h1>
          <p className="mt-1 text-sm text-muted-foreground">Find your answers in the Wisconsin Statutes</p>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge label="Connected" variant="success" />
          <Button variant="secondary" className="hover-scale">
            <Plus className="mr-2 h-4 w-4" onClick={() => setMessages([])}/> New Chat
          </Button>
        </div>
      </header>

      <div className="grid gap-6 md:grid-cols-[1fr_320px]">
        <section aria-label="Conversation" className="rounded-xl border bg-card p-0">
          <ScrollArea className="h-[56vh] px-4 py-4">
            <div className="flex flex-col gap-4">
              {messages.map((m, i) => (
                <ChatMessage key={i} role={m.role} sources={m.role === 'assistant' ? demoSources.slice(0,2) : undefined}>
                  <p>{m.content}</p>
                  {m.role === 'assistant' && (
                    <pre className="mt-3 overflow-x-auto rounded-md border border-border bg-background p-3 text-xs">
{`// Example pseudo-code
const query = embed(userQuestion)
const hits = vectorDB.search(query, { topK: 5 })
return synthesize(hits)`}
                    </pre>
                  )}
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
            <ChatInput onSend={onSend} />
          </div>
        </section>

        <aside aria-label="Sources" className="rounded-xl border bg-card p-4">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm">Context Sources</h2>
            <span className="text-xs text-muted-foreground">Top matches</span>
          </div>
          <div className="space-y-3">
            {demoSources.map((s, i) => (
              <SourceCard key={i} {...s} />
            ))}
          </div>
          <Separator className="my-4" />
          <div className="text-xs text-muted-foreground">
            Documents are chunked and ranked by semantic relevance. Citations appear with each answer.
          </div>
        </aside>
      </div>
    </div>
  );
};
