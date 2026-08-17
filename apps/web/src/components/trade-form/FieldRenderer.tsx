"use client";

import { Controller, type Control, type FieldValues, type Path } from "react-hook-form";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/Textarea";
import { SearchableSelect } from "@/components/ui/SearchableSelect";
import type { FieldDefinition } from "@/lib/types";
import { cn } from "@/lib/cn";

// انواعی که ورودی آن‌ها همیشه باید LTR باشد (اعداد، قیمت، نماد، تیکت و...)
const LTR_FIELD_TYPES = new Set(["number", "price", "percent", "symbol", "url"]);

interface FieldRendererProps<TFieldValues extends FieldValues> {
  field: FieldDefinition;
  control: Control<TFieldValues>;
  name: Path<TFieldValues>;
  error?: string;
}

export function FieldRenderer<TFieldValues extends FieldValues>({
  field,
  control,
  name,
  error,
}: FieldRendererProps<TFieldValues>) {
  const ltr = field.ltr_input || LTR_FIELD_TYPES.has(field.field_type);

  const label = (
    <label className="mb-1 flex items-center gap-1 text-sm font-medium text-slate-700">
      {field.title}
      {field.is_required && <span className="text-red-500">*</span>}
      {field.unit && <span className="text-xs font-normal text-slate-400">({field.unit})</span>}
    </label>
  );

  return (
    <Controller
      control={control}
      name={name}
      render={({ field: rhf }) => {
        switch (field.field_type) {
          case "number":
          case "price":
          case "percent":
            return (
              <div>
                {label}
                <Input
                  ltr
                  type="number"
                  step="any"
                  placeholder={field.placeholder ?? undefined}
                  value={rhf.value ?? ""}
                  onChange={(e) =>
                    rhf.onChange(e.target.value === "" ? null : e.target.value)
                  }
                  error={error}
                />
                {field.help_text && <Hint text={field.help_text} />}
                {error && <ErrorText text={error} />}
              </div>
            );

          case "short_text":
          case "symbol":
          case "url":
            return (
              <div>
                {label}
                <Input
                  ltr={ltr}
                  placeholder={field.placeholder ?? undefined}
                  value={rhf.value ?? ""}
                  onChange={(e) => rhf.onChange(e.target.value)}
                  error={error}
                />
                {field.help_text && <Hint text={field.help_text} />}
                {error && <ErrorText text={error} />}
              </div>
            );

          case "long_text":
            return (
              <div>
                {label}
                <Textarea
                  placeholder={field.placeholder ?? undefined}
                  value={rhf.value ?? ""}
                  onChange={(e) => rhf.onChange(e.target.value)}
                  error={error}
                />
                {field.help_text && <Hint text={field.help_text} />}
                {error && <ErrorText text={error} />}
              </div>
            );

          case "boolean":
            return (
              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
                  <input
                    type="checkbox"
                    checked={Boolean(rhf.value)}
                    onChange={(e) => rhf.onChange(e.target.checked)}
                    className="h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500"
                  />
                  {field.title}
                </label>
                {field.help_text && <Hint text={field.help_text} />}
              </div>
            );

          case "single_select":
          case "radio":
            return (
              <div>
                {label}
                <SearchableSelect
                  value={rhf.value ?? null}
                  onChange={rhf.onChange}
                  options={field.options
                    .filter((o) => o.is_active)
                    .map((o) => ({ value: o.value, label: o.label, color: o.color }))}
                  placeholder={field.placeholder ?? "انتخاب کنید..."}
                  error={error}
                />
                {field.help_text && <Hint text={field.help_text} />}
                {error && <ErrorText text={error} />}
              </div>
            );

          case "multi_select":
          case "checkbox":
            return (
              <div>
                {label}
                <SearchableSelect
                  multiple
                  value={rhf.value ?? null}
                  onChange={rhf.onChange}
                  options={field.options
                    .filter((o) => o.is_active)
                    .map((o) => ({ value: o.value, label: o.label, color: o.color }))}
                  placeholder={field.placeholder ?? "انتخاب کنید..."}
                  error={error}
                />
                {field.help_text && <Hint text={field.help_text} />}
                {error && <ErrorText text={error} />}
              </div>
            );

          case "date":
            return (
              <div>
                {label}
                <Input
                  ltr
                  type="date"
                  value={rhf.value ?? ""}
                  onChange={(e) => rhf.onChange(e.target.value)}
                  error={error}
                />
                {error && <ErrorText text={error} />}
              </div>
            );

          case "datetime":
            return (
              <div>
                {label}
                <Input
                  ltr
                  type="datetime-local"
                  value={rhf.value ?? ""}
                  onChange={(e) => rhf.onChange(e.target.value)}
                  error={error}
                />
                {error && <ErrorText text={error} />}
              </div>
            );

          case "time":
            return (
              <div>
                {label}
                <Input
                  ltr
                  type="time"
                  value={rhf.value ?? ""}
                  onChange={(e) => rhf.onChange(e.target.value)}
                  error={error}
                />
                {error && <ErrorText text={error} />}
              </div>
            );

          case "file":
            // فایل‌های عمومی فیلد پویا فعلاً به‌صورت متن مسیر/توضیح ذخیره می‌شوند؛
            // آپلود تصویر اصلی معامله در بخش پیوست‌ها (ImageDropzone) انجام می‌شود.
            return (
              <div>
                {label}
                <Input
                  ltr
                  placeholder="آدرس یا توضیح فایل"
                  value={rhf.value ?? ""}
                  onChange={(e) => rhf.onChange(e.target.value)}
                  error={error}
                />
                {error && <ErrorText text={error} />}
              </div>
            );

          default:
            return (
              <div>
                {label}
                <Input
                  value={rhf.value ?? ""}
                  onChange={(e) => rhf.onChange(e.target.value)}
                  error={error}
                />
                {error && <ErrorText text={error} />}
              </div>
            );
        }
      }}
    />
  );
}

function Hint({ text }: { text: string }) {
  return <p className="mt-1 text-xs text-slate-400">{text}</p>;
}

function ErrorText({ text }: { text: string }) {
  return <p className={cn("mt-1 text-xs text-red-500")}>{text}</p>;
}
