// frontend/src/components/GeneratorPanel.jsx  (complete replacement)

import { useState } from "react";
import {
  BookOpen, HelpCircle, Loader2, Copy, Check,
  ChevronDown, Clock, RotateCcw, Sparkles, Info
} from "lucide-react";
import { useGenerator } from "../hooks/useGenerator";
import { DOC_TYPE_CONFIG, formatCompany } from "../utils/formatters";

export default function GeneratorPanel() {
  const {
    availableTopics, availableCompanies, availableDocTypes,
    topic, setTopic,
    customTopic, setCustomTopic,
    genType, setGenType,
    docType, setDocType,
    company, setCompany,
    numQuestions, setNumQuestions,
    finalTopic,
    result, isGenerating, history,
    generate, copyResult, loadFromHistory, resetForm,
  } = useGenerator();

  const [copied,       setCopied]       = useState(false);
  const [showHistory,  setShowHistory]  = useState(false);
  const [activeSection, setActiveSection] = useState(null);

  const handleCopy = async () => {
    await copyResult();
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Topics to show: dynamic from backend, or fallback presets
  const topicsToShow = availableTopics.length > 0 ? availableTopics : [
    "DBMS", "Operating Systems", "Computer Networks", "OOP",
    "SQL", "Deadlock", "Process Scheduling", "TCP vs UDP",
    "Normalization", "Memory Management"
  ];

  return (
  <div className="relative flex h-full overflow-hidden bg-[#020617]">

    <div
      className="
        absolute
        top-20
        right-10
        w-[500px]
        h-[500px]
        rounded-full
        bg-blue-600/10
        blur-[140px]
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
        blur-[120px]
        pointer-events-none
      "
    />

      {/* ════════════════════════════════════
          LEFT PANEL — Controls
      ════════════════════════════════════ */}
      <div className="relative z-10 flex flex-col flex-1 overflow-hidden">

        {/* Header */}
        <div className="flex-shrink-0 px-5 py-4 border-b border-gray-800">
          <div className="flex items-center gap-2">
            <Sparkles size={16} className="text-blue-400" />
            <h2
              className="text-lg font-bold text-transparent bg-gradient-to-r from-blue-400 via-cyan-300 to-violet-400 bg-clip-text"
            >
              AI Generator
            </h2>
          </div>
          <p className="mt-1 text-xs text-gray-500">
            Generate from your uploaded documents
          </p>
        </div>

        {/* Scrollable form */}
        <div className="flex-1 p-4 space-y-5 overflow-y-auto">

          {/* ── Generate Type ── */}
          <div className="space-y-2">
            <label className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
              What to Generate
            </label>
            <div className="grid grid-cols-2 gap-1.5 p-1 bg-gray-800 rounded-xl">
              {[
                { value: "revision_notes",     Icon: BookOpen,   label: "Revision Notes" },
                { value: "interview_questions", Icon: HelpCircle, label: "Interview Q&A"  },
              ].map(({ value, Icon, label }) => (
                <button
                  key={value}
                  onClick={() => { setGenType(value); setCompany(""); }}
                  className={`
                    flex items-center justify-center gap-1.5 py-2.5 px-2
                    rounded-lg text-xs font-medium transition-all
                    ${genType === value
                      ? `
                          bg-gradient-to-r
                          from-blue-600
                          to-violet-600
                          hover:from-blue-500
                          hover:to-violet-500
                          text-white
                          shadow-xl
                          shadow-blue-900/40
                          hover:scale-[1.02]
                          `
                      : "text-gray-400 hover:text-gray-200"
                    }
                  `}
                >
                  <Icon size={13} />
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* ── Topic Selection ── */}
          <div className="space-y-2">
            <label className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
              Topic
            </label>

            {/* Preset chips — scrollable row */}
            {topicsToShow.length > 0 && (
              <div className="flex flex-wrap gap-1.5 max-h-28 overflow-y-auto
                              scrollbar-thin scrollbar-thumb-gray-700">
                {topicsToShow.map(t => (
                  <button
                    key={t}
                    onClick={() => { setTopic(t); setCustomTopic(""); }}
                    className={`
                      px-2.5 py-1 rounded-full text-[11px] border transition-all
                      whitespace-nowrap
                      ${topic === t && !customTopic
                        ? "bg-gradient-to-r from-blue-600 to-violet-600 text-white border-transparent shadow-lg shadow-blue-900/30"
                        : "bg-gray-800 text-gray-400 border-gray-700 hover:border-gray-500 hover:text-gray-200"
                      }
                    `}
                  >
                    {t}
                  </button>
                ))}
              </div>
            )}

            {/* Custom topic */}
            <input
              type="text"
              placeholder="Or type a custom topic..."
              value={customTopic}
              onChange={e => { setCustomTopic(e.target.value); setTopic(""); }}
              className="w-full bg-gray-800 border border-gray-700 text-white
                         text-xs rounded-lg px-3 py-2.5 focus:outline-none
                         focus:border-blue-500 placeholder-gray-600 transition-colors"
            />

            {/* Showing what will be searched */}
            {finalTopic && (
              <p className="text-[10px] text-gray-600 flex items-center gap-1">
                <Info size={10} />
                Will search for: <span className="text-blue-400">{finalTopic}</span>
              </p>
            )}
          </div>

          {/* ── Search In (doc type) ── */}
          <div className="space-y-2">
            <label className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
              Search In
            </label>
            <div className="relative">
              <select
                value={docType}
                onChange={e => setDocType(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 text-gray-300
                           text-xs rounded-lg px-3 py-2.5 appearance-none
                           focus:outline-none focus:border-blue-500 pr-8
                           transition-colors cursor-pointer"
              >
                <option value="">All document types</option>
                {Object.entries(DOC_TYPE_CONFIG)
                  .filter(([key]) => key !== "interview_experience")
                  .map(([key, cfg]) => (
                    <option
                      key={key}
                      value={key}
                      disabled={availableDocTypes.length > 0 && !availableDocTypes.includes(key)}
                    >
                      {cfg.emoji} {cfg.full}
                      {availableDocTypes.length > 0 && !availableDocTypes.includes(key)
                        ? " (not uploaded)"
                        : ""
                      }
                    </option>
                  ))
                }
              </select>
              <ChevronDown size={12} className="absolute right-2.5 top-3 text-gray-500 pointer-events-none" />
            </div>
          </div>

          {/* ── Company Focus (interview questions only) ── */}
          {genType === "interview_questions" && (
            <div className="space-y-2">
              <label className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
                Company Focus
                <span className="ml-1 font-normal text-gray-600 normal-case">(optional)</span>
              </label>

              {/* Company chips — only show companies that are uploaded */}
              {availableCompanies.length > 0 ? (
                <div className="flex flex-wrap gap-1.5">
                  <button
                    onClick={() => setCompany("")}
                    className={`px-2.5 py-1 rounded-full text-[11px] border transition-all
                      ${!company
                        ? "bg-gray-600 text-white border-gray-500"
                        : "bg-gray-800 text-gray-400 border-gray-700 hover:border-gray-500"
                      }`}
                  >
                    All
                  </button>
                  {availableCompanies.map(c => (
                    <button
                      key={c}
                      onClick={() => setCompany(company === c ? "" : c)}
                      className={`px-2.5 py-1 rounded-full text-[11px] border transition-all
                        ${company === c
                          ? "bg-pink-600 text-white border-pink-600"
                          : "bg-gray-800 text-gray-400 border-gray-700 hover:border-gray-500"
                        }`}
                    >
                      {formatCompany(c)}
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-xs italic text-gray-600">
                  No interview experiences uploaded yet
                </p>
              )}
            </div>
          )}

          {/* ── Number of Questions slider ── */}
          {genType === "interview_questions" && (
            <div className="space-y-2">
              <label className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
                Questions: <span className="font-bold text-blue-400">{numQuestions}</span>
              </label>
              <input
                type="range" min={5} max={30} step={5}
                value={numQuestions}
                onChange={e => setNumQuestions(Number(e.target.value))}
                className="w-full cursor-pointer accent-blue-500"
              />
              <div className="flex justify-between text-[10px] text-gray-600">
                {[5, 10, 15, 20, 25, 30].map(n => (
                  <span key={n} className={numQuestions === n ? "text-blue-400 font-medium" : ""}>
                    {n}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* ── Summary before generating ── */}
          {finalTopic && (
            <div className="p-3 space-y-1 border border-gray-700 bg-gray-800/60 rounded-xl">
              <p className="text-[11px] text-gray-400 font-medium">Will generate:</p>
              <p className="text-xs text-white">
                {genType === "revision_notes" ? "📖 Revision Notes" : "💡 Interview Questions"}
                {" for "}
                <span className="font-medium text-blue-300">{finalTopic}</span>
              </p>
              {genType === "interview_questions" && (
                <p className="text-[11px] text-gray-500">
                  {numQuestions} questions
                  {company ? ` · Focused on ${formatCompany(company)}` : " · All companies"}
                </p>
              )}
              {docType && (
                <p className="text-[11px] text-gray-500">
                  Searching in: {DOC_TYPE_CONFIG[docType]?.full || docType}
                </p>
              )}
            </div>
          )}

        </div>

        {/* ── Generate Button + Reset (sticky bottom) ── */}
        <div className="flex-shrink-0 p-4 space-y-2 border-t border-gray-800">
          <button
            onClick={generate}
            disabled={!finalTopic || isGenerating}
            className={`
              w-full py-3 rounded-xl text-sm font-semibold transition-all
              flex items-center justify-center gap-2
              ${finalTopic && !isGenerating
                ? "bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-900/40"
                : "bg-gray-800 text-gray-600 cursor-not-allowed"
              }
            `}
          >
            {isGenerating ? (
              <>
                <Loader2 size={15} className="animate-spin" />
                Generating...
              </>
            ) : (
              <>
                {genType === "revision_notes"
                  ? <BookOpen size={15} />
                  : <HelpCircle size={15} />
                }
                Generate
              </>
            )}
          </button>

          {result && (
            <button
              onClick={resetForm}
              className="w-full py-2 rounded-xl text-xs text-gray-500
                         hover:text-gray-300 flex items-center justify-center gap-1.5
                         transition-colors"
            >
              <RotateCcw size={12} />
              Reset
            </button>
          )}
        </div>
      </div>

      {/* ════════════════════════════════════
          RIGHT PANEL — Output
      ════════════════════════════════════ */}
      <div className="flex flex-col flex-1 overflow-hidden bg-slate-950/30">

        {/* ── Output Toolbar ── */}
        {(result || history.length > 0) && (
          <div className="flex items-center justify-between flex-shrink-0 px-5 py-3 border-b border-gray-800 bg-gray-900/50">
            <div className="flex items-center gap-3">
              {result && (
                <div>
                  <h3 className="text-sm font-medium text-white">
                    {result.genType === "revision_notes"
                      ? "📖 Revision Notes"
                      : "💡 Interview Questions"
                    }: {result.topic}
                  </h3>
                  <p className="text-[11px] text-gray-500">
                    Generated at {result.timestamp}
                    {result.company && ` · ${formatCompany(result.company)}`}
                  </p>
                </div>
              )}
            </div>

            <div className="flex items-center gap-2">
              {/* History dropdown */}
              {history.length > 1 && (
                <div className="relative">
                  <button
                    onClick={() => setShowHistory(!showHistory)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg
                               bg-gray-800 hover:bg-gray-700 text-xs text-gray-300
                               transition-colors border border-gray-700"
                  >
                    <Clock size={12} />
                    History ({history.length})
                    <ChevronDown size={11} />
                  </button>

                  {showHistory && (
                    <div className="absolute right-0 z-20 w-64 mt-1 overflow-hidden bg-gray-800 border border-gray-700 shadow-xl top-full rounded-xl">
                      {history.map((item, i) => (
                        <button
                          key={i}
                          onClick={() => { loadFromHistory(item); setShowHistory(false); }}
                          className="w-full flex items-start gap-3 px-3 py-2.5
                                     hover:bg-gray-700 transition-colors text-left"
                        >
                          <span className="flex-shrink-0 text-sm">
                            {item.genType === "revision_notes" ? "📖" : "💡"}
                          </span>
                          <div className="min-w-0">
                            <p className="text-xs font-medium text-gray-200 truncate">
                              {item.topic}
                            </p>
                            <p className="text-[10px] text-gray-500">
                              {item.timestamp}
                              {item.company && ` · ${formatCompany(item.company)}`}
                            </p>
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Copy button */}
              {result && (
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg
                             bg-gray-800 hover:bg-gray-700 text-xs text-gray-300
                             transition-colors border border-gray-700"
                >
                  {copied
                    ? <><Check size={12} className="text-green-400" /> Copied!</>
                    : <><Copy size={12} /> Copy</>
                  }
                </button>
              )}
            </div>
          </div>
        )}

        {/* ── Output Content ── */}
        <div className="flex-1 overflow-y-auto">
          {isGenerating ? (
            <GeneratingState genType={genType} topic={finalTopic} />
          ) : result ? (
            <div className="max-w-4xl p-6 mx-auto">
              <MarkdownRenderer content={result.content} />
            </div>
          ) : (
            <EmptyState genType={genType} />
          )}
        </div>
      </div>
    </div>
  );
}


// ── Generating State Component ─────────────────────────────────────────────────
function GeneratingState({ genType, topic }) {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-5 p-8 text-center">
      <div className="relative">
        <div className="flex items-center justify-center w-16 h-16 bg-blue-600/20 rounded-2xl">
          {genType === "revision_notes"
            ? <BookOpen size={28} className="text-blue-400" />
            : <HelpCircle size={28} className="text-blue-400" />
          }
        </div>
        {/* Pulse ring */}
        <div className="absolute inset-0 border-2 rounded-2xl border-blue-500/40 animate-ping" />
      </div>
      <div>
        <p className="font-semibold text-white">
          Generating {genType === "revision_notes" ? "revision notes" : "interview questions"}
        </p>
        <p className="mt-1 text-sm text-gray-400">
          for <span className="text-blue-300">{topic}</span>
        </p>
        <p className="mt-3 text-xs text-gray-600">
          Searching your documents and crafting content...
        </p>
      </div>
      {/* Step indicators */}
      <div className="flex flex-col gap-2 mt-2 text-xs text-gray-600">
        {[
          "🔍 Searching uploaded notes...",
          "📚 Retrieving relevant chunks...",
          "🤖 Generating with Gemini...",
        ].map((step, i) => (
          <div key={i} className="flex items-center gap-2">
            <Loader2 size={10} className="text-blue-600 animate-spin" />
            {step}
          </div>
        ))}
      </div>
    </div>
  );
}


// ── Empty State Component ──────────────────────────────────────────────────────
function EmptyState({ genType }) {
  const isNotes = genType === "revision_notes";
  return (
    <div className="flex flex-col items-center justify-center h-full gap-4 p-8 text-center">
      <div
          className="flex items-center justify-center w-24 h-24 border shadow-xl rounded-3xl bg-gradient-to-br from-blue-500/20 to-violet-500/20 border-blue-500/10 shadow-blue-900/20"
>
        {isNotes
          ? <BookOpen size={32} className="text-gray-600" />
          : <HelpCircle size={32} className="text-gray-600" />
        }
      </div>
      <div>
        <p className="text-lg font-semibold text-gray-300">
          {isNotes ? "Revision Notes Generator" : "Interview Question Generator"}
        </p>
        <p className="max-w-md mt-2 text-sm text-gray-500">
          {isNotes
            ? "Select a topic and generate structured revision notes from your uploaded study materials."
            : "Select a topic and company to generate targeted interview questions based on your notes and real interview experiences."
          }
        </p>
      </div>

      {/* Feature highlights */}
      <div className="grid max-w-lg grid-cols-3 gap-3 mt-2">
        {(isNotes ? [
          { emoji: "📌", label: "Topic Overview" },
          { emoji: "🔑", label: "Key Concepts"   },
          { emoji: "✅", label: "Revision Checklist" },
        ] : [
          { emoji: "🎯", label: "Company-Specific" },
          { emoji: "📊", label: "Difficulty Levels" },
          { emoji: "💬", label: "With Follow-ups"  },
        ]).map(({ emoji, label }) => (
          <div key={label} className="p-3 transition-all duration-300 border rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 border-white/5 hover:border-blue-500/20 hover:-translate-y-1">
            <div className="mb-1 text-xl">{emoji}</div>
            <p className="text-[11px] text-gray-400">{label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}


// ── Markdown Renderer ──────────────────────────────────────────────────────────
function MarkdownRenderer({ content }) {
  const lines = content.split("\n");

  return (
    <div className="space-y-1 text-sm leading-relaxed text-gray-300">
      {lines.map((line, i) => {
        // H2: ## Title
        if (line.startsWith("## ")) {
          return (
            <h2 key={i} className="pb-2 mb-3 text-base font-bold text-white border-b border-gray-800 mt-7 first:mt-0">
              {line.slice(3)}
            </h2>
          );
        }
        // H3: ### Title
        if (line.startsWith("### ")) {
          return (
            <h3 key={i} className="mt-5 mb-2 text-sm font-semibold text-gray-100">
              {line.slice(4)}
            </h3>
          );
        }
        // Question: **Q1: ...**
        if (/^\*\*Q\d+:/.test(line)) {
          return (
            <div key={i} className="mt-6 mb-2">
              <p className="text-sm font-semibold text-blue-300">
                {line.replace(/\*\*/g, "")}
              </p>
            </div>
          );
        }
        // Blockquote: > text
        if (line.startsWith("> ")) {
          const text = line.slice(2);
          // Special styling for difficulty / answer / follow-up / source
          const isDifficulty = text.startsWith("**Difficulty**");
          const isAnswer     = text.startsWith("**Expected Answer**");
          const isFollowup   = text.startsWith("**Follow-up**");
          const isSource     = text.startsWith("**Source**");

          const colorClass = isDifficulty ? "border-yellow-700/50 bg-yellow-900/10"
                           : isAnswer     ? "border-gray-700    bg-gray-800/40"
                           : isFollowup   ? "border-purple-700/50 bg-purple-900/10"
                           : isSource     ? "border-blue-700/50 bg-blue-900/10"
                           :               "border-gray-700    bg-gray-800/30";

          return (
            <div key={i} className={`border-l-2 pl-3 py-1 rounded-r text-xs ${colorClass}`}>
              {renderInlineBold(text)}
            </div>
          );
        }
        // Bullet: - text or * text
        if (line.startsWith("- ") || line.startsWith("* ")) {
          return (
            <div key={i} className="flex gap-2.5 items-start">
              <span className="text-blue-500 mt-1.5 flex-shrink-0 text-xs">•</span>
              <span className="text-sm">{renderInlineBold(line.slice(2))}</span>
            </div>
          );
        }
        // Checkbox: - [ ] or - [x]
        if (line.startsWith("- [ ]") || line.startsWith("- [x]")) {
          const checked = line.startsWith("- [x]");
          return (
            <div key={i} className="flex gap-2.5 items-start">
              <span className={`mt-0.5 flex-shrink-0 text-sm ${
                checked ? "text-green-400" : "text-gray-600"
              }`}>
                {checked ? "☑" : "☐"}
              </span>
              <span className={`text-sm ${checked ? "text-gray-400 line-through" : ""}`}>
                {renderInlineBold(line.slice(6))}
              </span>
            </div>
          );
        }
        // Numbered: 1. text
        if (/^\d+\.\s/.test(line)) {
          const match = line.match(/^(\d+)\.\s(.+)/);
          if (match) {
            return (
              <div key={i} className="flex gap-2.5 items-start">
                <span className="flex-shrink-0 w-5 mt-1 font-mono text-xs text-right text-gray-500">
                  {match[1]}.
                </span>
                <span className="text-sm">{renderInlineBold(match[2])}</span>
              </div>
            );
          }
        }
        // Horizontal rule: ---
        if (line.trim() === "---") {
          return <hr key={i} className="my-4 border-gray-800" />;
        }
        // Empty line
        if (!line.trim()) {
          return <div key={i} className="h-1" />;
        }
        // Default paragraph
        return (
          <p key={i} className="text-sm">{renderInlineBold(line)}</p>
        );
      })}
    </div>
  );
}

// Renders **bold** and `code` inline
function renderInlineBold(text) {
  // Handle both **bold** and `code`
  const parts = text.split(/(\*\*.+?\*\*|`.+?`)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={i} className="font-semibold text-white">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code key={i} className="bg-gray-800 text-blue-300 px-1.5 py-0.5
                                  rounded text-xs font-mono">
          {part.slice(1, -1)}
        </code>
      );
    }
    return part;
  });
}