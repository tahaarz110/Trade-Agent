"use client";

import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2, Save, Sparkles } from "lucide-react";

import { Input } from "@/components/ui/Input";
import { SearchableSelect } from "@/components/ui/SearchableSelect";
import { CollapsibleSection } from "@/components/ui/CollapsibleSection";
import { ImageDropzone } from "@/components/ui/ImageDropzone";
import { FieldRenderer } from "@/components/trade-form/FieldRenderer";
import { useDynamicFieldSchema } from "@/components/trade-form/useDynamicFieldSchema";
import {
  attachmentUrl,
  createTrade,
  deleteAttachment,
  fetchAccounts,
  fetchAttachments,
  fetchSymbols,
  fetchTradeDetail,
  fetchTrades,
  uploadAttachment,
  type TradeCreatePayload,
} from "@/lib/api";
import type { SectionWithFields } from "@/lib/types";

const CORE_SCHEMA = z.object({
  account_id: z.string().min(1, "انتخاب حساب الزامی است"),
  symbol_id: z.string().min(1, "انتخاب نماد الزامی است"),
  direction: z.enum(["buy", "sell"], { errorMap: () => ({ message: "جهت معامله را انتخاب کنید" }) }),
  entry_time: z.string().min(1, "زمان ورود الزامی است"),
  entry_price: z.string().min(1, "قیمت ورود الزامی است"),
  volume: z.string().min(1, "حجم معامله الزامی است"),
  stop_loss: z.string().optional().nullable(),
  take_profit: z.string().optional().nullable(),
  exit_price: z.string().optional().nullable(),
  exit_time: z.string().optional().nullable(),
});

function buildCustomFieldsSchema(sections: SectionWithFields[]) {
  const shape: Record<string, z.ZodTypeAny> = {};
  for (const section of sections) {
    for (const field of section.fields) {
      shape[field.slug] = field.is_required
        ? z
            .any()
            .refine((v) => v !== undefined && v !== null && v !== "", {
              message: `${field.title} الزامی است`,
            })
        : z.any().optional().nullable();
    }
  }
  return z.object(shape);
}

type CoreFormValues = z.infer<typeof CORE_SCHEMA> & {
  custom_fields: Record<string, unknown>;
};

const TEMPLATE_STORAGE_KEY = "trade-agent:quick-templates";

interface QuickTemplate {
  name: string;
  values: Partial<CoreFormValues>;
}

function loadTemplates(): QuickTemplate[] {
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(window.localStorage.getItem(TEMPLATE_STORAGE_KEY) ?? "[]");
  } catch {
    return [];
  }
}

function saveTemplates(templates: QuickTemplate[]) {
  window.localStorage.setItem(TEMPLATE_STORAGE_KEY, JSON.stringify(templates));
}

interface DynamicTradeFormProps {
  onSuccess?: (tradeId: string) => void;
}

export function DynamicTradeForm({ onSuccess }: DynamicTradeFormProps) {
  const { sections, isLoading: sectionsLoading } = useDynamicFieldSchema();

  const accountsQuery = useQuery({ queryKey: ["accounts"], queryFn: () => fetchAccounts() });
  const symbolsQuery = useQuery({ queryKey: ["symbols"], queryFn: () => fetchSymbols() });

  if (sectionsLoading || accountsQuery.isLoading || symbolsQuery.isLoading) {
    return (
      <div className="flex items-center justify-center py-16 text-slate-400">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    );
  }

  return (
    <TradeFormInner
      sections={sections}
      accounts={accountsQuery.data?.items ?? []}
      symbols={symbolsQuery.data?.items ?? []}
      onSuccess={onSuccess}
    />
  );
}

