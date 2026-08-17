import { forwardRef, type InputHTMLAttributes } from "react";
import { cn } from "@/lib/cn";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  /** برای قیمت، نماد، تیکت، مجیک‌نامبر و مقادیر فنی دیگر true بگذارید */
  ltr?: boolean;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, ltr, error, ...props }, ref) => (
    <input
      ref={ref}
      dir={ltr ? "ltr" : "rtl"}
      className={cn(
        "w-full rounded-lg border bg-white px-3 py-2 text-sm text-slate-900 shadow-sm outline-none transition",
        "placeholder:text-slate-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-100",
        ltr && "font-ltr text-left",
        error ? "border-red-400" : "border-slate-300",
        props.disabled && "cursor-not-allowed bg-slate-50 text-slate-400",
        className
      )}
      {...props}
    />
  )
);
Input.displayName = "Input";
