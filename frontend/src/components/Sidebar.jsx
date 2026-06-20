// frontend/src/components/Sidebar.jsx

import { useState } from "react";
import {
  Upload, FileText, Trash2, ChevronDown,
  ChevronRight, Database, Layers
} from "lucide-react";
import FilterPanel from "./FilterPanel";
import {
  formatDocType, formatCompany,
  formatChunkCount, truncateFilename,
  COLOR_CLASSES
} from "../utils/formatters";
import logo from "../assets/logo.png";
export default function Sidebar({
  // Documents
  documents,
  totalChunks,
  isLoadingDocs,
  onDeleteDocument,
  // Upload
  onOpenUpload,
  // Filters (passed through to FilterPanel)
  availableDocTypes,
  availableCompanies,
  activeDocTypes,
  activeCompany,
  onToggleDocType,
  onSetCompany,
  onClearFilters,
  hasActiveFilters,
}) {
  const [docsExpanded, setDocsExpanded] = useState(true);

  // Group documents by doc_type for organized display
  const grouped = documents.reduce((acc, doc) => {
    const key = doc.doc_type;
    if (!acc[key]) acc[key] = [];
    acc[key].push(doc);
    return acc;
  }, {});

  return (
    <aside
      className="
      flex flex-col
      w-[340px]
      border-r
      bg-slate-950/70
      backdrop-blur-xl
      border-white/5
      shadow-lg
      shadow-blue-950/20
      "
    >

  {/* ── Logo / Header ── */}
  <div className="px-6 py-5 border-b border-white/5">

    <div className="flex items-center gap-4">

      <img
        src={logo}
        alt="PlacementGPT"
        className="object-cover w-12 h-12 shadow-lg rounded-xl shadow-blue-900/40"
      />

      <div>
        <h1 className="text-base font-bold text-white">
          PlacementGPT
        </h1>
        <p className="text-xs text-slate-400">
          AI Placement Assistant
        </p>
      </div>

    </div>

  </div>

  {/* ── Statistics Card ── */}
      <div
  className="p-3 mx-4 mt-4 transition-all duration-300 border shadow-xl rounded-2xl border-white/5 bg-gradient-to-br from-slate-900 to-slate-800 shadow-blue-950/30 hover:border-blue-500/20"
>
  <div className="grid grid-cols-2 divide-x divide-white/5">

    <div className="py-1.5 flex flex-col items-center text-center">
      <p className="text-[10px] uppercase tracking-widest text-slate-500">
        DOCUMENTS
      </p>

      <p className="mt-1 text-3xl font-bold text-white">
        {documents.length}
      </p>
    </div>

    <div className="py-1.5 flex flex-col items-center text-center">
      <p className="text-[10px] uppercase tracking-widest text-slate-500">
        CHUNKS
      </p>

      <p className="mt-1 text-3xl font-bold text-blue-400">
        {totalChunks.toLocaleString()}
      </p>
    </div>

  </div>
</div>

  {/* ── Scrollable Content ── */}
  <div className="flex-1 p-3 space-y-4 overflow-y-auto">

        {/* ── Upload Button ── */}
        <button
          onClick={onOpenUpload}
          className="flex items-center justify-center w-full gap-2 px-4 py-2.5 text-[13px] font-medium text-white transition-all duration-300 border  rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 border-white/5 hover:border-blue-400/20">
          <Upload size={15} />
          Upload PDF
        </button>

        {/* ── Documents Section ── */}
        <div>
          {/* Collapsible header */}
          <button
            onClick={() => setDocsExpanded(!docsExpanded)}
            className="w-full flex items-center justify-between px-1 py-1.5
                       text-gray-400 hover:text-gray-200 transition-colors"
          >
            <div className="flex items-center gap-2">
              {docsExpanded
                ? <ChevronDown size={13} />
                : <ChevronRight size={13} />
              }
              <span className="text-[11px] font-semibold uppercase tracking-wider">
                Documents
              </span>
            </div>
            <span className="text-[10px] text-gray-600">
              {documents.length} file{documents.length !== 1 ? "s" : ""}
            </span>
          </button>

          {/* Documents list */}
          {docsExpanded && (
            <div className="mt-1 space-y-0.5">
              {isLoadingDocs ? (
                /* Skeleton loader */
                <div className="space-y-1.5 px-2 py-2">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="h-8 bg-gray-800 rounded-lg animate-pulse" />
                  ))}
                </div>
              ) : documents.length === 0 ? (
                <div className="px-3 py-4 text-center">
                  <Database size={20} className="mx-auto mb-2 text-gray-700" />
                  <p className="text-xs text-gray-600">No documents yet</p>
                  <p className="text-[11px] text-gray-700 mt-0.5">
                    Upload a PDF to start
                  </p>
                </div>
              ) : (
                /* Grouped by doc_type */
                Object.entries(grouped).map(([docType, docs]) => {
                  const config = formatDocType(docType);
                  const colors = COLOR_CLASSES[config.color] || COLOR_CLASSES.gray;

                  return (
                    <div key={docType} className="mb-1">
                      {/* Group header */}
                      <div className={`flex items-center gap-1.5 px-2 py-1 rounded text-[10px] font-medium ${colors.text}`}>
                        <span>{config.emoji}</span>
                        <span>{config.label}</span>
                        <span className="ml-auto font-normal text-gray-600">
                          {docs.length}
                        </span>
                      </div>

                      {/* Files in group */}
                      {docs.map(doc => (
                        <DocumentRow
                          key={doc.filename}
                          doc={doc}
                          onDelete={() => onDeleteDocument(doc.filename)}
                        />
                      ))}
                    </div>
                  );
                })
              )}
            </div>
          )}
        </div>

        {/* ── ChromaDB Stats ── */}
        {totalChunks > 0 && (
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-800/50">
            <Layers size={12} className="text-gray-500" />
            <span className="text-[11px] text-gray-500">
              {totalChunks.toLocaleString()} chunks indexed
            </span>
          </div>
        )}

        {/* Divider */}
        <div className="border-t border-gray-800" />

        {/* ── Filter Panel ── */}
        <FilterPanel
          availableDocTypes={availableDocTypes}
          availableCompanies={availableCompanies}
          activeDocTypes={activeDocTypes}
          activeCompany={activeCompany}
          onToggleDocType={onToggleDocType}
          onSetCompany={onSetCompany}
          onClear={onClearFilters}
          hasActiveFilters={hasActiveFilters}
        />
      </div>
    </aside>
  );
}


