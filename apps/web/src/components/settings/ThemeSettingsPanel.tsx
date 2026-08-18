"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2, Save } from "lucide-react";

import { fetchTheme, updateTheme } from "@/lib/api";

const THEME_OPTIONS = [
  { value: "light", label: "روشن" },
  { value: "dark", label: "تیره" },
];

const DENSITY_OPTIONS = [
  { value: "comfortable", label: "راحت" },
  { value: "compact", label: "فشرده" },
];

const FONT_SIZE_OPTIONS = [
  { value: "small", label: "کوچک" },
  { value: "medium", label: "متوسط" },
  { value: "large", label: "بزرگ" },
];

export function ThemeSettingsPanel() {
  const queryClient = useQueryClient();
  const themeQuery = useQuery({ queryKey: ["theme-settings"], queryFn: fetchTheme });

  const [themeName, setThemeName] = useState("light");
  const [density, setDensity] = useState("comfortable");
  const [fontSize, setFontSize] = useState("medium");
  const [primaryColor, setPrimaryColor] = useState("#2f7de1");

  useEffect(() => {
    if (themeQuery.data) {
      setThemeName(themeQuery.data.theme_name);
      setDensity(themeQuery.data.density ?? "comfortable");
      setFontSize(themeQuery.data.font_size ?? "medium");
      setPrimaryColor(themeQuery.data.primary_color ?? "#2f7de1");
    }
  }, [themeQuery.data]);

  const saveMutation = useMutation({
    mutationFn: () =>
      updateTheme({ theme_name: themeName, density, font_size: fontSize, primary_color: primaryColor }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["theme-settings"] }),
  });

  if (themeQuery.isLoading) {
    return (
      <div className="flex justify-center py-12 text-slate-400">
        <Loader2 className="h-5 w-5 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-slate-900">تنظیمات ظاهری</h2>

      <div className="grid grid-cols-1 gap-4 rounded-xl border border-slate-200 bg-white p-4 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">تم رنگی</label>
          <div className="flex gap-2">
            {THEME_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setThemeName(opt.value)}
                className={`flex-1 rounded-lg border px-3 py-2 text-sm ${
                  themeName === opt.value
                    ? "border-brand-500 bg-brand-50 text-brand-700"
                    : "border-slate-300 text-slate-500 hover:bg-slate-50"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">تراکم چیدمان</label>
          <select
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
            value={density}
            onChange={(e) => setDensity(e.target.value)}
          >
            {DENSITY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">اندازه فونت</label>
          <select
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
            value={fontSize}
            onChange={(e) => setFontSize(e.target.value)}
          >
            {FONT_SIZE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">رنگ اصلی</label>
          <div className="flex items-center gap-2">
            <input
              type="color"
              value={primaryColor}
              onChange={(e) => setPrimaryColor(e.target.value)}
              className="h-9 w-14 cursor-pointer rounded border border-slate-300"
            />
            <span className="font-ltr text-sm text-slate-500">{primaryColor}</span>
          </div>
        </div>
      </div>

      <button
        onClick={() => saveMutation.mutate()}
        disabled={saveMutation.isPending}
        className="flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
      >
        {saveMutation.isPending ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Save className="h-4 w-4" />
        )}
        ذخیره تنظیمات ظاهری
      </button>
      {saveMutation.isSuccess && (
        <p className="text-xs text-emerald-600">تنظیمات با موفقیت ذخیره شد.</p>
      )}
    </div>
  );
}
