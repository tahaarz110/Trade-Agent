"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ChevronDown, ChevronUp, Loader2, Plus, Settings2, Trash2 } from "lucide-react";

import { Input } from "@/components/ui/Input";
import { SortableList } from "@/components/ui/SortableList";
import {
  createFieldDefinition,
  createFieldOption,
  createFieldSection,
  deleteFieldDefinition,
  deleteFieldOption,
  deleteFieldSection,
  fetchFieldDefinitions,
  fetchFieldOptions,
  fetchFieldSections,
  reorderFieldDefinitions,
  reorderFieldOptions,
  reorderFieldSections,
  toggleFieldDefinition,
  toggleFieldOption,
  toggleFieldSection,
} from "@/lib/api";
import type { FieldDefinition, FieldOption, FieldSection, FieldType } from "@/lib/types";
import { cn } from "@/lib/cn";

const FIELD_TYPE_LABELS: Record<FieldType, string> = {
  number: "عدد",
  price: "قیمت",
  percent: "درصد",
  short_text: "متن کوتاه",
  long_text: "متن بلند",
  single_select: "انتخاب تکی",
  multi_select: "انتخاب چندگانه",
  radio: "رادیویی",
  checkbox: "چک‌باکس",
  boolean: "بولی (بله/خیر)",
  date: "تاریخ",
  datetime: "تاریخ و زمان",
  time: "زمان",
  symbol: "نماد (LTR)",
  url: "آدرس اینترنتی",
  file: "فایل",
};

const SELECT_TYPES = new Set<FieldType>(["single_select", "multi_select", "radio", "checkbox"]);

export function FieldManagerSettings() {
  const queryClient = useQueryClient();
  const [expandedSection, setExpandedSection] = useState<string | null>(null);
  const [expandedField, setExpandedField] = useState<string | null>(null);
  const [newSectionOpen, setNewSectionOpen] = useState(false);

  const sectionsQuery = useQuery({
    queryKey: ["settings-field-sections"],
    queryFn: () => fetchFieldSections(true),
  });
  const fieldsQuery = useQuery({
    queryKey: ["settings-field-definitions"],
    queryFn: () => fetchFieldDefinitions(true),
  });

  const invalidateSections = () =>
    queryClient.invalidateQueries({ queryKey: ["settings-field-sections"] });
  const invalidateFields = () =>
    queryClient.invalidateQueries({ queryKey: ["settings-field-definitions"] });

  const reorderSectionsMutation = useMutation({
    mutationFn: (items: FieldSection[]) =>
      reorderFieldSections(items.map((s, idx) => ({ id: s.id, sort_order: idx }))),
    onSuccess: invalidateSections,
  });

  const toggleSectionMutation = useMutation({
    mutationFn: ({ id, enable }: { id: string; enable: boolean }) => toggleFieldSection(id, enable),
    onSuccess: invalidateSections,
  });

  const deleteSectionMutation = useMutation({
    mutationFn: (id: string) => deleteFieldSection(id),
    onSuccess: invalidateSections,
    onError: (error: Error) => window.alert(`حذف سکشن ممکن نشد: ${error.message}`),
  });

  const createSectionMutation = useMutation({
    mutationFn: (data: { key: string; title: string }) => createFieldSection(data),
    onSuccess: () => {
      invalidateSections();
      setNewSectionOpen(false);
    },
    onError: (error: Error) => window.alert(`ساخت سکشن ممکن نشد: ${error.message}`),
  });

  const sections = (sectionsQuery.data ?? []).slice().sort((a, b) => a.sort_order - b.sort_order);
  const allFields = fieldsQuery.data ?? [];

  if (sectionsQuery.isLoading || fieldsQuery.isLoading) {
    return (
      <div className="flex justify-center py-12 text-slate-400">
        <Loader2 className="h-5 w-5 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">مدیریت فیلدهای پویا</h2>
        <button
          onClick={() => setNewSectionOpen((v) => !v)}
          className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-3 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          <Plus className="h-4 w-4" />
          سکشن جدید
        </button>
      </div>

      {newSectionOpen && (
        <NewSectionForm
          onSubmit={(data) => createSectionMutation.mutate(data)}
          submitting={createSectionMutation.isPending}
        />
      )}

      <SortableList
        items={sections}
        onReorder={(items) => reorderSectionsMutation.mutate(items)}
        renderItem={(section) => (
          <SectionRow
            section={section}
            fields={allFields.filter((f) => f.section_id === section.id)}
            expanded={expandedSection === section.id}
            onToggleExpand={() =>
              setExpandedSection((prev) => (prev === section.id ? null : section.id))
            }
            onToggleActive={() =>
              toggleSectionMutation.mutate({ id: section.id, enable: !section.is_active })
            }
            onDelete={() => {
              if (window.confirm(`سکشن «${section.title}» حذف شود؟`)) {
                deleteSectionMutation.mutate(section.id);
              }
            }}
            expandedField={expandedField}
            onToggleExpandField={(fieldId) =>
              setExpandedField((prev) => (prev === fieldId ? null : fieldId))
            }
            onFieldsChanged={invalidateFields}
          />
        )}
      />
    </div>
  );
}

function NewSectionForm({
  onSubmit,
  submitting,
}: {
  onSubmit: (data: { key: string; title: string }) => void;
  submitting: boolean;
}) {
  const [key, setKey] = useState("");
  const [title, setTitle] = useState("");
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({ key, title });
      }}
      className="grid grid-cols-1 gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 sm:grid-cols-3"
    >
      <Input ltr placeholder="کلید یکتا (مثلاً custom_section)" value={key} onChange={(e) => setKey(e.target.value)} required />
      <Input placeholder="عنوان سکشن" value={title} onChange={(e) => setTitle(e.target.value)} required />
      <button
        type="submit"
        disabled={submitting}
        className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
      >
        ذخیره سکشن
      </button>
    </form>
  );
}

