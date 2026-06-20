// frontend/src/components/FilterPanel.jsx

import { X } from "lucide-react";
import { formatDocType, formatCompany, COLOR_CLASSES } from "../utils/formatters";

export default function FilterPanel({
  availableDocTypes,
  availableCompanies,
  activeDocTypes,
  activeCompany,
  onToggleDocType,
  onSetCompany,
  onClear,
  hasActiveFilters,
}) {
  return (
        <div
          className="p-4 space-y-4 border rounded-2xlbg-gradient-to-br from-slate-900/80 to-slate-800/50 border-white/10 backdrop-blur-xl"
        >

      {/* ── Header ── */}
      <div className="flex items-center justify-between">
        <span
            className="
            text-[11px]
            font-semibold
            uppercase
            tracking-[0.2em]
            text-slate-500
            "
          >
          Filters
        </span>
        {hasActiveFilters && (
          <button
            onClick={onClear}
            className="flex items-center gap-1 px-2 py-1 text-xs transition-all rounded-lg text-slate-400 hover:text-white hover:bg-white/5"
          >
            <X size={10} />
            Clear
          </button>
        )}
      </div>

      {/* ── Subject Filter ── */}
      {availableDocTypes.length > 0 && (
        <div className="space-y-1.5">
          <p className="
                text-[10px]
                uppercase
                tracking-[0.18em]
                text-slate-500
                font-semibold
                ">
            Subject
          </p>
          <div className="space-y-1">
            {availableDocTypes.map(dt => {
              const config  = formatDocType(dt);
              const colors  = COLOR_CLASSES[config.color] || COLOR_CLASSES.gray;
              const isActive = activeDocTypes.includes(dt);

              return (
                <button
                  key={dt}
                  onClick={() => onToggleDocType(dt)}
                  className={`
                    w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs
                    transition-all border
                    ${isActive
                        ? `
                        bg-gradient-to-r
                        from-blue-600/20
                        to-violet-600/20
                        border-blue-500/20
                        text-white
                        shadow-lg
                        shadow-blue-900/20
                        `
                        : `
                        bg-slate-900/40
                        border-white/5
                        text-slate-400
                        hover:border-blue-500/10
                        hover:bg-slate-800/60
                        hover:text-white
                        `
}                  `}
                >
                  {/* Active indicator dot */}
                  <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                    isActive ? colors.dot : "bg-gray-600"
                  }`} />
                  <span>{config.emoji} {config.full}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* ── Company Filter ── */}
      {availableCompanies.length > 0 && (
        <div className="space-y-1.5">
          <p className="text-[11px] text-gray-500 font-medium uppercase tracking-wider">
            Company
          </p>
          <div className="space-y-1">
            {/* All companies option */}
            <button
              onClick={() => onSetCompany(null)}
              className={`
                w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs
                transition-all border
                ${!activeCompany
                  ? "bg-gray-800 text-gray-200 border-gray-600"
                  : "bg-transparent text-gray-400 border-transparent hover:bg-gray-800"
                }
              `}
            >
              <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                !activeCompany ? "bg-gray-200" : "bg-gray-600"
              }`} />
              All Companies
            </button>

            {availableCompanies.map(company => {
              const isActive = activeCompany === company;
              return (
                <button
                  key={company}
                  onClick={() => onSetCompany(isActive ? null : company)}
                  className={`
                    w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs
                    transition-all border
                    ${isActive
                      ? "bg-gradient-to-r from-pink-500/20 to-violet-500/20 border-pink-500/20 text-pink-300 shadow-lg  shadow-pink-900/20"
                      : "bg-slate-900/40 border-white/5 text-slate-400 hover:border-pink-500/10 hover:bg-slate-800/60 hover:text-white"
                    }
                  `}
                >
                  <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                    isActive ? "bg-pink-400" : "bg-gray-600"
                  }`} />
                  {formatCompany(company)}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Empty state */}
      {availableDocTypes.length === 0 && availableCompanies.length === 0 && (
        <p className="text-xs italic text-slate-500">
          Upload documents to enable filters
        </p>
      )}
    </div>
  );
}