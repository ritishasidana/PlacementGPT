// frontend/src/utils/formatters.js

// ── Doc Type Display Config ────────────────────────────────────────────────────
export const DOC_TYPE_CONFIG = {
  dbms: {
    label:  "DBMS",
    emoji:  "📚",
    color:  "blue",
    full:   "Database Management Systems",
  },
  os: {
    label:  "OS",
    emoji:  "💻",
    color:  "green",
    full:   "Operating Systems",
  },
  cn: {
    label:  "CN",
    emoji:  "🌐",
    color:  "yellow",
    full:   "Computer Networks",
  },
  oop: {
    label:  "OOP",
    emoji:  "🧩",
    color:  "purple",
    full:   "Object Oriented Programming",
  },
  interview_experience: {
    label:  "Interview",
    emoji:  "🏢",
    color:  "pink",
    full:   "Interview Experience",
  },
};

// ── Tailwind color maps ────────────────────────────────────────────────────────
// Tailwind purges unused classes — we must use complete class strings,
// not dynamic ones like `bg-${color}-500`. This map solves that.
export const COLOR_CLASSES = {
  blue:   { bg: "bg-blue-900/40",   text: "text-blue-400",   border: "border-blue-700",   dot: "bg-blue-400"   },
  green:  { bg: "bg-green-900/40",  text: "text-green-400",  border: "border-green-700",  dot: "bg-green-400"  },
  yellow: { bg: "bg-yellow-900/40", text: "text-yellow-400", border: "border-yellow-700", dot: "bg-yellow-400" },
  purple: { bg: "bg-purple-900/40", text: "text-purple-400", border: "border-purple-700", dot: "bg-purple-400" },
  pink:   { bg: "bg-pink-900/40",   text: "text-pink-400",   border: "border-pink-700",   dot: "bg-pink-400"   },
  gray:   { bg: "bg-gray-800",      text: "text-gray-400",   border: "border-gray-700",   dot: "bg-gray-400"   },
};

// ── Formatters ─────────────────────────────────────────────────────────────────

export function formatDocType(docType) {
  return DOC_TYPE_CONFIG[docType] || {
    label: docType,
    emoji: "📄",
    color: "gray",
    full:  docType,
  };
}

export function formatCompany(company) {
  if (!company) return null;
  return company.charAt(0).toUpperCase() + company.slice(1);
}

export function formatFileSize(bytes) {
  if (bytes < 1024)        return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function formatChunkCount(count) {
  if (count === 1) return "1 chunk";
  return `${count} chunks`;
}

export function truncateFilename(filename, maxLength = 28) {
  if (filename.length <= maxLength) return filename;
  const ext  = filename.split(".").pop();
  const base = filename.slice(0, maxLength - ext.length - 4);
  return `${base}...${ext}`;
}

export function formatSimilarity(score) {
  return `${Math.round(score * 100)}%`;
}
