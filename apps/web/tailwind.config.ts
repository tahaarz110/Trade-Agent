import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        // به‌صورت پیش‌فرض از فونت‌های سیستمی فارسی/RTL استفاده می‌شود تا
        // فرایند build به اینترنت وابسته نباشد (هم‌راستا با فلسفه
        // آفلاین‌محور پروژه). برای افزودن فونت اختصاصی (مثلاً Vazirmatn)،
        // فایل .woff2 را در public/fonts/ قرار داده و از next/font/local
        // استفاده کنید.
        sans: [
          "Vazirmatn",
          "IRANSans",
          "Tahoma",
          "system-ui",
          "sans-serif",
        ],
        // فیلدهای LTR (نماد، قیمت، تیکت، شناسه‌ها) از این استک استفاده می‌کنند.
        ltr: ["Vazirmatn", "Consolas", "monospace"],
      },
      colors: {
        brand: {
          50: "#eef7ff",
          100: "#d9edff",
          500: "#2f7de1",
          600: "#2563c9",
          700: "#1d4ea3",
        },
      },
    },
  },
  plugins: [],
};

export default config;