function SectionRow({
  section,
  fields,
  expanded,
  onToggleExpand,
  onToggleActive,
  onDelete,
  expandedField,
  onToggleExpandField,
  onFieldsChanged,
}: {
  section: FieldSection;
  fields: FieldDefinition[];
  expanded: boolean;
  onToggleExpand: () => void;
  onToggleActive: () => void;
  onDelete: () => void;
  expandedField: string | null;
  onToggleExpandField: (fieldId: string) => void;
  onFieldsChanged: () => void;
}) {
  const queryClient = useQueryClient();
  const [newFieldOpen, setNewFieldOpen] = useState(false);
  const sortedFields = fields.slice().sort((a, b) => a.sort_order - b.sort_order);

  const reorderFieldsMutation = useMutation({
    mutationFn: (items: FieldDefinition[]) =>
      reorderFieldDefinitions(items.map((f, idx) => ({ id: f.id, sort_order: idx }))),
    onSuccess: onFieldsChanged,
  });

  const createFieldMutation = useMutation({
    mutationFn: (data: Parameters<typeof createFieldDefinition>[0]) => createFieldDefinition(data),
    onSuccess: () => {
      onFieldsChanged();
      setNewFieldOpen(false);
    },
    onError: (error: Error) => window.alert(`ساخت فیلد ممکن نشد: ${error.message}`),
  });

  return (
    <div>
      <div className="flex items-center justify-between gap-2">
        <button
          type="button"
          onClick={onToggleExpand}
          className="flex flex-1 items-center gap-2 text-right"
        >
          {expanded ? (
            <ChevronUp className="h-4 w-4 text-slate-400" />
          ) : (
            <ChevronDown className="h-4 w-4 text-slate-400" />
          )}
          <span className="font-medium text-slate-800">{section.title}</span>
          <span className="font-ltr text-xs text-slate-400">({section.key})</span>
          {section.is_system && (
            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] text-slate-500">سیستمی</span>
          )}
          <span className="text-xs text-slate-400">{fields.length} فیلد</span>
        </button>
        <button
          onClick={onToggleActive}
          className={cn(
            "rounded-full px-2 py-0.5 text-xs font-medium",
            section.is_active ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-500"
          )}
        >
          {section.is_active ? "فعال" : "غیرفعال"}
        </button>
        {!section.is_system && (
          <button onClick={onDelete} className="text-slate-400 hover:text-red-500">
            <Trash2 className="h-4 w-4" />
          </button>
        )}
      </div>

      {expanded && (
        <div className="mt-3 space-y-3 border-r-2 border-slate-100 pr-4">
          <div className="flex justify-end">
            <button
              onClick={() => setNewFieldOpen((v) => !v)}
              className="flex items-center gap-1 rounded-lg border border-slate-300 px-2.5 py-1.5 text-xs text-slate-600 hover:bg-slate-50"
            >
              <Plus className="h-3.5 w-3.5" />
              فیلد جدید
            </button>
          </div>

          {newFieldOpen && (
            <NewFieldForm
              sectionId={section.id}
              onSubmit={(data) => createFieldMutation.mutate(data)}
              submitting={createFieldMutation.isPending}
            />
          )}

          {sortedFields.length === 0 ? (
            <p className="py-3 text-center text-xs text-slate-400">فیلدی در این سکشن نیست</p>
          ) : (
            <SortableList
              items={sortedFields}
              onReorder={(items) => reorderFieldsMutation.mutate(items)}
              renderItem={(field) => (
                <FieldRow
                  field={field}
                  expanded={expandedField === field.id}
                  onToggleExpand={() => onToggleExpandField(field.id)}
                  onChanged={onFieldsChanged}
                  queryClient={queryClient}
                />
              )}
            />
          )}
        </div>
      )}
    </div>
  );
}

