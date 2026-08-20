"use client";

import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, ListChecks, Loader2, Pencil, Save, TriangleAlert } from "lucide-react";

import { Input } from "@/components/ui/Input";
import {
  assignDefaultChecklist,
  fetchChecklistItems,
  fetchChecklistTemplates,
  fetchTradeChecklist,
  updateTradeChecklist,
} from "@/lib/api";
import type { ChecklistAnswerInput } from "@/lib/types";
import { cn } from "@/lib/cn";

interface DisplayItem {
  id: string;
  title: string;
  description: string | null;
  is_required: boolean;
  is_active: boolean;
  sort_order: number;
}

interface ChecklistCardProps {
  tradeId: string;
  /** در حالت «detail» پیش‌فرض فقط‌خواندنی است و با دکمه ویرایش باز می‌شود */
  variant?: "form" | "detail";
}

export function ChecklistCard({ tradeId, variant = "form" }: ChecklistCardProps) {
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(variant === "form");
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>("");
  const [localAnswers, setLocalAnswers] = useState<Record<string, ChecklistAnswerInput>>({});

  const checklistQuery = useQuery({
    queryKey: ["trade-checklist", tradeId],
    queryFn: () => fetchTradeChecklist(tradeId),
  });
  const templatesQuery = useQuery({
    queryKey: ["checklist-templates-for-trade"],
    queryFn: fetchChecklistTemplates,
    enabled: editing,
  });

  const checklist = checklistQuery.data;
  const assignedTemplateId = checklist?.checklist_template_id ?? "";
  const isViewingAssignedTemplate = selectedTemplateId === assignedTemplateId;

  // پاسخ‌های ذخیره‌شده قالب فعلاً اختصاص‌یافته را در state محلی لود می‌کند
  useEffect(() => {
    if (checklist) {
      setSelectedTemplateId(checklist.checklist_template_id ?? "");
      const initial: Record<string, ChecklistAnswerInput> = {};
      checklist.items.forEach((item) => {
        initial[item.id] = { item_id: item.id, checked: item.checked, note: item.note };
      });
      setLocalAnswers(initial);
    }
  }, [checklist]);

  // اگر کاربر قالب دیگری (غیر از قالب فعلاً اختصاص‌یافته) را انتخاب کند،
  // آیتم‌های همان قالب را برای پیش‌نمایش/پاسخ‌دهی زنده واکشی می‌کنیم
  const previewItemsQuery = useQuery({
    queryKey: ["checklist-template-items-preview", selectedTemplateId],
    queryFn: () => fetchChecklistItems(selectedTemplateId),
    enabled: editing && Boolean(selectedTemplateId) && !isViewingAssignedTemplate,
  });

  function handleTemplateChange(newId: string) {
    setSelectedTemplateId(newId);
    if (newId === assignedTemplateId) {
      const initial: Record<string, ChecklistAnswerInput> = {};
      checklist?.items.forEach((item) => {
        initial[item.id] = { item_id: item.id, checked: item.checked, note: item.note };
      });
      setLocalAnswers(initial);
    } else {
      setLocalAnswers({});
    }
  }

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["trade-checklist", tradeId] });
    queryClient.invalidateQueries({ queryKey: ["trade-detail", tradeId] });
    queryClient.invalidateQueries({ queryKey: ["trades"] });
  };

  const saveMutation = useMutation({
    mutationFn: () =>
      updateTradeChecklist(tradeId, {
        checklist_template_id: selectedTemplateId || null,
        answers: Object.values(localAnswers),
      }),
    onSuccess: () => {
      invalidate();
      if (variant === "detail") setEditing(false);
    },
  });

  const assignDefaultMutation = useMutation({
    mutationFn: () => assignDefaultChecklist(tradeId),
    onSuccess: (data) => {
      setSelectedTemplateId(data.checklist_template_id ?? "");
      invalidate();
    },
  });

  function toggleItem(itemId: string, checked: boolean) {
    setLocalAnswers((prev) => ({
      ...prev,
      [itemId]: { item_id: itemId, checked, note: prev[itemId]?.note ?? null },
    }));
  }

  function setNote(itemId: string, note: string) {
    setLocalAnswers((prev) => ({
      ...prev,
      [itemId]: { item_id: itemId, checked: prev[itemId]?.checked ?? false, note },
    }));
  }

  const displayItems: DisplayItem[] = useMemo(() => {
    if (isViewingAssignedTemplate) {
      return (checklist?.items ?? []).map((i) => ({
        id: i.id,
        title: i.title,
        description: i.description,
        is_required: i.is_required,
        is_active: i.is_active,
        sort_order: i.sort_order,
      }));
    }
    return (previewItemsQuery.data ?? [])
      .filter((i) => i.is_active)
      .map((i) => ({
        id: i.id,
        title: i.title,
        description: i.description,
        is_required: i.is_required,
        is_active: true,
        sort_order: i.sort_order,
      }));
  }, [isViewingAssignedTemplate, checklist, previewItemsQuery.data]);

  const liveStats = useMemo(() => {
    const active = displayItems.filter((i) => i.is_active);
    const checkedCount = active.filter((i) => localAnswers[i.id]?.checked).length;
    const total = active.length;
    const score = total > 0 ? Math.round((checkedCount / total) * 10000) / 100 : null;
    const requiredActive = active.filter((i) => i.is_required);
    const missing = requiredActive.filter((i) => !localAnswers[i.id]?.checked).map((i) => i.title);
    return { score, total, checkedCount, missing };
  }, [displayItems, localAnswers]);

  if (checklistQuery.isLoading) {
    return (
      <div className="flex justify-center py-6 text-slate-400">
        <Loader2 className="h-5 w-5 animate-spin" />
      </div>
    );
  }

  const templates = (templatesQuery.data ?? []).filter((t) => t.is_active);
  const defaultTemplate = templates.find((t) => t.is_default);
  const hasAssignedTemplate = Boolean(assignedTemplateId);

  // --- حالت فقط‌خواندنی (مودال جزئیات، پیش از کلیک روی ویرایش) --------------------
  if (variant === "detail" && !editing) {
    if (!hasAssignedTemplate) {
      return (
        <div className="rounded-xl border border-dashed border-slate-300 p-4 text-center text-sm text-slate-400">
          هیچ چک‌لیستی انتخاب نشده است.
        </div>
      );
    }
    return (
      <div className="space-y-3 rounded-xl border border-slate-200 bg-white p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ListChecks className="h-4 w-4 text-brand-500" />
            <span className="font-medium text-slate-800">{checklist?.checklist_template_title}</span>
          </div>
          <button
            type="button"
            onClick={() => setEditing(true)}
            className="flex items-center gap-1 text-xs text-brand-600 hover:underline"
          >
            <Pencil className="h-3.5 w-3.5" />
            ویرایش
          </button>
        </div>

        <ScoreBar
          score={checklist?.score_percent ?? null}
          missing={checklist?.required_missing_items ?? []}
        />

        <div className="space-y-1.5">
          {checklist?.items.map((item) => (
            <div key={item.id} className="flex items-start gap-2 text-sm">
              <CheckCircle2
                className={cn("mt-0.5 h-4 w-4 shrink-0", item.checked ? "text-emerald-500" : "text-slate-300")}
              />
              <div className="flex-1">
                <span className={item.checked ? "text-slate-800" : "text-slate-500"}>
                  {item.title}
                  {item.is_required && <span className="mr-1 text-red-500">*</span>}
                  {!item.is_active && (
                    <span className="mr-1 rounded bg-slate-100 px-1 text-[10px] text-slate-400">
                      غیرفعال
                    </span>
                  )}
                </span>
                {item.note && <p className="text-xs text-slate-400">{item.note}</p>}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // --- حالت ویرایش (فرم ثبت معامله، یا حالت ویرایش مودال جزئیات) -------------------
  return (
    <div className="space-y-3 rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex items-center gap-2">
        <ListChecks className="h-4 w-4 text-brand-500" />
        <span className="font-medium text-slate-800">چک‌لیست معامله</span>
      </div>

      {!hasAssignedTemplate && !selectedTemplateId && (
        <div className="space-y-2 rounded-lg bg-slate-50 p-3">
          <p className="text-sm text-slate-500">هیچ چک‌لیستی انتخاب نشده است.</p>
          {defaultTemplate && (
            <button
              type="button"
              onClick={() => assignDefaultMutation.mutate()}
              className="text-xs text-brand-600 hover:underline"
            >
              استفاده از قالب پیش‌فرض «{defaultTemplate.name}»
            </button>
          )}
        </div>
      )}

      <select
        className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
        value={selectedTemplateId}
        onChange={(e) => handleTemplateChange(e.target.value)}
      >
        <option value="">— انتخاب قالب چک‌لیست —</option>
        {templates.map((t) => (
          <option key={t.id} value={t.id}>
            {t.name}
            {t.is_default ? " (پیش‌فرض)" : ""}
          </option>
        ))}
      </select>

      {selectedTemplateId && (previewItemsQuery.isLoading ? (
        <Loader2 className="h-4 w-4 animate-spin text-slate-400" />
      ) : (
        <>
          <ScoreBar score={liveStats.score} missing={liveStats.missing} />
          <div className="space-y-2">
            {displayItems.map((item) => {
              const answer = localAnswers[item.id];
              return (
                <div key={item.id} className="rounded-lg border border-slate-100 p-2.5">
                  <label className="flex items-start gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={answer?.checked ?? false}
                      onChange={(e) => toggleItem(item.id, e.target.checked)}
                      className="mt-0.5 h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500"
                    />
                    <span className="flex-1 text-slate-700">
                      {item.title}
                      {item.is_required && <span className="mr-1 text-red-500">*</span>}
                    </span>
                  </label>
                  <Input
                    className="mt-2 text-xs"
                    placeholder="یادداشت (اختیاری)"
                    value={answer?.note ?? ""}
                    onChange={(e) => setNote(item.id, e.target.value)}
                  />
                </div>
              );
            })}
          </div>
        </>
      ))}

      <div className="flex justify-end gap-2">
        {variant === "detail" && (
          <button
            type="button"
            onClick={() => setEditing(false)}
            className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-50"
          >
            انصراف
          </button>
        )}
        <button
          type="button"
          onClick={() => saveMutation.mutate()}
          disabled={saveMutation.isPending || !selectedTemplateId}
          className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {saveMutation.isPending ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Save className="h-3.5 w-3.5" />
          )}
          ذخیره چک‌لیست
        </button>
      </div>

      {saveMutation.isError && (
        <p className="text-xs text-red-500">{(saveMutation.error as Error).message}</p>
      )}
    </div>
  );
}

function ScoreBar({ score, missing }: { score: number | null; missing: string[] }) {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span>امتیاز رعایت چک‌لیست</span>
        <span className="font-ltr font-medium text-slate-700">
          {score === null ? "—" : `${score}٪`}
        </span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
        <div
          className={cn(
            "h-full rounded-full transition-all",
            score !== null && score >= 70 ? "bg-emerald-500" : "bg-amber-500"
          )}
          style={{ width: `${score ?? 0}%` }}
        />
      </div>
      {missing.length > 0 && (
        <div className="flex items-start gap-1.5 rounded-lg bg-amber-50 px-2.5 py-1.5 text-xs text-amber-700">
          <TriangleAlert className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          <span>موارد الزامی جامانده: {missing.join("، ")}</span>
        </div>
      )}
    </div>
  );
}
