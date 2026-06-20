// frontend/src/hooks/useDocuments.js

import { useState, useEffect, useCallback } from "react";
import { listDocuments, deleteDocumentAPI } from "../api/client";
import toast from "react-hot-toast";

/**
 * Custom hook for managing the uploaded documents list.
 *
 * WHY A CUSTOM HOOK?
 * The document list is needed in both Sidebar (display) and
 * App (to refresh after upload). Putting the logic here means
 * any component can use it without duplicating fetch logic.
 *
 * Returns:
 * - documents: array of DocumentInfo objects
 * - totalChunks: total chunks across all docs
 * - isLoading: fetch in progress
 * - refresh: function to re-fetch
 * - deleteDocument: function to delete a doc by filename
 */
export function useDocuments() {
  const [documents,   setDocuments]   = useState([]);
  const [totalChunks, setTotalChunks] = useState(0);
  const [isLoading,   setIsLoading]   = useState(false);

  const fetchDocuments = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await listDocuments();
      setDocuments(data.documents   || []);
      setTotalChunks(data.total_chunks || 0);
    } catch (err) {
      // Don't toast on initial load failure — backend might be starting up
      console.error("Failed to fetch documents:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Fetch on mount
  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const deleteDocument = useCallback(async (filename) => {
    try {
      await deleteDocumentAPI(filename);
      toast.success(`Deleted: ${filename}`);
      // Refresh list after deletion
      await fetchDocuments();
    } catch (err) {
      toast.error("Failed to delete document");
      console.error(err);
    }
  }, [fetchDocuments]);

  return {
    documents,
    totalChunks,
    isLoading,
    refresh: fetchDocuments,
    deleteDocument,
  };
}