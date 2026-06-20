// frontend/src/hooks/useFilters.js

import { useState, useEffect, useCallback } from "react";
import { getFilters } from "../api/client";

/**
 * Custom hook for managing search filters.
 *
 * Fetches available filter options from the backend
 * (derived from what's actually in ChromaDB — dynamic).
 *
 * Manages which filters are currently active.
 *
 * Returns:
 * - availableDocTypes:   doc types present in ChromaDB
 * - availableCompanies:  companies present in ChromaDB
 * - activeDocTypes:      currently selected doc type filters
 * - activeCompany:       currently selected company filter
 * - toggleDocType:       toggle a doc type filter on/off
 * - setActiveCompany:    set company filter
 * - clearFilters:        reset all filters
 * - hasActiveFilters:    boolean — are any filters active?
 */
export function useFilters() {
  // Available options (from backend)
  const [availableDocTypes,  setAvailableDocTypes]  = useState([]);
  const [availableCompanies, setAvailableCompanies] = useState([]);

  // Active selections
  const [activeDocTypes, setActiveDocTypes] = useState([]);
  const [activeCompany,  setActiveCompany]  = useState(null);

  // Fetch available options on mount and whenever docs change
  const fetchFilters = useCallback(async () => {
    try {
      const data = await getFilters();
      setAvailableDocTypes(data.doc_types  || []);
      setAvailableCompanies(data.companies || []);
    } catch (err) {
      console.error("Failed to fetch filters:", err);
    }
  }, []);

  useEffect(() => {
    fetchFilters();
  }, [fetchFilters]);

  // Toggle a doc type on/off
  const toggleDocType = useCallback((docType) => {
    setActiveDocTypes(prev =>
      prev.includes(docType)
        ? prev.filter(dt => dt !== docType)  // Remove if active
        : [...prev, docType]                  // Add if inactive
    );
  }, []);

  // Clear all active filters
  const clearFilters = useCallback(() => {
    setActiveDocTypes([]);
    setActiveCompany(null);
  }, []);

  const hasActiveFilters = activeDocTypes.length > 0 || activeCompany !== null;

  return {
    availableDocTypes,
    availableCompanies,
    activeDocTypes,
    activeCompany,
    toggleDocType,
    setActiveCompany,
    clearFilters,
    hasActiveFilters,
    refreshFilters: fetchFilters,
  };
}