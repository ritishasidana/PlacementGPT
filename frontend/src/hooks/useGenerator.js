// frontend/src/hooks/useGenerator.js

import { useState, useCallback, useEffect } from "react";
import { generateContent, getFilters } from "../api/client";
import toast from "react-hot-toast";

/**
 * Custom hook for the generator panel.
 *
 * Manages:
 * - Available topics (fetched from backend based on uploads)
 * - Generation form state (topic, type, company, numQuestions)
 * - Generation request + result
 * - Copy to clipboard
 * - Generation history (last 5 results)
 *
 * WHY HISTORY?
 * Generation is slow (3-8 seconds). If the user accidentally
 * navigates away, they'd lose their notes. History keeps
 * the last 5 results in memory during the session.
 */
export function useGenerator() {
  // ── Available options (from backend) ──────────────────────────────────────
  const [availableTopics,    setAvailableTopics]    = useState([]);
  const [availableCompanies, setAvailableCompanies] = useState([]);
  const [availableDocTypes,  setAvailableDocTypes]  = useState([]);

  // ── Form state ─────────────────────────────────────────────────────────────
  const [topic,        setTopic]        = useState("");
  const [customTopic,  setCustomTopic]  = useState("");
  const [genType,      setGenType]      = useState("revision_notes");
  const [docType,      setDocType]      = useState("");
  const [company,      setCompany]      = useState("");
  const [numQuestions, setNumQuestions] = useState(10);

  // ── Result state ───────────────────────────────────────────────────────────
  const [result,       setResult]       = useState(null);   // {content, topic, genType, timestamp}
  const [isGenerating, setIsGenerating] = useState(false);
  const [history,      setHistory]      = useState([]);     // Last 5 results

  // Final topic used in generation
  const finalTopic = customTopic.trim() || topic;

  // ── Fetch available options on mount ──────────────────────────────────────
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        // Fetch available topics from the backend's dynamic endpoint
        const res = await fetch("http://localhost:8000/api/v1/generate/topics");
        if (res.ok) {
          const data = await res.json();
          setAvailableTopics(data.topics    || []);
          setAvailableDocTypes(data.doc_types || []);
        }
      } catch (err) {
        console.error("Failed to fetch topics:", err);
      }

      // Also fetch companies for the company dropdown
      try {
        const filterData = await getFilters();
        setAvailableCompanies(filterData.companies || []);
      } catch (err) {
        console.error("Failed to fetch companies:", err);
      }
    };

    fetchOptions();
  }, []);

  // ── Generate ───────────────────────────────────────────────────────────────
  const generate = useCallback(async () => {
    if (!finalTopic.trim()) {
      toast.error("Please select or enter a topic");
      return;
    }

    setIsGenerating(true);
    setResult(null);

    try {
      const data = await generateContent({
        topic:       finalTopic,
        generateType: genType,
        docType:     docType || null,
        company:     company || null,
        numQuestions,
      });

      const newResult = {
        content:   data.content,
        topic:     data.topic,
        genType:   data.generate_type,
        company:   company || null,
        timestamp: new Date().toLocaleTimeString(),
      };

      setResult(newResult);

      // Add to history (keep last 5)
      setHistory(prev => [newResult, ...prev].slice(0, 5));

      toast.success(
        genType === "revision_notes"
          ? "Revision notes generated!"
          : `${numQuestions} interview questions generated!`
      );

    } catch (err) {
      const msg = err.response?.data?.detail || "Generation failed. Please try again.";
      toast.error(msg);
    } finally {
      setIsGenerating(false);
    }
  }, [finalTopic, genType, docType, company, numQuestions]);

  // ── Copy to clipboard ──────────────────────────────────────────────────────
  const copyResult = useCallback(async () => {
    if (!result?.content) return;
    try {
      await navigator.clipboard.writeText(result.content);
      toast.success("Copied to clipboard!");
    } catch {
      toast.error("Copy failed — try selecting and copying manually");
    }
  }, [result]);

  // ── Load from history ──────────────────────────────────────────────────────
  const loadFromHistory = useCallback((historyItem) => {
    setResult(historyItem);
  }, []);

  // ── Reset form ─────────────────────────────────────────────────────────────
  const resetForm = useCallback(() => {
    setTopic("");
    setCustomTopic("");
    setDocType("");
    setCompany("");
    setNumQuestions(10);
    setResult(null);
  }, []);

  return {
    // Options
    availableTopics,
    availableCompanies,
    availableDocTypes,
    // Form state + setters
    topic, setTopic,
    customTopic, setCustomTopic,
    genType, setGenType,
    docType, setDocType,
    company, setCompany,
    numQuestions, setNumQuestions,
    finalTopic,
    // Results
    result,
    isGenerating,
    history,
    // Actions
    generate,
    copyResult,
    loadFromHistory,
    resetForm,
  };
}