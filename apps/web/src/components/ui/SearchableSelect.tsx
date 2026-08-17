"use client";

import { useMemo, useRef, useState } from "react";
import { ChevronDown, Search, X } from "lucide-react";
import { cn } from "@/lib/cn";

export interface SearchableOption {
  value: string;
  label: string;
  color?: string | null;
}

interface SearchableSelectProps {
  options: SearchableOption[];
  value: string | string[] | null;
  onChange: (value: string | string[] | null) => void;
  multiple?: boolean;
  placeholder?: string;
  error?: string;
  disabled?: boolean;
}

export function SearchableSelect({
  options,
  value,
  onChange,
  multiple = false,
  placeholder = "انتخاب کنید...",
  error,
  disabled,
}: SearchableSelectProps) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const containerRef = useRef<HTMLDivElement>(null);

  const selectedValues = useMemo<string[]>(() => {
    if (!value) return [];
    return Array.isArray(value) ? value : [value];
  }, [value]);

  const filtered = useMemo(
    () =>
      options.filter((opt) =>
        opt.label.toLowerCase().includes(query.trim().toLowerCase())
      ),
    [options, query]
  );

  function toggleValue(optionValue: string) {
    if (multiple) {
      const next = selectedValues.includes(optionValue)
        ? selectedValues.filter((v) => v !== optionValue)
        : [...selectedValues, optionValue];
      onChange(next.length ? next : null);
    } else {
      onChange(optionValue);
      setOpen(false);
      setQuery("");
    }
  }

  const selectedLabels = options
    .filter((o) => selectedValues.includes(o.value))
    .map((o) => o.label);

  return (
    <div className="relative" ref={containerRef}>
      <button
        type="button"
        disabled={disabled}
        onClick={() => setOpen((v) => !v)}
        className={cn(
          "flex w-full items-center justify-between gap-2 rounded-lg border bg-white px-3 py-2 text-sm shadow-sm outline-none transition",
          "focus:border-brand-500 focus:ring-2 focus:ring-brand-100",
          error ? "border-red-400" : "border-slate-300",
          disabled && "cursor-not-allowed bg-slate-50 text-slate-400"
        )}
      >
        <span
          className={cn(
            "truncate text-right",
            selectedLabels.length === 0 && "text-slate-400"
          )}
        >
          {selectedLabels.length > 0 ? selectedLabels.join("، ") : placeholder}
        </span>
        <ChevronDown className="h-4 w-4 shrink-0 text-slate-400" />
      </button>

      {open && !disabled && (
        <div className="absolute z-20 mt-1 w-full rounded-lg border border-slate-200 bg-white shadow-lg">
          <div className="flex items-center gap-2 border-b border-slate-100 px-3 py-2">
            <Search className="h-4 w-4 text-slate-400" />
            <input
              autoFocus
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="جست‌وجو..."
              className="w-full text-sm outline-none placeholder:text-slate-400"
            />
            {query && (
              <button type="button" onClick={() => setQuery("")}>
                <X className="h-3.5 w-3.5 text-slate-400" />
              </button>
            )}
          </div>
          <ul className="max-h-56 overflow-y-auto py-1">
            {filtered.length === 0 && (
              <li className="px-3 py-2 text-sm text-slate-400">موردی یافت نشد</li>
            )}
            {filtered.map((opt) => {
              const isSelected = selectedValues.includes(opt.value);
              return (
                <li key={opt.value}>
                  <button
                    type="button"
                    onClick={() => toggleValue(opt.value)}
                    className={cn(
                      "flex w-full items-center gap-2 px-3 py-2 text-sm text-right hover:bg-brand-50",
                      isSelected && "bg-brand-50 font-medium text-brand-700"
                    )}
                  >
                    {opt.color && (
                      <span
                        className="h-2 w-2 shrink-0 rounded-full"
                        style={{ backgroundColor: opt.color }}
                      />
                    )}
                    <span className="flex-1">{opt.label}</span>
                    {isSelected && <span className="text-brand-500">✓</span>}
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {open && (
        <div
          className="fixed inset-0 z-10"
          onClick={() => {
            setOpen(false);
            setQuery("");
          }}
        />
      )}
    </div>
  );
}
