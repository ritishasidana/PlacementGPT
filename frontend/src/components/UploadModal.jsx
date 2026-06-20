// frontend/src/components/UploadModal.jsx

import { useState } from "react";
import { uploadPDF } from "../api/client";
import toast from "react-hot-toast";
import { Upload, X, FileText, Loader2 } from "lucide-react";

// Document type options shown in the dropdown
const DOC_TYPES = [
  { value: "dbms",                 label: "📚 DBMS Notes" },
  { value: "os",                   label: "💻 Operating System Notes" },
  { value: "cn",                   label: "🌐 Computer Networks Notes" },
  { value: "oop",                  label: "🧩 OOP Notes" },
  { value: "interview_experience", label: "🏢 Interview Experience" },
];

const COMPANIES = [
  "Amazon", "Google", "Microsoft", "Flipkart",
  "Infosys", "TCS", "Wipro", "Adobe",
  "Samsung", "Oracle", "Uber", "Swiggy", "Zomato", "Other"
];

export default function UploadModal({ onClose, onUploadSuccess }) {
  // ── State ──────────────────────────────────────────────────────────────────
  const [selectedFile, setSelectedFile] = useState(null);
  const [docType, setDocType]           = useState("");
  const [company, setCompany]           = useState("");
  const [isUploading, setIsUploading]   = useState(false);
  const [dragOver, setDragOver]         = useState(false);

  // ── Derived state ──────────────────────────────────────────────────────────
  const isInterviewExp = docType === "interview_experience";
  const canSubmit = selectedFile && docType && (!isInterviewExp || company);

  // ── Drag and Drop Handlers ─────────────────────────────────────────────────
  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => setDragOver(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file?.type === "application/pdf") {
      setSelectedFile(file);
    } else {
      toast.error("Only PDF files are supported");
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) setSelectedFile(file);
  };

  // ── Upload Handler ─────────────────────────────────────────────────────────
  const handleUpload = async () => {
    if (!canSubmit) return;

    setIsUploading(true);

    try {
      const result = await uploadPDF(
        selectedFile,
        docType,
        isInterviewExp ? company : null
      );

      toast.success(
        `✅ Uploaded! Created ${result.chunks_created} searchable chunks from ${result.pages_extracted} pages.`
      );

      onUploadSuccess(result);  // Notify parent to refresh document list
      onClose();

    } catch (error) {
      const message = error.response?.data?.detail || "Upload failed. Please try again.";
      toast.error(`❌ ${message}`);
    } finally {
      setIsUploading(false);
    }
  };

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    // Backdrop
            <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4  bg-black/70 backdrop-blur-md"
        >

      {/* Modal */}
              <div
          className="w-full max-w-lg overflow-hidden border shadow-2xl  rounded-3xl border-white/10 bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800 shadow-blue-950/30 backdrop-blur-xl"
        >
        {/* Header */}
                  <div
            className="flex items-center justify-between p-6 border-b  border-white/5"
          >
          <h2 className="text-xl font-bold text-white">Upload PDF</h2>
          <button
            onClick={onClose}
            className="text-gray-400 transition-colors hover:text-white"
          >
            <X size={20} />
          </button>
        </div>

        <div className="p-6 space-y-5">
        <div
        className="p-4 border  rounded-2xl border-white/5 bg-gradient-to-r from-blue-500/10 to-violet-500/10"
      >
        <p className="text-sm font-medium text-white">
          Smart PDF Processing
        </p>

        <p className="mt-1 text-xs text-slate-400">
          Upload notes, interview experiences, or study materials.
          PDFs are automatically chunked and indexed into ChromaDB.
        </p>
      </div>
          {/* ── Drag and Drop Zone ── */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById("file-input").click()}
            className={`
              border-2
              border-dashed
              rounded-2xl
              p-10
              text-center
              cursor-pointer
              transition-all
              duration-300
              ${dragOver
                ? "border-blue-500 bg-blue-500/10 scale-[1.02]"
                : "border-white/10 hover:border-blue-500/30 hover:bg-slate-800/50"
              }
            `}
          >
            {selectedFile ? (
              <div className="flex items-center justify-center gap-3 text-green-400">
                <FileText size={24} />
                <span className="max-w-xs text-sm font-medium truncate">
                  {selectedFile.name}
                </span>
              </div>
            ) : (
              <div className="space-y-2 text-gray-400">
                <Upload
                  size={40}
                  className="
                    mx-auto
                    text-blue-400
                    drop-shadow-[0_0_20px_rgba(59,130,246,0.5)]
                  "
                />
                <p className="text-sm">Drop your PDF here or <span className="text-blue-400">browse</span></p>
                <p className="text-xs text-gray-500">PDF files only, max 50MB</p>
              </div>
            )}

            {/* Hidden file input */}
            <input
              id="file-input"
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={handleFileSelect}
            />
          </div>

          {/* ── Document Type Selector ── */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">
              Document Type <span className="text-red-400">*</span>
            </label>
            <select
              value={docType}
              onChange={(e) => {
                setDocType(e.target.value);
                setCompany(""); // Reset company when type changes
              }}
              className="w-full px-4 py-3 text-sm text-white transition-all border  bg-slate-900/80 border-white/10 rounded-xl focus:outline-none focus:border-blue-500/40 focus:ring-2 focus:ring-blue-500/10"
            >
              <option value="">Select document type...</option>
              {DOC_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* ── Company Selector (only for interview experiences) ── */}
          {isInterviewExp && (
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">
                Company <span className="text-red-400">*</span>
              </label>
              <select
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                className="w-full bg-gray-800 border border-gray-600 text-white rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-blue-500 transition-colors"
              >
                <option value="">Select company...</option>
                {COMPANIES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* ── Upload Button ── */}
          <button
            onClick={handleUpload}
            disabled={!canSubmit || isUploading}
            className={`
              w-full py-3 rounded-xl font-semibold text-sm transition-all flex items-center justify-center gap-2
              ${canSubmit && !isUploading
                ? `
                  bg-gradient-to-r
                  from-blue-600
                  to-violet-600
                  hover:from-blue-500
                  hover:to-violet-500
                  text-white
                  shadow-xl
                  shadow-blue-900/30
                  hover:scale-[1.02]
                  active:scale-[0.98]
                  `
                : "bg-slate-800 text-slate-500 cursor-not-allowed"
              }
            `}
          >
            {isUploading ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Processing PDF...
              </>
            ) : (
              <>
                <Upload size={18} />
                Upload & Process
              </>
            )}
          </button>

        </div>
      </div>
    </div>
  );
}