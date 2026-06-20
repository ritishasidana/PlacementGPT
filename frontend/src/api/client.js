// frontend/src/api/client.js  (complete — adds missing functions)

import axios from "axios";

const API_BASE = "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,  // 2 min — generation can be slow
});

// ── Interceptor: global error logging ─────────────────────────────────────────
api.interceptors.response.use(
  res  => res,
  err  => {
    console.error(
      "API Error:",
      err.response?.status,
      err.response?.data?.detail || err.message
    );
    return Promise.reject(err);
  }
);

// ── Upload ─────────────────────────────────────────────────────────────────────
export const uploadPDF = async (file, docType, company = null) => {
  const formData = new FormData();
  formData.append("file",     file);
  formData.append("doc_type", docType);
  if (company) formData.append("company", company);

  const res = await api.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
};

// ── Documents ──────────────────────────────────────────────────────────────────
export const listDocuments = async () => {
  const res = await api.get("/documents");
  return res.data;
};

export const deleteDocumentAPI = async (filename) => {
  const res = await api.delete(`/documents/${encodeURIComponent(filename)}`);
  return res.data;
};

// ── Filters ────────────────────────────────────────────────────────────────────
export const getFilters = async () => {
  const res = await api.get("/filters");
  return res.data;
};

// ── Query ──────────────────────────────────────────────────────────────────────
export const queryDocuments = async (question, docTypes = null, company = null, topK = 5) => {
  const res = await api.post("/query", {
    question,
    doc_types: docTypes?.length ? docTypes : null,
    company:   company  || null,
    top_k:     topK,
  });
  return res.data;
};

// ── Generate ───────────────────────────────────────────────────────────────────
export const generateContent = async ({
  topic,
  generateType,
  docType   = null,
  company   = null,
  numQuestions = 20,
}) => {
  const res = await api.post("/generate", {
    topic,
    generate_type: generateType,
    doc_type:      docType  || null,
    company:       company  || null,
    num_questions: numQuestions,
  });
  return res.data;
};

export default api;