function TradeFormInner({
  sections,
  accounts,
  symbols,
  onSuccess,
}: {
  sections: SectionWithFields[];
  accounts: { id: string; name: string }[];
  symbols: { id: string; name: string; display_name: string | null }[];
  onSuccess?: (tradeId: string) => void;
}) {
  const queryClient = useQueryClient();
  const schema = useMemo(
    () => CORE_SCHEMA.extend({ custom_fields: buildCustomFieldsSchema(sections) }),
    [sections]
  );

  const {
    control,
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<CoreFormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      direction: "buy",
      entry_time: new Date().toISOString().slice(0, 16),
      custom_fields: {},
    },
  });

  const [pendingTradeId, setPendingTradeId] = useState<string | null>(null);
  const [pendingImages, setPendingImages] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [templates, setTemplates] = useState<QuickTemplate[]>([]);
  const [copyFrom, setCopyFrom] = useState("");

  useEffect(() => {
    setTemplates(loadTemplates());
  }, []);

  const selectedAccountId = watch("account_id");
  const recentTradesQuery = useQuery({
    queryKey: ["recent-trades-for-copy", selectedAccountId],
    queryFn: () => fetchTrades(1, 10, { account_id: selectedAccountId }),
    enabled: Boolean(selectedAccountId),
  });

  const attachmentsQuery = useQuery({
    queryKey: ["attachments", pendingTradeId],
    queryFn: () => fetchAttachments(pendingTradeId as string),
    enabled: Boolean(pendingTradeId),
  });

  const createMutation = useMutation({
    mutationFn: (payload: TradeCreatePayload) => createTrade(payload),
    onSuccess: async (trade) => {
      setPendingTradeId(trade.id);
      queryClient.invalidateQueries({ queryKey: ["trades"] });
      if (pendingImages.length) {
        setUploading(true);
        try {
          for (const file of pendingImages) {
            await uploadAttachment(trade.id, file);
          }
          setPendingImages([]);
          queryClient.invalidateQueries({ queryKey: ["attachments", trade.id] });
        } finally {
          setUploading(false);
        }
      }
      onSuccess?.(trade.id);
    },
  });

  async function onSubmit(values: CoreFormValues) {
    const payload: TradeCreatePayload = {
      account_id: values.account_id,
      symbol_id: values.symbol_id,
      direction: values.direction,
      entry_time: new Date(values.entry_time).toISOString(),
      entry_price: values.entry_price,
      volume: values.volume,
      stop_loss: values.stop_loss || null,
      take_profit: values.take_profit || null,
      exit_price: values.exit_price || null,
      exit_time: values.exit_time ? new Date(values.exit_time).toISOString() : null,
      custom_fields: values.custom_fields,
    };
    createMutation.mutate(payload);
  }

  async function handleUploadNow(files: File[]) {
    if (!pendingTradeId) {
      // معامله هنوز ثبت نشده؛ تصاویر برای بعد از ثبت نگه داشته می‌شوند
      setPendingImages((prev) => [...prev, ...files]);
      return;
    }
    setUploading(true);
    try {
      for (const file of files) {
        await uploadAttachment(pendingTradeId, file);
      }
      queryClient.invalidateQueries({ queryKey: ["attachments", pendingTradeId] });
    } finally {
      setUploading(false);
    }
  }

  async function handleRemoveImage(attachmentId: string) {
    await deleteAttachment(attachmentId);
    if (pendingTradeId) {
      queryClient.invalidateQueries({ queryKey: ["attachments", pendingTradeId] });
    }
  }

  function handleSaveTemplate() {
    const name = window.prompt("نام قالب سریع را وارد کنید:");
    if (!name) return;
    const values = {
      direction: watch("direction"),
      account_id: watch("account_id"),
      symbol_id: watch("symbol_id"),
      custom_fields: watch("custom_fields"),
    };
    const next = [...templates.filter((t) => t.name !== name), { name, values }];
    setTemplates(next);
    saveTemplates(next);
  }

  function handleApplyTemplate(name: string) {
    const tpl = templates.find((t) => t.name === name);
    if (!tpl) return;
    Object.entries(tpl.values).forEach(([key, value]) => {
      setValue(key as keyof CoreFormValues, value as never, { shouldValidate: true, shouldDirty: true });
    });
  }

  async function handleCopyFromPrevious(tradeId: string) {
    if (!tradeId) return;
    const detail = await fetchTradeDetail(tradeId);
    const customValues: Record<string, unknown> = {};
    detail.custom_fields.forEach((f) => {
      customValues[f.field_slug] = f.value;
    });
    reset({
      account_id: detail.account_id,
      symbol_id: detail.symbol_id,
      direction: detail.direction,
      entry_time: new Date().toISOString().slice(0, 16),
      entry_price: String(detail.entry_price),
      volume: String(detail.volume),
      stop_loss: detail.stop_loss != null ? String(detail.stop_loss) : "",
      take_profit: detail.take_profit != null ? String(detail.take_profit) : "",
      custom_fields: customValues,
    });
  }

  const symbolOptions = symbols.map((s) => ({
    value: s.id,
    label: s.display_name ? `${s.name} — ${s.display_name}` : s.name,
  }));

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
      {/* --- نوار ابزار قالب سریع / کپی از معامله قبلی ------------------- */}
      <div className="flex flex-wrap items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 p-3">
        <Sparkles className="h-4 w-4 text-brand-500" />
        <span className="text-xs font-medium text-slate-600">شروع سریع:</span>

        {templates.length > 0 && (
          <select
            className="rounded-lg border border-slate-300 bg-white px-2 py-1 text-xs"
            onChange={(e) => e.target.value && handleApplyTemplate(e.target.value)}
            defaultValue=""
          >
            <option value="" disabled>
              اعمال قالب ذخیره‌شده...
            </option>
            {templates.map((t) => (
              <option key={t.name} value={t.name}>
                {t.name}
              </option>
            ))}
          </select>
        )}

        <button
          type="button"
          onClick={handleSaveTemplate}
          className="rounded-lg border border-slate-300 bg-white px-2 py-1 text-xs text-slate-600 hover:bg-slate-100"
        >
          ذخیره به‌عنوان قالب
        </button>

        {selectedAccountId && (recentTradesQuery.data?.items.length ?? 0) > 0 && (
          <select
            className="rounded-lg border border-slate-300 bg-white px-2 py-1 text-xs"
            value={copyFrom}
            onChange={(e) => {
              setCopyFrom(e.target.value);
              handleCopyFromPrevious(e.target.value);
            }}
          >
            <option value="">کپی از معامله قبلی...</option>
            {recentTradesQuery.data?.items.map((t) => (
              <option key={t.id} value={t.id}>
                {t.direction === "buy" ? "خرید" : "فروش"} — {new Date(t.entry_time).toLocaleDateString("fa-IR")}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* --- اطلاعات اصلی معامله ------------------------------------------ */}
      <CollapsibleSection title="اطلاعات اصلی معامله" defaultOpen>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">
              حساب <span className="text-red-500">*</span>
            </label>
            <SearchableSelect
              value={watch("account_id") ?? null}
              onChange={(v) => setValue("account_id", (v as string) ?? "", { shouldValidate: true, shouldDirty: true })}
              options={accounts.map((a) => ({ value: a.id, label: a.name }))}
              placeholder="انتخاب حساب..."
              error={errors.account_id?.message}
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">
              نماد <span className="text-red-500">*</span>
            </label>
            <SearchableSelect
              value={watch("symbol_id") ?? null}
              onChange={(v) => setValue("symbol_id", (v as string) ?? "", { shouldValidate: true, shouldDirty: true })}
              options={symbolOptions}
              placeholder="انتخاب نماد..."
              error={errors.symbol_id?.message}
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">جهت معامله</label>
            <div className="flex gap-2">
              {(["buy", "sell"] as const).map((dir) => (
                <button
                  key={dir}
                  type="button"
                  onClick={() => setValue("direction", dir, { shouldValidate: true, shouldDirty: true })}
                  className={`flex-1 rounded-lg border px-3 py-2 text-sm font-medium transition ${
                    watch("direction") === dir
                      ? dir === "buy"
                        ? "border-emerald-500 bg-emerald-50 text-emerald-700"
                        : "border-rose-500 bg-rose-50 text-rose-700"
                      : "border-slate-300 text-slate-500 hover:bg-slate-50"
                  }`}
                >
                  {dir === "buy" ? "خرید (Buy)" : "فروش (Sell)"}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">
              زمان ورود <span className="text-red-500">*</span>
            </label>
            <Input ltr type="datetime-local" {...register("entry_time")} error={errors.entry_time?.message} />
            {errors.entry_time && <p className="mt-1 text-xs text-red-500">{errors.entry_time.message}</p>}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">
              قیمت ورود <span className="text-red-500">*</span>
            </label>
            <Input ltr type="number" step="any" {...register("entry_price")} error={errors.entry_price?.message} />
            {errors.entry_price && <p className="mt-1 text-xs text-red-500">{errors.entry_price.message}</p>}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">
              حجم <span className="text-red-500">*</span>
            </label>
            <Input ltr type="number" step="any" {...register("volume")} error={errors.volume?.message} />
            {errors.volume && <p className="mt-1 text-xs text-red-500">{errors.volume.message}</p>}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">حد ضرر</label>
            <Input ltr type="number" step="any" {...register("stop_loss")} />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">حد سود</label>
            <Input ltr type="number" step="any" {...register("take_profit")} />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">قیمت خروج</label>
            <Input ltr type="number" step="any" {...register("exit_price")} />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">زمان خروج</label>
            <Input ltr type="datetime-local" {...register("exit_time")} />
          </div>
        </div>
      </CollapsibleSection>

      {/* --- سکشن‌های داینامیک --------------------------------------------- */}
      {sections.map((section) => (
        <CollapsibleSection
          key={section.id}
          title={section.title}
          description={section.description}
          defaultOpen={section.key === "ict_market_structure"}
        >
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {section.fields.map((field) => (
              <FieldRenderer
                key={field.id}
                field={field}
                control={control}
                name={`custom_fields.${field.slug}`}
                error={(errors.custom_fields as any)?.[field.slug]?.message}
              />
            ))}
          </div>
        </CollapsibleSection>
      ))}

      {/* --- تصاویر --------------------------------------------------------- */}
      <CollapsibleSection title="تصاویر و اسکرین‌شات‌ها" defaultOpen={false}>
        <ImageDropzone
          attachments={attachmentsQuery.data ?? []}
          onUpload={handleUploadNow}
          onRemove={handleRemoveImage}
          uploading={uploading}
          getPreviewUrl={(a) => attachmentUrl(a.thumbnail_path ?? a.file_path)}
        />
        {pendingImages.length > 0 && !pendingTradeId && (
          <p className="mt-2 text-xs text-slate-500">
            {pendingImages.length} تصویر پس از ثبت معامله آپلود خواهد شد.
          </p>
        )}
      </CollapsibleSection>

      <div className="flex justify-end gap-3 border-t border-slate-100 pt-4">
        <button
          type="submit"
          disabled={isSubmitting || createMutation.isPending}
          className="flex items-center gap-2 rounded-lg bg-brand-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-brand-700 disabled:opacity-50"
        >
          {createMutation.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Save className="h-4 w-4" />
          )}
          ثبت معامله
        </button>
      </div>

      {createMutation.isError && (
        <p className="text-sm text-red-500">
          خطا در ثبت معامله: {(createMutation.error as Error).message}
        </p>
      )}
    </form>
  );
}
