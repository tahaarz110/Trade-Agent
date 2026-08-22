"use client";

import { useMemo, useState } from "react";
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  createColumnHelper,
} from "@tanstack/react-table";
import { useQuery } from "@tanstack/react-query";
import { ChevronLeft, ChevronRight, Loader2 } from "lucide-react";

import { fetchAllAccounts, fetchAllSymbols, fetchTrades, type TradeListFilters } from "@/lib/api";
import type { Trade } from "@/lib/types";
import { SearchableSelect } from "@/components/ui/SearchableSelect";
import { cn } from "@/lib/cn";

const columnHelper = createColumnHelper<Trade>();

interface TradesTableProps {
  onRowClick: (trade: Trade) => void;
}

export function TradesTable({ onRowClick }: TradesTableProps) {
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [filters, setFilters] = useState<TradeListFilters>({});

  const accountsQuery = useQuery({ queryKey: ["accounts-all"], queryFn: fetchAllAccounts });
  const symbolsQuery = useQuery({ queryKey: ["symbols-all"], queryFn: fetchAllSymbols });

  const tradesQuery = useQuery({
    queryKey: ["trades", page, pageSize, filters],
    queryFn: () => fetchTrades(page, pageSize, filters),
  });

  const symbolNameById = useMemo(() => {
    const map = new Map<string, string>();
    symbolsQuery.data?.forEach((s) => map.set(s.id, s.name));
    return map;
  }, [symbolsQuery.data]);

  const accountNameById = useMemo(() => {
    const map = new Map<string, string>();
    accountsQuery.data?.forEach((a) => map.set(a.id, a.name));
    return map;
  }, [accountsQuery.data]);

  const columns = useMemo(
    () => [
      columnHelper.accessor("entry_time", {
        header: "تاریخ ورود",
        cell: (info) => (
          <span className="font-ltr text-xs text-slate-500">
            {new Date(info.getValue()).toLocaleString("fa-IR")}
          </span>
        ),
      }),
      columnHelper.accessor("symbol_id", {
        header: "نماد",
        cell: (info) => (
          <span className="font-ltr font-medium">
            {symbolNameById.get(info.getValue()) ?? "—"}
          </span>
        ),
      }),
      columnHelper.accessor("account_id", {
        header: "حساب",
        cell: (info) => accountNameById.get(info.getValue()) ?? "—",
      }),
      columnHelper.accessor("direction", {
        header: "جهت",
        cell: (info) => (
          <span
            className={cn(
              "rounded-full px-2 py-0.5 text-xs font-medium",
              info.getValue() === "buy"
                ? "bg-emerald-50 text-emerald-700"
                : "bg-rose-50 text-rose-700"
            )}
          >
            {info.getValue() === "buy" ? "خرید" : "فروش"}
          </span>
        ),
      }),
      columnHelper.accessor("status", {
        header: "وضعیت",
        cell: (info) => {
          const label =
            info.getValue() === "open" ? "باز" : info.getValue() === "closed" ? "بسته" : "لغوشده";
          return <span className="text-xs text-slate-600">{label}</span>;
        },
      }),
      columnHelper.accessor("entry_price", {
        header: "قیمت ورود",
        cell: (info) => <span className="font-ltr">{info.getValue()}</span>,
      }),
      columnHelper.accessor("net_profit", {
        header: "سود/زیان خالص",
        cell: (info) => {
          const raw = info.getValue();
          if (raw == null) return <span className="text-slate-400">—</span>;
          const v = Number(raw);
          return (
            <span className={cn("font-ltr font-medium", v >= 0 ? "text-emerald-600" : "text-rose-600")}>
              {raw}
            </span>
          );
        },
      }),
      columnHelper.accessor("r_multiple", {
        header: "R",
        cell: (info) => (
          <span className="font-ltr text-slate-600">{info.getValue() ?? "—"}</span>
        ),
      }),
    ],
    [symbolNameById, accountNameById]
  );

  const table = useReactTable({
    data: tradesQuery.data?.items ?? [],
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  const totalPages = tradesQuery.data?.total_pages ?? 1;

  function updateFilter<K extends keyof TradeListFilters>(key: K, value: string) {
    setPage(1);
    setFilters((prev) => ({ ...prev, [key]: value || undefined }));
  }

  return (
    <div className="space-y-3">
      {/* --- فیلترها ------------------------------------------------------- */}
      <div className="flex flex-wrap items-center gap-2 rounded-xl border border-slate-200 bg-white p-3">
        <div className="w-48">
          <SearchableSelect
            value={filters.account_id ?? null}
            onChange={(v) => updateFilter("account_id", (v as string) ?? "")}
            options={(accountsQuery.data ?? []).map((a) => ({ value: a.id, label: a.name }))}
            placeholder="فیلتر بر اساس حساب"
          />
        </div>
        <div className="w-48">
          <SearchableSelect
            value={filters.symbol_id ?? null}
            onChange={(v) => updateFilter("symbol_id", (v as string) ?? "")}
            options={(symbolsQuery.data ?? []).map((s) => ({ value: s.id, label: s.name }))}
            placeholder="فیلتر بر اساس نماد"
          />
        </div>
        <select
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
          value={filters.direction ?? ""}
          onChange={(e) => updateFilter("direction", e.target.value)}
        >
          <option value="">همه جهت‌ها</option>
          <option value="buy">خرید</option>
          <option value="sell">فروش</option>
        </select>
        <select
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
          value={filters.status ?? ""}
          onChange={(e) => updateFilter("status", e.target.value)}
        >
          <option value="">همه وضعیت‌ها</option>
          <option value="open">باز</option>
          <option value="closed">بسته</option>
          <option value="cancelled">لغوشده</option>
        </select>
        <input
          type="date"
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-ltr"
          value={filters.date_from ?? ""}
          onChange={(e) => updateFilter("date_from", e.target.value)}
        />
        <span className="text-xs text-slate-400">تا</span>
        <input
          type="date"
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-ltr"
          value={filters.date_to ?? ""}
          onChange={(e) => updateFilter("date_to", e.target.value)}
        />
      </div>

      {/* --- جدول ------------------------------------------------------------ */}
      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
        <table className="w-full text-sm">
          <thead className="border-b border-slate-100 bg-slate-50">
            {table.getHeaderGroups().map((hg) => (
              <tr key={hg.id}>
                {hg.headers.map((header) => (
                  <th key={header.id} className="px-4 py-3 text-right font-medium text-slate-500">
                    {flexRender(header.column.columnDef.header, header.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {tradesQuery.isLoading && (
              <tr>
                <td colSpan={columns.length} className="py-12 text-center text-slate-400">
                  <Loader2 className="mx-auto h-5 w-5 animate-spin" />
                </td>
              </tr>
            )}
            {!tradesQuery.isLoading && (tradesQuery.data?.items.length ?? 0) === 0 && (
              <tr>
                <td colSpan={columns.length} className="py-12 text-center text-slate-400">
                  معامله‌ای یافت نشد
                </td>
              </tr>
            )}
            {table.getRowModel().rows.map((row) => (
              <tr
                key={row.id}
                onClick={() => onRowClick(row.original)}
                className="cursor-pointer border-b border-slate-50 last:border-0 hover:bg-slate-50"
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-4 py-3">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* --- صفحه‌بندی --------------------------------------------------------- */}
      <div className="flex items-center justify-between text-sm text-slate-500">
        <span>
          {tradesQuery.data?.total ?? 0} معامله — صفحه {page} از {totalPages}
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
            className="rounded-lg border border-slate-300 p-2 disabled:opacity-40"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
            className="rounded-lg border border-slate-300 p-2 disabled:opacity-40"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
