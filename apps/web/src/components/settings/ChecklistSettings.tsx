"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ChevronDown, ChevronUp, Loader2, Plus, Trash2 } from "lucide-react";

import { Input } from "@/components/ui/Input";
import { SortableList } from "@/components/ui/SortableList";
import {
  createChecklistItem,
  createChecklistTemplate,
  deleteChecklistItem,
  deleteChecklistTemplate,
  fetchChecklistItems,
  fetchChecklistTemplates,
  reorderChecklistItems,
  toggleChecklistTemplate,
} from "@/lib/api";
import type { ChecklistItem, ChecklistTemplate } from "@/lib/types";
import { cn } from "@/lib/cn";

export function ChecklistSettings() {
  const queryClient = useQueryClient();
  const [expanded, setExpanded] = useState<string | null>(null);
  const [newOpen, setNewOpen] = useState(false);
  const [name, setName] = useState("");

  const templatesQuery = useQuery({
    queryKey: ["checklist-templates"],
    queryFn: fetchChecklistTemplates,
  });

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["checklist-templates"] });

  const createMutation = useMutation({
    mutationFn: () => createChecklistTemplate({ name }),
    onSuccess: () => {
      invalidate();
      setNewOpen(false);
      setName("");
    },
  });

  const toggleMutation = useMutation({
    mutationFn: ({ id, enable }: { id: string; enable: boolean }) =>
      toggleChecklistTemplate(id, enable),
    onSuccess: invalidate,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteChecklistTemplate(id),
    onSuccess: invalidate,
  });

  const templates = templatesQuery.data ?? [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">مدیریت چک‌لیست‌ها</h2>
        <button
          onClick={() => setNewOpen((v) => !v)}
          className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-3 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          <Plus className="h-4 w-4" />
          قالب جدید
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
          <Input placeholder="نام قالب چک‌لیست" value={name} onChange={(e) => setName(e.target.value)} required />
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="shrink-0 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
          >
            ذخیره
          </button>
        </form>
      )}

      {templatesQuery.isLoading ? (
        <Loader2 className="mx-auto h-5 w-5 animate-spin text-slate-400" />
      ) : (
        <div className="space-y-2">
          {templates.map((template: ChecklistTemplate) => (
            <div key={template.id} className="rounded-xl border border-slate-200 bg-white p-3">
              <div className="flex items-center justify-between gap-2">
                <button
                  type="button"
                  onClick={() => setExpanded((prev) => (prev === template.id ? null : template.id))}
                  className="flex flex-1 items-center gap-2 text-right"
                >
                  {expanded === template.id ? (
                    <ChevronUp className="h-4 w-4 text-slate-400" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-slate-400" />
                  )}
                  <span className="font-medium text-slate-800">{template.name}</span>
                  {template.is_default && (
                    <span className="rounded-full bg-brand-50 px-2 py-0.5 text-[10px] text-brand-700">
                      پیش‌فرض
                    </span>
                  )}
                </button>
                <button
                  onClick={() =>
                    toggleMutation.mutate({ id: template.id, enable: !template.is_active })
                  }
                  className={cn(
                    "rounded-full px-2 py-0.5 text-xs font-medium",
                    template.is_active
                      ? "bg-emerald-50 text-emerald-700"
                      : "bg-slate-100 text-slate-500"
                  )}
                >
                  {template.is_active ? "فعال" : "غیرفعال"}
                </button>
                <button
                  onClick={() => {
                    if (window.confirm(`قالب «${template.name}» حذف شود؟`)) {
                      deleteMutation.mutate(template.id);
                    }
                  }}
                  className="text-slate-400 hover:text-red-500"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>

              {expanded === template.id && <ChecklistItemsManager templateId={template.id} />}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ChecklistItemsManager({ templateId }: { templateId: string }) {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [isRequired, setIsRequired] = useState(false);

  const itemsQuery = useQuery({
    queryKey: ["checklist-items", templateId],
    queryFn: () => fetchChecklistItems(templateId),
  });

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ["checklist-items", templateId] });

  const createMutation = useMutation({
    mutationFn: () => createChecklistItem({ template_id: templateId, title, is_required: isRequired }),
    onSuccess: () => {
      invalidate();
      setTitle("");
      setIsRequired(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteChecklistItem(id),
    onSuccess: invalidate,
    onError: (error: Error) => window.alert(`حذف آیتم ممکن نشد: ${error.message}`),
  });

  const reorderMutation = useMutation({
    mutationFn: (items: ChecklistItem[]) =>
      reorderChecklistItems(
        templateId,
        items.map((i, idx) => ({ id: i.id, sort_order: idx }))
      ),
    onSuccess: invalidate,
  });

  const items = (itemsQuery.data ?? []).slice().sort((a, b) => a.sort_order - b.sort_order);

  return (
    <div className="mt-3 space-y-2 border-r-2 border-slate-100 pr-4">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (title) createMutation.mutate();
        }}
        className="flex flex-wrap items-center gap-2"
      >
        <Input
          className="flex-1"
          placeholder="عنوان آیتم چک‌لیست"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <label className="flex items-center gap-1.5 text-xs text-slate-600">
          <input
            type="checkbox"
            checked={isRequired}
            onChange={(e) => setIsRequired(e.target.checked)}
            className="h-3.5 w-3.5 rounded border-slate-300"
          />
          الزامی
        </label>
        <button
          type="submit"
          className="rounded-lg bg-brand-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-brand-700"
        >
          افزودن
        </button>
      </form>

      {itemsQuery.isLoading ? (
        <Loader2 className="h-4 w-4 animate-spin text-slate-400" />
      ) : items.length === 0 ? (
        <p className="text-xs text-slate-400">آیتمی ثبت نشده</p>
      ) : (
        <SortableList
          items={items}
          onReorder={(next) => reorderMutation.mutate(next)}
          renderItem={(item) => (
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs text-slate-700">
                {item.title}
                {item.is_required && <span className="mr-1 text-red-500">*</span>}
              </span>
              <button
                onClick={() => {
                  if (window.confirm(`آیتم «${item.title}» حذف شود؟`)) deleteMutation.mutate(item.id);
                }}
                className="text-slate-400 hover:text-red-500"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </div>
          )}
        />
      )}
    </div>
  );
}
