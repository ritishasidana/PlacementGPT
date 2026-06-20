// frontend/src/components/CitationCard.jsx

import { useState } from "react";
import { FileText, ChevronDown, ChevronUp } from "lucide-react";

// Maps doc_type keys to display labels and colors
const DOC_TYPE_CONFIG = {
  dbms: {
    label: "DBMS",
    color: "text-purple-300 bg-purple-500/15 border-purple-500/30"
  },

  os: {
    label: "OS",
    color: "text-green-300 bg-green-500/15 border-green-500/30"
  },

  cn: {
    label: "CN",
    color: "text-blue-300 bg-blue-500/15 border-blue-500/30"
  },

  oop: {
    label: "OOP",
    color: "text-orange-300 bg-orange-500/15 border-orange-500/30"
  },

  interview_experience: {
    label: "Interview",
    color: "text-yellow-300 bg-yellow-500/15 border-yellow-500/30"
  },
};

export default function CitationCard({ citation, index }) {
  const [expanded, setExpanded] = useState(false);

  const config    = DOC_TYPE_CONFIG[citation.doc_type] || {
    label: citation.doc_type,
    color: "text-gray-400 bg-gray-900/40 border-gray-700"
  };

  const similarity = Math.round((citation.similarity || 0) * 100);
  const cleanName = String(
      citation.filename || citation.source || "Unknown Document"
  )
    .replace(/\s*\(Page.*?\)/i, "") // removes "(Page 2, Chunk 1)"
    .replace(/_[a-f0-9]{8}\.pdf$/i, "") // removes "_4af30d20.pdf"
    .replace(/\.pdf$/i, "") // removes remaining ".pdf"
    .replace(/_/g, " "); // converts underscores to spaces
  
  const pageMatch = citation.source?.match(/Page\s+(\d+)/i);
  const pageNumber = pageMatch ? pageMatch[1] : null;

  const chunkText =
  citation.chunk_text ||
  citation.text ||
  "Click to view source extract";

  const previewText =
    chunkText.length > 120
      ? chunkText.slice(0, 120) + "..."
      : chunkText;
  console.log("Citation:", citation);

  const [showFullText, setShowFullText] = useState(false);

  const displayedText =
    showFullText
      ? chunkText
      : chunkText.slice(0, 180) + (chunkText.length > 180 ? "..." : "");
  
  const formattedText = displayedText.replace(
    /(Q\d+\.)/g,
    "\n• $1"
  );
  return (
    <div
        className="overflow-hidden transition-all duration-300 border shadow-lg rounded-2xl border-white/5 bg-gradient-to-br from-slate-900/90 to-slate-800/80 backdrop-blur-xl shadow-black/20 hover:border-blue-500/20 hover:shadow-blue-900/20"
      >
      {/* ── Header (always visible) ── */}
      <div
        className="
              flex items-center
              gap-2
              px-3
              py-2
              cursor-pointer
              hover:bg-white/[0.03]
              transition-all
              duration-300
              "
        
      >
        {/* Source number */}
        <span className="w-5 font-mono text-center text-gray-500">{index}</span>

        <div
          className="flex items-center justify-center flex-shrink-0 rounded-lg w-7 h-7 bg-blue-500/10"
        >
          <FileText size={12} className="text-blue-400" />
      </div>

        {/* Filename */}
        <span className="flex-1 text-sm font-medium text-gray-300 truncate">
          📄 {cleanName}
        </span>

        {/* Page number */}
        <span className="flex-shrink-0 text-[10px] text-slate-500">
          Page {pageNumber || "Unknown"}
        </span>

        {/* Doc type badge */}
        <span
            className={`
              px-2.5 py-1
              rounded-full
              border
              text-[10px]
              font-semibold
              tracking-wide
              flex-shrink-0
              backdrop-blur-sm
              ${config.color}
            `}
          >
          {config.label}
        </span>

        {/* Company badge (for interview experiences) */}
        {citation.company && (
          <span className="px-1.5 py-0.5 rounded-full bg-gray-700 text-gray-300 border border-gray-600 text-[10px] flex-shrink-0">
            {citation.company.charAt(0).toUpperCase() + citation.company.slice(1)}
          </span>
        )}

        {/* Similarity score */}
        <span
            className={`
            px-2 py-0.5
            rounded-full
            text-[9px]
            font-semibold
            ${
              similarity >= 80
                ? "bg-green-500/10 text-green-400"
                : similarity >= 60
                ? "bg-yellow-500/10 text-yellow-400"
                : "bg-slate-700/40 text-slate-500"
            }
          `}
          >
          {similarity}%
        </span>

        {/* Expand toggle */}
        {expanded
          ? <ChevronUp  size={12} className="flex-shrink-0 text-gray-400" />
          : <ChevronDown size={12} className="flex-shrink-0 text-gray-400" />
        }
      </div>

      {/* ── Expanded chunk text ── */}
      <div className="px-3 py-2 border-t border-white/5">
  <button
    onClick={() => setExpanded(!expanded)}
    className="text-sm font-medium text-blue-400 hover:text-blue-300"
  >
    {expanded ? "▼ View Extract" : "▶ View Extract"}
  </button>
</div>

{expanded && (
  <div className="px-3 pb-3 bg-black/10">
    <p className="text-sm leading-6 text-gray-400 whitespace-pre-line">
      {formattedText}
    </p>

    {chunkText.length > 180 && (
      <button
        onClick={(e) => {
          e.stopPropagation();
          setShowFullText(!showFullText);
        }}
        className="mt-2 text-sm text-blue-400 hover:text-blue-300"
      >
        {showFullText ? "Show Less" : "Show More"}
      </button>
    )}
  </div>
)}

      {/* ── Collapsed preview ── */}
      {!expanded && (
        <div className="px-3 pb-2">
          <p className="text-[11px] leading-5 text-slate-500 line-clamp-2">
            {previewText}
          </p>
        </div>
      )}
    </div>
  );
}