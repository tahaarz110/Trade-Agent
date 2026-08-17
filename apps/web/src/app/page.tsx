"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { fetchHealth } from "@/lib/api";

const normalFeatures = [
  "مدیریت حساب‌ها (دمو، واقعی، پراپ)",
  "فرم ثبت معامله با فیلدهای پویا و اختصاصی",
  "سکشن‌ها و فیلدهای پیش‌فرض بر پایه ICT",
  "تاریخچه معاملات با فیلتر و صفحه‌بندی سمت سرور",
  "پیوست تصویر با نمایش بزرگ‌نمایی‌شونده",
  "ایمپورت خودکار از متاتریدر",
];

const professionalFeatures = [
  "موتور هوش تحلیلی آفلاین (بدون نیاز به LLM)",
  "پروفایل DNA معامله‌گر",
  "کاوشگر مزیت آماری (Edge Explorer)",
  "موتور هزینه اشتباهات",
  "دروازه پیش از معامله و کالبدشکافی پس از معامله",
  "امتیاز ریسک رفتاری و امتیاز انضباط",
];

export default function HomePage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth,
    retry: 1,
  });

  return (
    <main className="mx-auto flex min-h-screen max-w-4xl flex-col gap-8 px-6 py-12">
      <header className="flex flex-col gap-2">
        <span className="w-fit rounded-full bg-brand-100 px-3 py-1 text-xs font-medium text-brand-700">
          فاز ۴ — رابط کاربری اصلی
        </span>
        <h1 className="text-3xl font-bold text-slate-900">
          ژورنال معاملاتی حرفه‌ای ICT
        </h1>
        <p className="text-slate-600">
          سامانه آفلاین‌محور ثبت، تحلیل و بهبود عملکرد معاملاتی — نسخه حرفه‌ای
          با موتور هوش تحلیلی داخلی و بدون وابستگی به مدل‌های زبانی بزرگ.
        </p>
        <Link
          href="/trades"
          className="mt-2 flex w-fit items-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-brand-700"
        >
          ورود به ژورنال معاملات
          <ArrowLeft className="h-4 w-4" />
        </Link>
      </header>

      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="mb-3 text-lg font-semibold text-slate-900">
          وضعیت سرویس API
        </h2>
        {isLoading && <p className="text-slate-500">در حال بررسی اتصال...</p>}
        {isError && (
          <p className="text-red-600">
            اتصال به API برقرار نشد. مطمئن شوید سرویس بک‌اند در حال اجراست.
          </p>
        )}
        {data && (
          <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm sm:grid-cols-3">
            <div className="flex flex-col">
              <dt className="text-slate-500">وضعیت</dt>
              <dd className="ltr-field font-medium text-emerald-600">
                {data.status}
              </dd>
            </div>
            <div className="flex flex-col">
              <dt className="text-slate-500">پایگاه‌داده</dt>
              <dd className="ltr-field font-medium text-slate-800">
                {data.database}
              </dd>
            </div>
            <div className="flex flex-col">
              <dt className="text-slate-500">محیط اجرا</dt>
              <dd className="ltr-field font-medium text-slate-800">
                {data.env}
              </dd>
            </div>
            <div className="flex flex-col">
              <dt className="text-slate-500">حالت کم‌مصرف</dt>
              <dd className="font-medium text-slate-800">
                {data.low_resource_mode ? "فعال" : "غیرفعال"}
              </dd>
            </div>
            <div className="flex flex-col">
              <dt className="text-slate-500">راوی هوش مصنوعی</dt>
              <dd className="font-medium text-slate-800">
                {data.ai_narrator_enabled ? "فعال" : "غیرفعال"}
              </dd>
            </div>
          </dl>
        )}
      </section>

      <section className="grid gap-6 sm:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="mb-3 text-lg font-semibold text-slate-900">
            نسخه عادی
          </h2>
          <ul className="list-inside list-disc space-y-1.5 text-sm text-slate-600">
            {normalFeatures.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div className="rounded-xl border border-brand-100 bg-brand-50 p-5 shadow-sm">
          <h2 className="mb-3 text-lg font-semibold text-slate-900">
            افزوده‌های نسخه حرفه‌ای
          </h2>
          <ul className="list-inside list-disc space-y-1.5 text-sm text-slate-700">
            {professionalFeatures.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </section>

      <footer className="text-xs text-slate-400">
        این صفحه بخشی از رابط کاربری پروژه (فاز ۴) است. ماژول‌های تحلیلی و
        هوش آفلاین در فازهای بعدی پیاده‌سازی می‌شوند.
      </footer>
    </main>
  );
}
