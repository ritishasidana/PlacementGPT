// frontend/src/components/ChatWindow.jsx

import { useState, useRef, useEffect } from "react";
import { queryDocuments } from "../api/client";
import CitationCard from "./CitationCard";
import { Send, Bot, User, Loader2, AlertCircle } from "lucide-react";
import toast from "react-hot-toast";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
export default function ChatWindow({ activeFilters }) {
  // ── State ──────────────────────────────────────────────────────────────────
  const [messages,  setMessages]  = useState([]);
  const [input,     setInput]     = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showSlowMessage, setShowSlowMessage] = useState(false);
  // Auto-scroll to bottom ref
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ── Send Question ──────────────────────────────────────────────────────────
  const handleSend = async () => {
    const question = input.trim();
    if (!question || isLoading) return;

    // Add user message immediately
    const userMsg = { role: "user", content: question };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);
    const slowTimer = setTimeout(() => {
    setShowSlowMessage(true);
    }, 10000);

    try {
      const response = await queryDocuments(
        question,
        activeFilters.docTypes,   // e.g. ["dbms", "os"]
        activeFilters.company     // e.g. "amazon"
      );

      // Add assistant message with answer + citations
      const assistantMsg = {
        role:      "assistant",
        content:   response.answer,
        citations: response.citations,
        chunksRetrieved: response.chunks_retrieved
      };
      setMessages(prev => [...prev, assistantMsg]);

    } catch (error) {
      const errMsg = error.response?.data?.detail || "Something went wrong.";
      toast.error(errMsg);

      setMessages(prev => [...prev, {
        role:    "assistant",
        content: `Error: ${errMsg}`,
        isError: true
      }]);
    } finally {
      clearTimeout(slowTimer);
      setShowSlowMessage(false);
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    // Send on Enter, but allow Shift+Enter for new lines
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="relative flex flex-col h-full bg-[#020617] overflow-hidden">

  <div
    className="
    absolute
    top-10
    right-20
    w-[500px]
    h-[500px]
    rounded-full
    bg-blue-600/10
    blur-[150px]
    pointer-events-none
    "
  />

  <div
    className="
    absolute
    bottom-0
    left-20
    w-[400px]
    h-[400px]
    rounded-full
    bg-violet-600/10
    blur-[140px]
    pointer-events-none
    "
  />

      {/* ── Active Filters Banner ── */}
      {(activeFilters.docTypes?.length > 0 || activeFilters.company) && (
        <div className="flex flex-wrap gap-3 px-4 py-2 text-xs text-blue-300 border-b bg-blue-900/30 border-blue-800/50">
          <span className="font-medium">Active filters:</span>
          {activeFilters.docTypes?.map(dt => (
            <span key={dt} className="bg-blue-800/50 px-2 py-0.5 rounded-full">
              {dt.toUpperCase()}
            </span>
          ))}
          {activeFilters.company && (
            <span className="bg-purple-800/50 px-2 py-0.5 rounded-full text-purple-300">
              🏢 {activeFilters.company}
            </span>
          )}
        </div>
      )}

      {/* ── Messages Area ── */}
      <div className="relative z-10 flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Empty state */}
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full space-y-4 text-center">
            <div
                className="flex items-center justify-center w-24 h-24 border shadow-xl rounded-3xl bg-gradient-to-br from-blue-500/20 to-violet-500/20 border-blue-500/10 shadow-blue-900/20"
              >
              <Bot size={42} className="text-blue-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">PlacementGPT</h3>
              <p className="max-w-sm mt-1 text-sm text-gray-400">
                Ask me anything about your uploaded notes or interview experiences.
              </p>
            </div>
            {/* Quick prompts */}
            <div className="grid w-full max-w-md grid-cols-1 gap-2 mt-4">
              {[
                "Explain deadlock with all 4 conditions",
                "What DBMS questions were asked in Amazon?",
                "Difference between TCP and UDP",
                "Generate revision notes for OOP"
              ].map(prompt => (
                <button
                  key={prompt}
                  onClick={() => setInput(prompt)}
                  className="px-4 py-3 text-sm text-left transition-all duration-300 border rounded-2xl border-white/5 bg-gradient-to-br from-slate-900 to-slate-800 text-slate-300 hover:border-blue-500/20 hover:-translate-y-1 hover:shadow-lg hover:shadow-blue-900/20"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Message list */}
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>

            {/* Bot avatar */}
            {msg.role === "assistant" && (
              <div className="flex items-center justify-center flex-shrink-0 w-8 h-8 mt-1 bg-blue-600 rounded-lg">
                <Bot size={16} className="text-white" />
              </div>
            )}

            {/* Message bubble + citations */}
            <div
                className={`
                  px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap
                  ${
                    msg.role === "user"
                      ? `
                        bg-gradient-to-r
                        from-blue-600
                        to-violet-600
                        text-white
                        rounded-tr-sm
                        shadow-lg
                        shadow-blue-900/30
                      `
                      : msg.isError
                      ? "bg-red-900/40 text-red-300 border border-red-800"
                      : `
                        bg-gradient-to-br
                        from-slate-900
                        to-slate-800
                        text-slate-100
                        rounded-tl-sm
                        border
                        border-white/5
                        shadow-lg
                        shadow-black/20
                      `
                  }
                `}
              >
                {msg.role === "assistant" ? (
              <div className="markdown-content">
                  
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  h1: ({ children }) => (
                    <h1 className="mt-4 mb-2 text-3xl font-bold text-white">
                      {children}
                    </h1>
                  ),

                  h2: ({ children }) => (
                    <h2 className="mt-4 mb-2 text-2xl font-semibold text-blue-300">
                      {children}
                    </h2>
                  ),

                  h3: ({ children }) => (
                    <h3 className="mt-3 mb-2 text-xl font-bold text-blue-300">
                      {children}
                    </h3>
                  ),

                  ul: ({ children }) => (
                    <ul className="pl-5 space-y-1 list-disc">
                      {children}
                    </ul>
                  ),

                  li: ({ children }) => (
                    <li className="leading-6">
                      {children}
                    </li>
                  ),

                  ol: ({ children }) => (
                    <ol className="pl-5 space-y-1 list-decimal">
                      {children}
                    </ol>
                  ),

                  strong: ({ children }) => (
                    <strong className="font-semibold text-white">
                      {children}
                    </strong>
                  ),

                  p: ({ children }) => (
                    <p className="leading-6">
                      {children}
                    </p>
                  ),
                }}
              >
                {msg.content.replace(/\n{3,}/g, "\n\n")}
              </ReactMarkdown>
              </div>
                              ) : (
                                msg.content
                              )}
                            </div>

              {/* Citations */}
              {msg.citations?.length > 0 && (
                <div className="space-y-2">
                  <p className="px-1 text-xs font-medium text-gray-500">
                    📎 {msg.citations.length} source{msg.citations.length > 1 ? "s" : ""} retrieved
                    {msg.chunksRetrieved !== undefined &&
                      ` · ${msg.chunksRetrieved} chunks searched`
                    }
                  </p>
                  {msg.citations.map((citation, cIdx) => (
                    <CitationCard key={cIdx} citation={citation} index={cIdx + 1} />
                  ))}
                </div>
              )}
            

            {/* User avatar */}
            {msg.role === "user" && (
              <div className="flex items-center justify-center flex-shrink-0 w-8 h-8 mt-1 bg-gray-700 rounded-lg">
                <User size={16} className="text-gray-300" />
              </div>
            )}
          </div>
        ))} 

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex gap-3">
            <div className="flex items-center justify-center flex-shrink-0 w-8 h-8 bg-blue-600 rounded-lg">
              <Bot size={16} className="text-white" />
            </div>
            <div className="flex items-center gap-2 px-4 py-3 text-sm text-gray-400 bg-gray-800 rounded-tl-sm rounded-2xl">
              <Loader2 size={14} className="animate-spin" />
              Searching your notes and generating answer...
              {showSlowMessage && (
                  <div className="mt-2 text-xs text-yellow-400">
                      Still generating...
                      Gemini may be experiencing heavy load.
                  </div>
              )}
            </div>
          </div>
        )}

        {/* Auto-scroll anchor */}
        <div ref={bottomRef} />
      </div>

      {/* ── Input Area ── */}
      <div
          className="relative z-10 p-5 border-t border-white/5 backdrop-blur-xl bg-slate-950/60"
        >
        <div className="flex items-end gap-3">
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about your notes... (Enter to send, Shift+Enter for new line)"
            rows={1}
            className="flex-1 px-5 py-3 text-sm text-white transition-all border outline-none resize-none bg-slate-900/80 border-white/10 focus:border-blue-500/40 rounded-2xl placeholder:text-slate-500"
            style={{ minHeight: "48px", maxHeight: "120px" }}
            onInput={e => {
              e.target.style.height = "auto";
              e.target.style.height = e.target.scrollHeight + "px";
            }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className={`
              w-12 h-12 rounded-xl flex items-center justify-center transition-all flex-shrink-0
              ${input.trim() && !isLoading
                ?  `
                bg-gradient-to-r
                from-blue-600
                to-violet-600
                hover:from-blue-500
                hover:to-violet-500
                text-white
                shadow-xl
                shadow-blue-900/40
                hover:scale-105
                `
                : "bg-gray-800 text-gray-600 cursor-not-allowed"
              }
            `}
          >
            {isLoading
              ? <Loader2 size={18} className="animate-spin" />
              : <Send size={18} />
            }
          </button>
        </div>
      </div>
    </div>
  );
}