"use client";

import { useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  ClipboardList,
  LayoutGrid,
  ListChecks,
  Palette,
  Settings,
  SlidersHorizontal,
  Wallet,
} from "lucide-react";

import { GeneralSettings } from "@/components/settings/GeneralSettings";
import { AccountsSettings } from "@/components/settings/AccountsSettings";
import { SymbolsSettings } from "@/components/settings/SymbolsSettings";
import { FieldManagerSettings } from "@/components/settings/FieldManagerSettings";
import { ChecklistSettings } from "@/components/settings/ChecklistSettings";
import { ThemeSettingsPanel } from "@/components/settings/ThemeSettingsPanel";
import { TabsSettings } from "@/components/settings/TabsSettings";
import { cn } from "@/lib/cn";

const SECTIONS = [
  { key: "general", label: "عمومی", icon: Settings, Component: GeneralSettings },
  { key: "accounts", label: "حساب‌ها", icon: Wallet, Component: AccountsSettings },
  { key: "symbols", label: "نمادها", icon: LayoutGrid, Component: SymbolsSettings },
  { key: "fields", label: "مدیریت فیلدها", icon: SlidersHorizontal, Component: FieldManagerSettings },
  { key: "checklist", label: "چک‌لیست‌ها", icon: ListChecks, Component: ChecklistSettings },
  { key: "theme", label: "ظاهر و تم", icon: Palette, Component: ThemeSettingsPanel },
  { key: "tabs", label: "تب‌های سایدبار", icon: ClipboardList, Component: TabsSettings },
] as const;

export default function SettingsPage() {
  const [active, setActive] = useState<(typeof SECTIONS)[number]["key"]>("general");
  const ActiveComponent = SECTIONS.find((s) => s.key === active)?.Component ?? GeneralSettings;

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">تنظیمات</h1>
          <p className="text-sm text-slate-500">مدیریت حساب‌ها، فیلدهای پویا، چک‌لیست و ظاهر برنامه</p>
        </div>
        <Link
          href="/trades"
          className="flex items-center gap-2 rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-600 hover:bg-slate-50"
        >
          بازگشت به ژورنال
          <ArrowRight className="h-4 w-4" />
        </Link>
      </header>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-[220px_1fr]">
        <nav className="flex gap-1.5 overflow-x-auto md:flex-col md:overflow-visible">
          {SECTIONS.map((section) => {
            const Icon = section.icon;
            return (
              <button
                key={section.key}
                onClick={() => setActive(section.key)}
                className={cn(
                  "flex shrink-0 items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition",
                  active === section.key
                    ? "bg-brand-50 text-brand-700"
                    : "text-slate-600 hover:bg-slate-100"
                )}
              >
                <Icon className="h-4 w-4" />
                {section.label}
              </button>
            );
          })}
        </nav>

        <div className="min-w-0">
          <ActiveComponent />
        </div>
      </div>
    </main>
  );
}