// ── Document Row Sub-component ─────────────────────────────────────────────────
function DocumentRow({ doc, onDelete }) {
  const [showDelete, setShowDelete] = useState(false);

  return (
    <div
      className="flex items-center gap-2 px-3 py-2 transition-colors rounded-lg cursor-default group hover:bg-gray-800"
      onMouseEnter={() => setShowDelete(true)}
      onMouseLeave={() => setShowDelete(false)}
    >
      <FileText size={12} className="flex-shrink-0 text-gray-500" />

      <div className="flex-1 min-w-0">
        <p className="text-xs leading-tight text-gray-300 truncate">
          {truncateFilename(doc.filename)}
        </p>
        <div className="flex items-center gap-1.5 mt-0.5">
          <span className="text-[10px] text-gray-600">
            {formatChunkCount(doc.chunks)}
          </span>
          {doc.company && (
            <>
              <span className="text-gray-700">·</span>
              <span className="text-[10px] text-pink-500">
                {formatCompany(doc.company)}
              </span>
            </>
          )}
        </div>
      </div>

      {/* Delete button — appears on hover */}
      {showDelete && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            if (window.confirm(`Delete "${doc.filename}"? This cannot be undone.`)) {
              onDelete();
            }
          }}
          className="flex-shrink-0 p-1 text-gray-600 transition-colors rounded hover:text-red-400"
        >
          <Trash2 size={12} />
        </button>
      )}
    </div>
  );
}




