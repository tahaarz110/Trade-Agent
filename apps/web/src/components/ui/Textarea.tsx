import { forwardRef, type TextareaHTMLAttributes } from "react";
import { cn } from "@/lib/cn";

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, error, ...props }, ref) => (
    <textarea
      ref={ref}
      dir="rtl"
      className={cn(
        "w-full rounded-lg border bg-white px-3 py-2 text-sm text-slate-900 shadow-sm outline-none transition",
        "placeholder:text-slate-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-100",
        "min-h-[90px] resize-y",
        error ? "border-red-400" : "border-slate-300",
        className
      )}
      {...props}
    />
  )
);
Textarea.displayName = "Textarea";
