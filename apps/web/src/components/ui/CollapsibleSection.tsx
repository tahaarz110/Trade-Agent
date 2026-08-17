"use client";

import { useState, type ReactNode } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/cn";

interface CollapsibleSectionProps {
  title: string;
  description?: string | null;
  defaultOpen?: boolean;
  children: ReactNode;
  badge?: ReactNode;
}

export function CollapsibleSection({
  title,
  description,
  defaultOpen = true,
  children,
  badge,
}: CollapsibleSectionProps) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between gap-3 px-4 py-3 text-right hover:bg-slate-50"
      >
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-900">{title}</span>
          {badge}
        </div>
        <ChevronDown
          className={cn(
            "h-4 w-4 shrink-0 text-slate-400 transition-transform",
            open && "rotate-180"
          )}
        />
      </button>
      {description && open && (
        <p className="border-t border-slate-100 px-4 pt-2 text-xs text-slate-500">
          {description}
        </p>
      )}
      {open && <div className="space-y-4 px-4 py-4">{children}</div>}
    </div>
  );
}
