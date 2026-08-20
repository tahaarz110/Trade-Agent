"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Lightbox from "yet-another-react-lightbox";
import Zoom from "yet-another-react-lightbox/plugins/zoom";
import "yet-another-react-lightbox/styles.css";

import { Modal } from "@/components/ui/Modal";
import { ChecklistCard } from "@/components/trade-form/ChecklistCard";
import {
  attachmentUrl,
  fetchAccounts,
  fetchAttachments,
  fetchFieldSections,
  fetchFieldDefinitions,
  fetchSymbols,
  fetchTradeDetail,
} from "@/lib/api";
import { cn } from "@/lib/cn";

interface TradeDetailModalProps {
  tradeId: string | null;
  onClose: () => void;
}

export function TradeDetailModal({ tradeId, onClose }: TradeDetailModalProps) {
  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null);

  const tradeQuery = useQuery({
    queryKey: ["trade-detail", tradeId],
    queryFn: () => fetchTradeDetail(tradeId as string),
    enabled: Boolean(tradeId),
  });
  const attachmentsQuery = useQuery({
    queryKey: ["attachments", tradeId],
    queryFn: () => fetchAttachments(tradeId as string),
    enabled: Boolean(tradeId),
  });
  const accountsQuery = useQuery({ queryKey: ["accounts"], queryFn: () => fetchAccounts() });
  const symbolsQuery = useQuery({ queryKey: ["symbols"], queryFn: () => fetchSymbols() });
  const sectionsQuery = useQuery({
    queryKey: ["field-sections"],
    queryFn: () => fetchFieldSections(true),
  });
  const fieldsQuery = useQuery({
    queryKey: ["field-definitions"],
    queryFn: () => fetchFieldDefinitions(true),
  });

  const trade = tradeQuery.data;

  const accountName = useMemo(
    () => accountsQuery.data?.items.find((a) => a.id === trade?.account_id)?.name ?? "—",
    [accountsQuery.data, trade]
  );
  const symbolName = useMemo(
    () => symbolsQuery.data?.items.find((s) => s.id === trade?.symbol_id)?.name ?? "—",
    [symbolsQuery.data, trade]
  );

  // گروه‌بندی فیلدهای پویا بر اساس عنوان سکشن، با استفاده از field_slug -> field_id -> section
  const groupedCustomFields = useMemo(() => {
    if (!trade || !fieldsQuery.data || !sectionsQuery.data) return [];
    const fieldBySlug = new Map(fieldsQuery.data.map((f) => [f.slug, f]));
    const sectionById = new Map(sectionsQuery.data.map((s) => [s.id, s]));

    const groups = new Map<string, { title: string; items: typeof trade.custom_fields }>();
    trade.custom_fields.forEach((cf) => {
      const fieldDef = fieldBySlug.get(cf.field_slug);
      const sectionTitle = fieldDef ? sectionById.get(fieldDef.section_id)?.title ?? "سایر" : "سایر";
      if (!groups.has(sectionTitle)) groups.set(sectionTitle, { title: sectionTitle, items: [] });
      groups.get(sectionTitle)!.items.push(cf);
    });
    return Array.from(groups.values());
  }, [trade, fieldsQuery.data, sectionsQuery.data]);

  const attachments = attachmentsQuery.data ?? [];
  const slides = attachments.map((a) => ({ src: attachmentUrl(a.file_path) }));

  return (
    <>
      <Modal open={Boolean(tradeId)} onClose={onClose} title="جزئیات معامله" widthClassName="max-w-3xl">
        {tradeQuery.isLoading || !trade ? (
          <div className="py-12 text-center text-slate-400">در حال بارگذاری...</div>
        ) : (
          <div className="space-y-5">
            {/* --- خلاصه ------------------------------------------------------- */}
            <div className="grid grid-cols-2 gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 sm:grid-cols-4">
              <SummaryItem label="حساب" value={accountName} />
              <SummaryItem label="نماد" value={symbolName} ltr />
              <SummaryItem
                label="جهت"
                value={trade.direction === "buy" ? "خرید" : "فروش"}
                valueClassName={trade.direction === "buy" ? "text-emerald-600" : "text-rose-600"}
              />
              <SummaryItem
                label="وضعیت"
                value={trade.status === "open" ? "باز" : trade.status === "closed" ? "بسته" : "لغوشده"}
              />
              <SummaryItem label="قیمت ورود" value={trade.entry_price} ltr />
              <SummaryItem label="قیمت خروج" value={trade.exit_price ?? "—"} ltr />
              <SummaryItem label="حجم" value={trade.volume} ltr />
              <SummaryItem
                label="سود/زیان خالص"
                value={trade.net_profit ?? "—"}
                ltr
                valueClassName={
                  trade.net_profit != null
                    ? Number(trade.net_profit) >= 0
                      ? "text-emerald-600"
                      : "text-rose-600"
                    : undefined
                }
              />
              {trade.has_checklist && (
                <SummaryItem
                  label="امتیاز چک‌لیست"
                  value={
                    trade.checklist_score_percent !== null
                      ? `${trade.checklist_score_percent}٪`
                      : "—"
                  }
                  ltr
                  valueClassName={
                    trade.required_missing_count > 0 ? "text-amber-600" : "text-emerald-600"
                  }
                />
              )}
            </div>

            {/* --- فیلدهای پویا گروه‌بندی‌شده بر اساس سکشن ------------------------ */}
            {groupedCustomFields.map((group) => (
              <div key={group.title}>
                <h3 className="mb-2 text-sm font-semibold text-slate-700">{group.title}</h3>
                <div className="grid grid-cols-1 gap-x-6 gap-y-2 rounded-xl border border-slate-100 p-4 sm:grid-cols-2">
                  {group.items.map((item) => (
                    <div key={item.field_slug} className="flex justify-between border-b border-slate-50 py-1.5 text-sm last:border-0">
                      <span className="text-slate-500">{item.field_title}</span>
                      <span className="font-medium text-slate-800">
                        {formatValue(item.value)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}

            {/* --- چک‌لیست (فاز ۵.۵) --------------------------------------------- */}
            <div>
              <h3 className="mb-2 text-sm font-semibold text-slate-700">چک‌لیست معامله</h3>
              <ChecklistCard tradeId={trade.id} variant="detail" />
            </div>

            {/* --- تصاویر ------------------------------------------------------- */}
            {attachments.length > 0 && (
              <div>
                <h3 className="mb-2 text-sm font-semibold text-slate-700">تصاویر و اسکرین‌شات‌ها</h3>
                <div className="grid grid-cols-3 gap-3 sm:grid-cols-4">
                  {attachments.map((att, idx) => (
                    <button
                      key={att.id}
                      type="button"
                      onClick={() => setLightboxIndex(idx)}
                      className="aspect-square overflow-hidden rounded-lg border border-slate-200 bg-slate-50"
                    >
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={attachmentUrl(att.thumbnail_path ?? att.file_path)}
                        alt={att.caption ?? att.file_name}
                        className="h-full w-full object-cover transition hover:scale-105"
                      />
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>

      <Lightbox
        open={lightboxIndex !== null}
        index={lightboxIndex ?? 0}
        close={() => setLightboxIndex(null)}
        slides={slides}
        plugins={[Zoom]}
      />
    </>
  );
}

function SummaryItem({
  label,
  value,
  ltr,
  valueClassName,
}: {
  label: string;
  value: string;
  ltr?: boolean;
  valueClassName?: string;
}) {
  return (
    <div>
      <div className="text-xs text-slate-500">{label}</div>
      <div className={cn("font-medium text-slate-900", ltr && "font-ltr text-left", valueClassName)}>
        {value}
      </div>
    </div>
  );
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "boolean") return value ? "بله" : "خیر";
  if (Array.isArray(value)) return value.join("، ");
  return String(value);
}
