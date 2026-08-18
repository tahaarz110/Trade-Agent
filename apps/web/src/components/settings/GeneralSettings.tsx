"use client";

import { useQuery } from "@tanstack/react-query";
import { CheckCircle2, XCircle } from "lucide-react";
import { fetchHealth } from "@/lib/api";

export function GeneralSettings() {
  const healthQuery = useQuery({ queryKey: ["health"], queryFn: fetchHealth });
  const health = healthQuery.data;

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-slate-900">تنظیمات عمومی</h2>

      <div className="rounded-xl border border-slate-200 bg-white p-4">
        <h3 className="mb-3 text-sm font-semibold text-slate-700">وضعیت سیستم</h3>
        <dl className="grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
          <div>
            <dt className="text-slate-500">اتصال به سرور</dt>
            <dd className="mt-1 flex items-center gap-1.5 font-medium">
              {health?.status === "ok" ? (
                <>
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                  <span className="text-emerald-600">متصل</span>
                </>
              ) : (
                <>
                  <XCircle className="h-4 w-4 text-red-500" />
                  <span className="text-red-600">قطع</span>
                </>
              )}
            </dd>
          </div>
          <div>
            <dt className="text-slate-500">پایگاه‌داده</dt>
            <dd className="mt-1 font-ltr font-medium text-slate-800">{health?.database ?? "—"}</dd>
          </div>
          <div>
            <dt className="text-slate-500">محیط اجرا</dt>
            <dd className="mt-1 font-ltr font-medium text-slate-800">{health?.env ?? "—"}</dd>
          </div>
          <div>
            <dt className="text-slate-500">حالت کم‌مصرف</dt>
            <dd className="mt-1 font-medium text-slate-800">
              {health?.low_resource_mode ? "فعال" : "غیرفعال"}
            </dd>
          </div>
          <div>
            <dt className="text-slate-500">راوی هوش مصنوعی</dt>
            <dd className="mt-1 font-medium text-slate-800">
              {health?.ai_narrator_enabled ? "فعال" : "غیرفعال"}
            </dd>
          </div>
        </dl>
        <p className="mt-4 text-xs text-slate-400">
          این مقادیر از طریق متغیرهای محیطی سرور (.env) پیکربندی می‌شوند و در
          فازهای بعدی امکان تغییر آن‌ها از همین صفحه اضافه خواهد شد.
        </p>
      </div>
    </div>
  );
}
