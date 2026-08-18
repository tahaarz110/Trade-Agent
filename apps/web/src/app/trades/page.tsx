"use client";

import { useState } from "react";
import Link from "next/link";
import { Plus, Settings } from "lucide-react";

import { Modal } from "@/components/ui/Modal";
import { DynamicTradeForm } from "@/components/trade-form/DynamicTradeForm";
import { TradesTable } from "@/components/trades-table/TradesTable";
import { TradeDetailModal } from "@/components/trade-detail/TradeDetailModal";
import type { Trade } from "@/lib/types";

export default function TradesPage() {
  const [createOpen, setCreateOpen] = useState(false);
  const [selectedTrade, setSelectedTrade] = useState<Trade | null>(null);

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">ژورنال معاملات</h1>
          <p className="text-sm text-slate-500">تاریخچه، فیلتر و ثبت معاملات جدید</p>
        </div>
        <button
          onClick={() => setCreateOpen(true)}
          className="flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-brand-700"
        >
          <Plus className="h-4 w-4" />
          معامله جدید
        </button>
      </header>

      <div className="mb-4 flex justify-end">
        <Link
          href="/settings"
          className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-brand-600"
        >
          <Settings className="h-4 w-4" />
          تنظیمات
        </Link>
      </div>

      <TradesTable onRowClick={(trade) => setSelectedTrade(trade)} />

      <Modal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        title="ثبت معامله جدید"
        widthClassName="max-w-3xl"
      >
        <DynamicTradeForm
          onSuccess={() => {
            setCreateOpen(false);
          }}
        />
      </Modal>

      <TradeDetailModal tradeId={selectedTrade?.id ?? null} onClose={() => setSelectedTrade(null)} />
    </main>
  );
}
