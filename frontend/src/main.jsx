// frontend/src/main.jsx

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Toaster } from "react-hot-toast";
import "./index.css";
import App from "./App.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    {/* Toast notifications — positioned top-right */}
    <Toaster
      position="top-right"
      toastOptions={{
        duration: 4000,
        style: {
          background: "#1f2937",  // gray-800
          color:      "#f9fafb",  // gray-50
          border:     "1px solid #374151",  // gray-700
          fontSize:   "14px",
        },
        success: { iconTheme: { primary: "#22c55e", secondary: "#1f2937" } },
        error:   { iconTheme: { primary: "#ef4444", secondary: "#1f2937" } },
      }}
    />
    <App />
  </StrictMode>
);