"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2, Plus, Trash2 } from "lucide-react";

import { Input } from "@/components/ui/Input";
import { SortableList } from "@/components/ui/SortableList";
import { createUITab, deleteUITab, fetchUITabs, reorderUITabs, toggleUITab } from "@/lib/api";
import type { UITab } from "@/lib/types";
import { cn } from "@/lib/cn";

export function TabsSettings() {
  const queryClient = useQueryClient();
  const tabsQuery = useQuery({ queryKey: ["ui-tabs"], queryFn: fetchUITabs });
  const [newOpen, setNewOpen] = useState(false);
  const [key, setKey] = useState("");
  const [title, setTitle] = useState("");

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["ui-tabs"] });

  const createMutation = useMutation({
    mutationFn: () => createUITab({ key, title }),
    onSuccess: () => {
      invalidate();
      setNewOpen(false);
      setKey("");
      setTitle("");
    },
    onError: (error: Error) => window.alert(`ساخت تب ممکن نشد: ${error.message}`),
  });

  const toggleMutation = useMutation({
    mutationFn: ({ id, visible }: { id: string; visible: boolean }) => toggleUITab(id, visible),
    onSuccess: invalidate,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteUITab(id),
    onSuccess: invalidate,
  });

  const reorderMutation = useMutation({
    mutationFn: (items: UITab[]) => reorderUITabs(items.map((t, idx) => ({ id: t.id, sort_order: idx }))),
    onSuccess: invalidate,
  });

  const tabs = (tabsQuery.data ?? []).slice().sort((a, b) => a.sort_order - b.sort_order);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">مدیریت تب‌های سایدبار</h2>
        <button
          onClick={() => setNewOpen((v) => !v)}
          className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-3 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          <Plus className="h-4 w-4" />
          تب جدید
        </button>
      </div>

      {newOpen && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            createMutation.mutate();
          }}
          className="flex gap-2 rounded-xl border border-slate-200 bg-slate-50 p-4"
        >
          <Input ltr placeholder="کلید یکتا" value={key} onChange={(e) => setKey(e.target.value)} required />
          <Input placeholder="عنوان تب" value={title} onChange={(e) => setTitle(e.target.value)} required />
          <button
            type="submit"
            className="shrink-0 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
          >
            ذخیره
          </button>
        </form>
      )}

      {tabsQuery.isLoading ? (
        <Loader2 className="mx-auto h-5 w-5 animate-spin text-slate-400" />
      ) : (
        <SortableList
          items={tabs}
          onReorder={(items) => reorderMutation.mutate(items)}
          renderItem={(tab) => (
            <div className="flex items-center justify-between gap-2">
              <div>
                <span className="text-sm font-medium text-slate-800">{tab.title}</span>
                <span className="font-ltr mr-2 text-xs text-slate-400">({tab.key})</span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => toggleMutation.mutate({ id: tab.id, visible: !tab.is_visible })}
                  className={cn(
                    "rounded-full px-2 py-0.5 text-xs font-medium",
                    tab.is_visible ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-500"
                  )}
                >
                  {tab.is_visible ? "نمایان" : "مخفی"}
                </button>
                <button
                  onClick={() => {
                    if (window.confirm(`تب «${tab.title}» حذف شود؟`)) deleteMutation.mutate(tab.id);
                  }}
                  className="text-slate-400 hover:text-red-500"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}
        />
      )}
    </div>
  );
}
