"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2, Plus, Trash2 } from "lucide-react";

import { Input } from "@/components/ui/Input";
import {
  createAccount,
  deleteAccount,
  fetchAccounts,
  updateAccount,
} from "@/lib/api";
import type { Account, AccountType } from "@/lib/types";

const ACCOUNT_TYPE_LABELS: Record<AccountType, string> = {
  demo: "دمو",
  real: "واقعی",
  prop: "پراپ",
};

export function AccountsSettings() {
  const queryClient = useQueryClient();
  const accountsQuery = useQuery({ queryKey: ["accounts"], queryFn: () => fetchAccounts() });
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [accountType, setAccountType] = useState<AccountType>("demo");
  const [currency, setCurrency] = useState("USD");
  const [initialBalance, setInitialBalance] = useState("");

  const createMutation = useMutation({
    mutationFn: () =>
      createAccount({
        name,
        account_type: accountType,
        currency,
        initial_balance: initialBalance ? Number(initialBalance) : null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
      setShowForm(false);
      setName("");
      setInitialBalance("");
    },
  });

  const toggleActiveMutation = useMutation({
    mutationFn: ({ id, isActive }: { id: string; isActive: boolean }) =>
      updateAccount(id, { is_active: isActive }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["accounts"] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteAccount(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["accounts"] }),
    onError: (error: Error) => window.alert(`حذف حساب ممکن نشد: ${error.message}`),
  });

  const accounts = accountsQuery.data?.items ?? [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">مدیریت حساب‌ها</h2>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-3 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          <Plus className="h-4 w-4" />
          حساب جدید
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            createMutation.mutate();
          }}
          className="grid grid-cols-1 gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 sm:grid-cols-4"
        >
          <Input
            placeholder="نام حساب"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <select
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
            value={accountType}
            onChange={(e) => setAccountType(e.target.value as AccountType)}
          >
            <option value="demo">دمو</option>
            <option value="real">واقعی</option>
            <option value="prop">پراپ</option>
          </select>
          <Input
            ltr
            placeholder="ارز (USD)"
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
          />
          <Input
            ltr
            type="number"
            step="any"
            placeholder="موجودی اولیه"
            value={initialBalance}
            onChange={(e) => setInitialBalance(e.target.value)}
          />
          <div className="sm:col-span-4">
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
            >
              {createMutation.isPending ? "در حال ذخیره..." : "ذخیره حساب"}
            </button>
          </div>
        </form>
      )}

      <div className="overflow-hidden rounded-xl border border-slate-200">
        <table className="w-full text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-2 text-right font-medium text-slate-500">نام</th>
              <th className="px-4 py-2 text-right font-medium text-slate-500">نوع</th>
              <th className="px-4 py-2 text-right font-medium text-slate-500">ارز</th>
              <th className="px-4 py-2 text-right font-medium text-slate-500">وضعیت</th>
              <th className="px-4 py-2"></th>
            </tr>
          </thead>
          <tbody>
            {accountsQuery.isLoading && (
              <tr>
                <td colSpan={5} className="py-8 text-center text-slate-400">
                  <Loader2 className="mx-auto h-4 w-4 animate-spin" />
                </td>
              </tr>
            )}
            {accounts.map((account: Account) => (
              <tr key={account.id} className="border-t border-slate-100">
                <td className="px-4 py-2.5 font-medium text-slate-800">{account.name}</td>
                <td className="px-4 py-2.5 text-slate-600">
                  {ACCOUNT_TYPE_LABELS[account.account_type]}
                </td>
                <td className="px-4 py-2.5 font-ltr text-slate-600">{account.currency}</td>
                <td className="px-4 py-2.5">
                  <button
                    onClick={() =>
                      toggleActiveMutation.mutate({ id: account.id, isActive: !account.is_active })
                    }
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                      account.is_active
                        ? "bg-emerald-50 text-emerald-700"
                        : "bg-slate-100 text-slate-500"
                    }`}
                  >
                    {account.is_active ? "فعال" : "غیرفعال"}
                  </button>
                </td>
                <td className="px-4 py-2.5 text-left">
                  <button
                    onClick={() => {
                      if (window.confirm(`حساب «${account.name}» حذف شود؟`)) {
                        deleteMutation.mutate(account.id);
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