function NewFieldForm({
  sectionId,
  onSubmit,
  submitting,
}: {
  sectionId: string;
  onSubmit: (data: Parameters<typeof createFieldDefinition>[0]) => void;
  submitting: boolean;
}) {
  const [slug, setSlug] = useState("");
  const [title, setTitle] = useState("");
  const [fieldType, setFieldType] = useState<FieldType>("short_text");
  const [isRequired, setIsRequired] = useState(false);
  const [analyticEnabled, setAnalyticEnabled] = useState(false);
  const [aiEnabled, setAiEnabled] = useState(false);
  const [showInTable, setShowInTable] = useState(false);
  const [filterable, setFilterable] = useState(false);
  const [ltrInput, setLtrInput] = useState(false);
  const [optionsText, setOptionsText] = useState("");

  const isSelectType = SELECT_TYPES.has(fieldType);

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({
          section_id: sectionId,
          slug,
          title,
          field_type: fieldType,
          is_required: isRequired,
          analytic_enabled: analyticEnabled,
          ai_enabled: aiEnabled,
          show_in_table: showInTable,
          filterable,
          ltr_input: ltrInput,
          options: isSelectType
            ? optionsText.split(",").map((s) => s.trim()).filter(Boolean)
            : undefined,
        });
      }}
      className="space-y-3 rounded-xl border border-slate-200 bg-slate-50 p-4"
    >
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <Input ltr placeholder="اسلاگ یکتا (custom_field)" value={slug} onChange={(e) => setSlug(e.target.value)} required />
        <Input placeholder="عنوان فیلد" value={title} onChange={(e) => setTitle(e.target.value)} required />
        <select
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
          value={fieldType}
          onChange={(e) => setFieldType(e.target.value as FieldType)}
        >
          {Object.entries(FIELD_TYPE_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </div>

      {isSelectType && (
        <Input
          placeholder="گزینه‌ها با ویرگول جدا کنید (مثلاً: لندن, نیویورک, آسیا)"
          value={optionsText}
          onChange={(e) => setOptionsText(e.target.value)}
        />
      )}

      <div className="flex flex-wrap gap-4 text-xs text-slate-600">
        <FlagCheckbox label="الزامی" checked={isRequired} onChange={setIsRequired} />
        <FlagCheckbox label="ورودی LTR" checked={ltrInput} onChange={setLtrInput} />
        <FlagCheckbox label="نمایش در جدول" checked={showInTable} onChange={setShowInTable} />
        <FlagCheckbox label="قابل فیلتر" checked={filterable} onChange={setFilterable} />
        <FlagCheckbox label="ورود به تحلیل‌ها (analytic)" checked={analyticEnabled} onChange={setAnalyticEnabled} />
        <FlagCheckbox label="در دسترس هوش مصنوعی" checked={aiEnabled} onChange={setAiEnabled} />
      </div>

      <button
        type="submit"
        disabled={submitting}
        className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
      >
        ذخیره فیلد
      </button>
    </form>
  );
}

function FlagCheckbox({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <label className="flex items-center gap-1.5">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="h-3.5 w-3.5 rounded border-slate-300 text-brand-600 focus:ring-brand-500"
      />
      {label}
    </label>
  );
}

