"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2, Plus, Trash2 } from "lucide-react";

import { Input } from "@/components/ui/Input";
import { createSymbol, deleteSymbol, fetchSymbols, updateSymbol } from "@/lib/api";

export function SymbolsSettings() {
  const queryClient = useQueryClient();
  const symbolsQuery = useQuery({ queryKey: ["symbols"], queryFn: () => fetchSymbols() });
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [assetClass, setAssetClass] = useState("forex");

  const createMutation = useMutation({
    mutationFn: () =>
      createSymbol({ name: name.toUpperCase(), display_name: displayName || null, asset_class: assetClass }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["symbols"] });
      setShowForm(false);
      setName("");
      setDisplayName("");
    },
  });

  const toggleActiveMutation = useMutation({
    mutationFn: ({ id, isActive }: { id: string; isActive: boolean }) =>
      updateSymbol(id, { is_active: isActive }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["symbols"] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteSymbol(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["symbols"] }),
    onError: (error: Error) => window.alert(`حذف نماد ممکن نشد: ${error.message}`),
  });

  const symbols = symbolsQuery.data?.items ?? [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">مدیریت نمادها</h2>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-3 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          <Plus className="h-4 w-4" />
          نماد جدید
        </button>
      </div>

      {createMutation.isError && (
        <p className="text-sm text-red-500">{(createMutation.error as Error).message}</p>
      )}

      {showForm && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            createMutation.mutate();
          }}
          className="grid grid-cols-1 gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 sm:grid-cols-4"
        >
          <Input ltr placeholder="نماد (EURUSD)" value={name} onChange={(e) => setName(e.target.value)} required />
          <Input
            placeholder="نام نمایشی"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
          />
          <select
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
            value={assetClass}
            onChange={(e) => setAssetClass(e.target.value)}
          >
            <option value="forex">فارکس</option>
            <option value="crypto">ارز دیجیتال</option>
            <option value="indices">شاخص</option>
            <option value="commodities">کالا</option>
          </select>
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
          >
            {createMutation.isPending ? "در حال ذخیره..." : "ذخیره نماد"}
          </button>
        </form>
      )}

      <div className="overflow-hidden rounded-xl border border-slate-200">
        <table className="w-full text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-2 text-right font-medium text-slate-500">نماد</th>
              <th className="px-4 py-2 text-right font-medium text-slate-500">نام نمایشی</th>
              <th className="px-4 py-2 text-right font-medium text-slate-500">دسته</th>
              <th className="px-4 py-2 text-right font-medium text-slate-500">وضعیت</th>
              <th className="px-4 py-2"></th>
            </tr>
          </thead>
          <tbody>
            {symbolsQuery.isLoading && (
              <tr>
                <td colSpan={5} className="py-8 text-center text-slate-400">
                  <Loader2 className="mx-auto h-4 w-4 animate-spin" />
                </td>
              </tr>
            )}
            {symbols.map((symbol) => (
              <tr key={symbol.id} className="border-t border-slate-100">
                <td className="px-4 py-2.5 font-ltr font-medium text-slate-800">{symbol.name}</td>
                <td className="px-4 py-2.5 text-slate-600">{symbol.display_name ?? "—"}</td>
                <td className="px-4 py-2.5 text-slate-600">{symbol.asset_class ?? "—"}</td>
                <td className="px-4 py-2.5">
                  <button
                    onClick={() =>
                      toggleActiveMutation.mutate({ id: symbol.id, isActive: !symbol.is_active })
                    }
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                      symbol.is_active
                        ? "bg-emerald-50 text-emerald-700"
                        : "bg-slate-100 text-slate-500"
                    }`}
                  >
                    {symbol.is_active ? "فعال" : "غیرفعال"}
                  </button>
                </td>
                <td className="px-4 py-2.5 text-left">
                  <button
                    onClick={() => {
                      if (window.confirm(`نماد «${symbol.name}» حذف شود؟`)) {
                        deleteMutation.mutate(symbol.id);
                      }
                    }}
                    className="text-slate-400 hover:text-red-500"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
