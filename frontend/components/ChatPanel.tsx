"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { sendChatMessage } from "@/lib/api";
import type { ChatMessage } from "@/lib/types";

interface ChatPanelProps {
  docId: string;
  exampleQuestion?: string | null;
}

export default function ChatPanel({ docId, exampleQuestion }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const question = input.trim();
    if (!question || isSending) return;

    setError(null);
    setInput("");
    const history = messages;
    setMessages([...history, { role: "user", content: question }]);
    setIsSending(true);

    try {
      const answer = await sendChatMessage(docId, question, history);
      setMessages((prev) => [...prev, { role: "assistant", content: answer.answer }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    } finally {
      setIsSending(false);
    }
  };

  return (
    <section className="flex flex-col rounded-xl border border-slate-200 bg-white p-6">
      <h2 className="text-lg font-semibold text-slate-900">Ask a follow-up question</h2>

      <div className="mt-4 flex-1 space-y-3 overflow-y-auto">
        {messages.length === 0 && (
          <p className="text-sm text-slate-500">
            {exampleQuestion ? (
              <>
                Ask anything about this document — e.g.{" "}
                <button
                  type="button"
                  onClick={() => setInput(exampleQuestion)}
                  className="underline hover:text-blue-600"
                >
                  &ldquo;{exampleQuestion}&rdquo;
                </button>
              </>
            ) : (
              "Ask anything about this document."
            )}
          </p>
        )}
        {messages.map((message, index) => (
          <div
            key={index}
            className={`rounded-lg px-3 py-2 text-sm ${
              message.role === "user"
                ? "ml-auto max-w-[80%] bg-blue-600 text-white"
                : "mr-auto max-w-[80%] bg-slate-100 text-slate-800"
            }`}
          >
            {message.role === "assistant" ? (
              <div className="prose prose-sm max-w-none prose-p:my-1 prose-ul:my-1">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            ) : (
              message.content
            )}
          </div>
        ))}
        {isSending && <p className="text-sm text-slate-400">Thinking…</p>}
      </div>

      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}

      <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your question…"
          disabled={isSending}
          className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={isSending || !input.trim()}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </section>
  );
}