function FieldRow({
  field,
  expanded,
  onToggleExpand,
  onChanged,
  queryClient,
}: {
  field: FieldDefinition;
  expanded: boolean;
  onToggleExpand: () => void;
  onChanged: () => void;
  queryClient: ReturnType<typeof useQueryClient>;
}) {
  const toggleMutation = useMutation({
    mutationFn: () => toggleFieldDefinition(field.id, !field.is_active),
    onSuccess: onChanged,
  });
  const deleteMutation = useMutation({
    mutationFn: () => deleteFieldDefinition(field.id),
    onSuccess: onChanged,
    onError: (error: Error) => window.alert(`حذف فیلد ممکن نشد: ${error.message}`),
  });

  const isSelectType = SELECT_TYPES.has(field.field_type);

  return (
    <div>
      <div className="flex items-center justify-between gap-2">
        <button
          type="button"
          onClick={isSelectType ? onToggleExpand : undefined}
          disabled={!isSelectType}
          className="flex flex-1 items-center gap-2 text-right disabled:cursor-default"
        >
          {isSelectType &&
            (expanded ? (
              <ChevronUp className="h-3.5 w-3.5 text-slate-400" />
            ) : (
              <ChevronDown className="h-3.5 w-3.5 text-slate-400" />
            ))}
          <span className="text-sm font-medium text-slate-700">{field.title}</span>
          <span className="font-ltr text-xs text-slate-400">({field.slug})</span>
          <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] text-slate-500">
            {FIELD_TYPE_LABELS[field.field_type]}
          </span>
          {field.analytic_enabled && (
            <Settings2 className="h-3 w-3 text-brand-500" aria-label="در تحلیل‌ها استفاده می‌شود" />
          )}
        </button>
        <button
          onClick={() => toggleMutation.mutate()}
          className={cn(
            "rounded-full px-2 py-0.5 text-xs font-medium",
            field.is_active ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-500"
          )}
        >
          {field.is_active ? "فعال" : "غیرفعال"}
        </button>
        {!field.is_system && (
          <button
            onClick={() => {
              if (window.confirm(`فیلد «${field.title}» حذف شود؟`)) deleteMutation.mutate();
            }}
            className="text-slate-400 hover:text-red-500"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>
        )}
      </div>

      {expanded && isSelectType && (
        <div className="mt-2 border-r-2 border-slate-100 pr-4">
          <FieldOptionsManager fieldId={field.id} queryClient={queryClient} />
        </div>
      )}
    </div>
  );
}

function FieldOptionsManager({
  fieldId,
  queryClient,
}: {
  fieldId: string;
  queryClient: ReturnType<typeof useQueryClient>;
}) {
  const [newValue, setNewValue] = useState("");
  const [newLabel, setNewLabel] = useState("");

  const optionsQuery = useQuery({
    queryKey: ["field-options", fieldId],
    queryFn: () => fetchFieldOptions(fieldId),
  });

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["field-options", fieldId] });

  const createMutation = useMutation({
    mutationFn: () => createFieldOption({ field_id: fieldId, value: newValue, label: newLabel || newValue }),
    onSuccess: () => {
      invalidate();
      setNewValue("");
      setNewLabel("");
    },
  });

  const toggleMutation = useMutation({
    mutationFn: ({ id, enable }: { id: string; enable: boolean }) => toggleFieldOption(id, enable),
    onSuccess: invalidate,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteFieldOption(id),
    onSuccess: invalidate,
    onError: (error: Error) => window.alert(`حذف گزینه ممکن نشد: ${error.message}`),
  });

  const reorderMutation = useMutation({
    mutationFn: (items: FieldOption[]) =>
      reorderFieldOptions(fieldId, items.map((o, idx) => ({ id: o.id, sort_order: idx }))),
    onSuccess: invalidate,
  });

  const options = (optionsQuery.data ?? []).slice().sort((a, b) => a.sort_order - b.sort_order);

  return (
    <div className="space-y-2 py-2">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (newValue) createMutation.mutate();
        }}
        className="flex gap-2"
      >
        <Input
          className="text-xs"
          placeholder="مقدار گزینه"
          value={newValue}
          onChange={(e) => setNewValue(e.target.value)}
        />
        <Input
          className="text-xs"
          placeholder="برچسب نمایشی (اختیاری)"
          value={newLabel}
          onChange={(e) => setNewLabel(e.target.value)}
        />
        <button
          type="submit"
          className="shrink-0 rounded-lg bg-brand-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-brand-700"
        >
          افزودن
        </button>
      </form>

      {optionsQuery.isLoading ? (
        <Loader2 className="h-4 w-4 animate-spin text-slate-400" />
      ) : options.length === 0 ? (
        <p className="text-xs text-slate-400">گزینه‌ای ثبت نشده</p>
      ) : (
        <SortableList
          items={options}
          onReorder={(items) => reorderMutation.mutate(items)}
          renderItem={(option) => (
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs font-medium text-slate-700">{option.label}</span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => toggleMutation.mutate({ id: option.id, enable: !option.is_active })}
                  className={cn(
                    "rounded-full px-2 py-0.5 text-[10px] font-medium",
                    option.is_active ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-500"
                  )}
                >
                  {option.is_active ? "فعال" : "غیرفعال"}
                </button>
                <button
                  onClick={() => {
                    if (window.confirm(`گزینه «${option.label}» حذف شود؟`)) deleteMutation.mutate(option.id);
                  }}
                  className="text-slate-400 hover:text-red-500"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          )}
        />
      )}
    </div>
  );
}
