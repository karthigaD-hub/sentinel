import { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useSearch } from '@tanstack/react-router';
import { Bot, Send, Loader2, MessageSquare, BookOpen } from 'lucide-react';
import { assistantApi } from '../api/assistantApi';
import { ragApi } from '../api/ragApi';
import { LoadingState, EmptyState, BackendOfflineState, LLMUnavailable } from '../components/StateComponents';
import { cn, formatRelativeTime } from '../utils/cn';
import type { Citation } from '../api/types';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
}

export function AIAssistantPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const search = useSearch({ strict: false }) as { q?: string };
  const pendingQuery = useRef<string | null>(null);
  const sentInitial = useRef(false);

  const historyQuery = useQuery({ queryKey: ['assistant', 'history'], queryFn: assistantApi.history });
  const ragStatusQuery = useQuery({ queryKey: ['rag', 'status'], queryFn: ragApi.status });

  const chatMutation = useMutation({
    mutationFn: assistantApi.chat,
    onSuccess: (data) => {
      setConversationId(data.conversation_id);
      setMessages((prev) => [...prev, { role: 'assistant', content: data.answer, citations: data.citations }]);
    },
    onError: (err: unknown) => {
      const message = (err as { message?: string })?.message || 'Failed to get response';
      setMessages((prev) => [...prev, { role: 'assistant', content: `Error: ${message}`, citations: [] }]);
    },
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = (text: string) => {
    if (!text.trim()) return;
    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    chatMutation.mutate({ conversation_id: conversationId || undefined, message: text });
  };

  useEffect(() => {
    if (sentInitial.current) return;
    if (search.q && search.q.trim()) {
      sentInitial.current = true;
      pendingQuery.current = search.q.trim();
      sendMessage(search.q.trim());
    }
  }, [search.q]);

  if (historyQuery.isError && (historyQuery.error as { type?: string })?.type === 'network') {
    return <BackendOfflineState />;
  }

  const ragAvailable = ragStatusQuery.data?.available ?? false;

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || chatMutation.isPending) return;
    const userMessage = input.trim();
    setInput('');
    sendMessage(userMessage);
  };

  const isLLMUnavailable = messages.some((m) => m.role === 'assistant' && m.content.includes('LLM provider is not configured'));

  if (isLLMUnavailable && messages.length > 0 && !ragAvailable) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="font-display text-2xl font-bold text-navy-50">AI Security Assistant</h1>
          <p className="text-sm text-navy-400">RAG-powered cybersecurity question answering</p>
        </div>
        <LLMUnavailable />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold text-navy-50">AI Security Assistant</h1>
        <p className="text-sm text-navy-400">RAG-powered cybersecurity question answering</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-4">
        <div className="glass-panel p-5 lg:col-span-1">
          <h3 className="mb-3 font-display text-sm font-semibold text-navy-100">Conversation History</h3>
          {historyQuery.isLoading ? (
            <LoadingState title="Loading..." />
          ) : historyQuery.data && historyQuery.data.length > 0 ? (
            <div className="space-y-2">
              {historyQuery.data.map((conv) => (
                <div key={conv.id} className="glass-card p-3">
                  <div className="flex items-center gap-2">
                    <MessageSquare className="h-3.5 w-3.5 text-navy-400" />
                    <span className="truncate text-sm text-navy-100">{conv.title}</span>
                  </div>
                  <p className="mt-1 text-xs text-navy-400">{formatRelativeTime(conv.created_at)}</p>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState title="No conversations" message="Start asking questions to build history." />
          )}
        </div>

        <div className="glass-panel flex flex-col lg:col-span-3" style={{ minHeight: '500px' }}>
          <div className="flex-1 overflow-y-auto p-5">
            {messages.length === 0 ? (
              <EmptyState title="Ask a question" message="Ask about detected attacks, MITRE techniques, CVEs, OWASP guidance, or defensive actions." />
            ) : (
              <div className="space-y-4">
                {messages.map((msg, i) => (
                  <div key={i} className={cn('flex', msg.role === 'user' ? 'justify-end' : 'justify-start')}>
                    <div className={cn('max-w-[80%] rounded-lg p-4', msg.role === 'user' ? 'bg-cyber-600/20 border border-cyber-500/30' : 'glass-card')}>
                      <div className="flex items-center gap-2 mb-1">
                        {msg.role === 'assistant' && <Bot className="h-4 w-4 text-cyber-400" />}
                        <span className="text-xs font-medium text-navy-400">{msg.role === 'user' ? 'You' : 'Q-Sentinel AI'}</span>
                      </div>
                      <p className="text-sm text-navy-100 whitespace-pre-wrap">{msg.content}</p>
                      {msg.citations && msg.citations.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-navy-700/50">
                          <div className="flex items-center gap-1.5 mb-2">
                            <BookOpen className="h-3.5 w-3.5 text-navy-400" />
                            <span className="text-xs font-medium text-navy-400">Supporting Sources</span>
                          </div>
                          <div className="space-y-1">
                            {msg.citations.map((cite, j) => (
                              <div key={j} className="flex items-center gap-2 text-xs">
                                <span className="badge border-cyber-500/30 bg-cyber-500/10 text-cyber-400">{cite.source}</span>
                                <span className="font-mono text-navy-400">{cite.external_id}</span>
                                <span className="font-mono text-navy-400">Score: {(cite.score * 100).toFixed(1)}%</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {chatMutation.isPending && (
                  <div className="flex justify-start">
                    <div className="glass-card p-4">
                      <Loader2 className="h-4 w-4 animate-spin text-cyber-400" />
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          <form onSubmit={handleSend} className="border-t border-navy-700/60 p-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about threats, MITRE techniques, CVEs..."
                className="input-field"
                disabled={chatMutation.isPending}
              />
              <button type="submit" disabled={!input.trim() || chatMutation.isPending} className="btn-primary flex items-center gap-2">
                {chatMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                Send
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
