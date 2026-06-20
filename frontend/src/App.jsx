// frontend/src/App.jsx

import { useState } from "react";
import Sidebar       from "./components/Sidebar";
import ChatWindow    from "./components/ChatWindow";
import GeneratorPanel from "./components/GeneratorPanel";
import UploadModal   from "./components/UploadModal";
import { useDocuments } from "./hooks/useDocuments";
import { useFilters }   from "./hooks/useFilters";
import { MessageSquare, Sparkles } from "lucide-react";

// ── Tab Definition ─────────────────────────────────────────────────────────────
const TABS = [
  { id: "chat",      label: "Ask Questions", icon: MessageSquare },
  { id: "generate",  label: "Generate",      icon: Sparkles      },
];

export default function App() {
  // ── UI State ───────────────────────────────────────────────────────────────
  const [activeTab,     setActiveTab]     = useState("chat");
  const [showUpload,    setShowUpload]    = useState(false);

  // ── Documents (custom hook) ────────────────────────────────────────────────
  const {
    documents,
    totalChunks,
    isLoading: isLoadingDocs,
    refresh:   refreshDocuments,
    deleteDocument,
  } = useDocuments();

  // ── Filters (custom hook) ──────────────────────────────────────────────────
  const {
    availableDocTypes,
    availableCompanies,
    activeDocTypes,
    activeCompany,
    toggleDocType,
    setActiveCompany,
    clearFilters,
    hasActiveFilters,
    refreshFilters,
  } = useFilters();

  // ── Upload Success Handler ─────────────────────────────────────────────────
  // Called by UploadModal when upload completes successfully.
  // Refreshes both the document list and filter options.
  const handleUploadSuccess = async () => {
    await refreshDocuments();
    await refreshFilters();
  };

  // Active filters object passed to ChatWindow
  const activeFilters = {
    docTypes: activeDocTypes.length > 0 ? activeDocTypes : null,
    company:  activeCompany,
  };

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="flex flex-col h-screen overflow-hidden bg-gray-950">

      {/* ── Top Navigation Bar ── */}
      <header className="z-20 flex items-center justify-between px-6 py-3 border-b border-white/5 backdrop-blur-xl bg-slate-950/70">

        {/* Tab switcher */}
        <div className="flex items-center gap-1 bg-white/[0.03] border border-white/[0.05] rounded-2xl p-1">
          {TABS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`
                flex items-center gap-2 px-4 py-1.5 rounded-lg text-sm
                font-medium transition-all
                ${activeTab === id
                  ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-900/30"
                  : "text-slate-400  hover:text-white"
                }
              `}
            >
              <Icon size={15} />
              {label}
            </button>
          ))}
        </div>

        {/* Active filter indicator */}
        {hasActiveFilters && (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-900/40
                          border border-blue-700 rounded-lg">
            <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse" />
            <span className="text-xs font-medium text-blue-300">
              Filters active
            </span>
            <button
              onClick={clearFilters}
              className="ml-1 text-xs text-blue-400 transition-colors hover:text-blue-200"
            >
              ✕
            </button>
          </div>
        )}
      </header>

      {/* ── Main Layout ── */}
      <div className="flex flex-1 overflow-hidden">

        {/* ── Sidebar ── */}
        <Sidebar
          documents={documents}
          totalChunks={totalChunks}
          isLoadingDocs={isLoadingDocs}
          onDeleteDocument={deleteDocument}
          onOpenUpload={() => setShowUpload(true)}
          availableDocTypes={availableDocTypes}
          availableCompanies={availableCompanies}
          activeDocTypes={activeDocTypes}
          activeCompany={activeCompany}
          onToggleDocType={toggleDocType}
          onSetCompany={setActiveCompany}
          onClearFilters={clearFilters}
          hasActiveFilters={hasActiveFilters}
        />

        {/* ── Main Content Area ── */}
        <main className="flex-1 overflow-hidden">
          {activeTab === "chat" && (
            <ChatWindow activeFilters={activeFilters} />
          )}
          {activeTab === "generate" && (
            <GeneratorPanel activeFilters={activeFilters} />
          )}
        </main>
      </div>

      {/* ── Upload Modal ── */}
      {showUpload && (
        <UploadModal
          onClose={() => setShowUpload(false)}
          onUploadSuccess={handleUploadSuccess}
        />
      )}
      <div className="fixed inset-0 overflow-hidden -z-10">
  <div className="absolute top-40 left-40 w-96 h-96 bg-blue-600/10 blur-[140px] rounded-full" />
  <div className="absolute bottom-20 right-20 w-96 h-96 bg-violet-600/10 blur-[140px] rounded-full" />
</div>
    </div>
    
  );
}