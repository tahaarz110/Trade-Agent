# Professional ICT Trading Journal — Offline Intelligence Engine

ژورنال معاملاتی حرفه‌ای ICT با موتور هوش تحلیلی آفلاین. این مخزن بر اساس
«پرامپت مادر» (Master Prompt — Professional Edition) به‌صورت فاز‌به‌فاز
ساخته می‌شود.

> **وضعیت فعلی: PHASE 3 — Dynamic Field Engine (تکمیل‌شده)**
> فاز ۰ (اسکلت پروژه)، فاز ۱ (اسکیمای کامل ۳۸ جدولی + مایگریشن + seed)،
> فاز ۲ (APIهای CRUD حساب/نماد/معامله/پیوست + تولید thumbnail)، و فاز ۳
> (مدیریت کامل سکشن/فیلد/گزینه پویا، reorder، فعال/غیرفعال‌سازی، جلوگیری
> از حذف مخرب، اعتبارسنجی مقدار، فیلتر داینامیک) پیاده‌سازی، تست (۴۸
> تست pytest روی PostgreSQL واقعی) و بررسی خط‌به‌خط شده‌اند.

## ساختار پروژه

```
Trade-Agent/
├── apps/
│   ├── api/            # FastAPI backend (Python 3.11+)
│   └── web/             # Next.js + TypeScript frontend (Persian RTL)
├── infra/
│   └── docker/           # docker-compose stack (PostgreSQL 16, API, Web)
├── storage/
│   ├── attachments/       # Trade image/file attachments
│   ├── backups/           # DB/app backups
│   └── analytics/parquet/ # Parquet analytical snapshots
├── .env.example           # Documents every env var used across the stack
└── promp_mother.txt        # Master Prompt (source of truth for scope)
```

## پیش‌نیازها

- Docker + Docker Compose
- (برای توسعه محلی بدون Docker) Python 3.11+ و Node.js 20+

## اجرا با Docker Compose

```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env

cd infra/docker
docker compose up --build
```

سرویس‌ها:

| سرویس | آدرس | توضیح |
|---|---|---|
| PostgreSQL 16 | localhost:5432 | `trade_agent` / `trade_agent` |
| API (FastAPI) | http://localhost:8000 | `GET /health` وضعیت را برمی‌گرداند |
| Web (Next.js) | http://localhost:3000 | صفحه فارسی RTL |

## اجرای محلی بدون Docker (اختیاری)

### Backend

```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# اطمینان از بالا بودن PostgreSQL 16 روی DATABASE_URL تنظیم‌شده
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd apps/web
npm install
cp .env.example .env
npm run dev
```

## متغیرهای محیطی

جدول کامل و مستندسازی هر متغیر در [`/.env.example`](./.env.example),
[`apps/api/.env.example`](./apps/api/.env.example) و
[`apps/web/.env.example`](./apps/web/.env.example) موجود است. خلاصه:

| متغیر | توضیح | پیش‌فرض |
|---|---|---|
| `DATABASE_URL` | رشته اتصال SQLAlchemy به PostgreSQL 16 | `postgresql+psycopg://trade_agent:trade_agent@localhost:5432/trade_agent` |
| `ATTACHMENT_DIR` | مسیر ذخیره پیوست‌های تصویری معاملات | `./storage/attachments` |
| `BACKUP_DIR` | مسیر ذخیره بکاپ‌ها | `./storage/backups` |
| `PARQUET_DIR` | مسیر خروجی تحلیلی Parquet | `./storage/analytics/parquet` |
| `LOW_RESOURCE_MODE` | فعال‌سازی حالت کم‌مصرف برای سخت‌افزار ضعیف | `true` |
| `AI_NARRATOR_ENABLED` | فعال/غیرفعال بودن لایه اختیاری راوی هوش مصنوعی | `false` |
| `ANALYTICS_SCHEDULE` | زمان‌بندی رفرش تحلیل‌های سنگین (`manual`/`daily`/`weekly`) | `daily` |
| `NEXT_PUBLIC_API_URL` | آدرس API قابل‌دسترس از مرورگر (فرانت‌اند) | `http://localhost:8000` |

## چک‌لیست پذیرش فاز ۰

- [x] `docker compose up` سرویس PostgreSQL را بالا می‌آورد.
- [x] `GET /health` مقدار `status: ok` برمی‌گرداند (به‌همراه وضعیت دیتابیس).
- [x] صفحه اصلی فرانت‌اند به‌صورت فارسی و RTL نمایش داده می‌شود.
- [x] تمام متغیرهای محیطی مستند شده‌اند.

## فاز ۱ — اسکیمای پایگاه‌داده

مدل‌های SQLAlchemy کامل در `apps/api/app/models/` (۳۸ جدول: ۱۷ جدول نسخه
عادی + ۲۱ جدول نسخه حرفه‌ای)، همراه با کلید اصلی UUID، ستون‌های
`TIMESTAMPTZ` برای زمان‌ها، و `NUMERIC` برای فیلدهای مالی.

### اجرای مایگریشن

```bash
cd apps/api
cp .env.example .env   # و در صورت نیاز DATABASE_URL را اصلاح کنید
alembic upgrade head
```

### اجرای seed (نقطه شروع کامل نسخه حرفه‌ای)

```bash
python -m app.scripts.seed
```

اسکریپت seed این موارد را می‌سازد (و در اجراهای بعدی idempotent است):

- ۴ سکشن و ۱۴ فیلد پویای پیش‌فرض ICT (کیل‌زون، سشن، دسته‌بندی ستاپ،
  ساختار بازار، بایاس تایم‌فریم بالا، مدیریت ریسک، روان‌شناسی معامله،
  بازبینی و اشتباهات) به‌همراه گزینه‌های انتخابی
- ۱ قالب چک‌لیست پیش‌فرض ورود ICT با ۶ آیتم
- ۷ تب پیش‌فرض رابط کاربری
- ۱ تم پیش‌فرض (روشن، فونت Vazirmatn)
- ۱۰ برچسب پیش‌فرض اشتباه معاملاتی
- ۶ قالب پیش‌فرض قانون پراپ‌فرم (حداکثر ضرر روزانه، حداکثر افت سرمایه،
  قانون ثبات، حداکثر معامله روزانه، محدودیت نگه‌داری آخر هفته، محدودیت
  اخبار)

### چک‌لیست پذیرش فاز ۱

- [x] مایگریشن به‌صورت تمیز روی PostgreSQL 16 اجرا می‌شود (up و down تست شد).
- [x] اسکریپت seed یک نقطه شروع کامل برای نسخه حرفه‌ای می‌سازد.
- [x] مدل فیلد پویا (`trade_field_values`) از همه انواع فیلد پشتیبانی می‌کند.
- [x] جداول نسخه حرفه‌ای ایجاد شده و در جای لازم به trades/accounts متصل‌اند.

## فاز ۲ — APIهای پایه CRUD

`apps/api/app/routers/{accounts,symbols,trades,attachments}.py` با
معماری Repository/Service. آپلود پیوست تصویر بندانگشتی (۳۲۰×۳۲۰) به‌طور
خودکار با Pillow می‌سازد. فهرست معاملات فیلترپذیر (حساب، نماد، جهت،
وضعیت، وضعیت بازبینی، بازه تاریخ) و صفحه‌بندی‌شده است.

### چک‌لیست پذیرش فاز ۲

- [x] ایجاد حساب/نماد/معامله از طریق API.
- [x] آپلود تصویر و اتصال آن به معامله؛ تصویر بندانگشتی ساخته می‌شود.
- [x] دریافت فهرست صفحه‌بندی‌شده معاملات.
- [x] دریافت جزئیات یک معامله همراه با فیلدهای پویا.
- [x] پوشش تست pytest برای CRUD، فیلتر، و صفحه‌بندی.

## فاز ۳ — موتور فیلد داینامیک

`apps/api/app/routers/{field_sections,field_definitions,field_options}.py`
مدیریت کامل سکشن/فیلد/گزینه پویا را فراهم می‌کند:

- CRUD کامل برای سکشن، تعریف فیلد، و گزینه‌های انتخابی
- Endpoint جابه‌جایی ترتیب (`/reorder`) برای هر سه سطح
- فعال/غیرفعال‌سازی (`/enable`, `/disable`) بدون نیاز به حذف
- **جلوگیری از حذف مخرب**: اگر فیلد/گزینه/سکشنی در معاملات قبلی مقدار
  ثبت‌شده داشته باشد، حذف با خطای ۴۲۲ رد می‌شود (باید غیرفعال شود)
- اعتبارسنجی کامل مقدار فیلد پویا هنگام ثبت/ویرایش معامله (تطبیق با
  گزینه‌های مجاز select، تبدیل امن نوع عددی/تاریخ/بولی، رد مقدار برای
  فیلد غیرفعال)
- فیلتر داینامیک معاملات بر اساس `field_id` + `field_value` در
  `GET /trades`
- مقادیر فیلد پویا در پاسخ جزئیات معامله (`GET /trades/{id}`) برگردانده
  می‌شوند

### چک‌لیست پذیرش فاز ۳

- [x] ساخت سکشن و فیلد سفارشی از طریق API.
- [x] افزودن گزینه به فیلدهای انتخابی.
- [x] ثبت معامله مقادیر فیلد پویا را اعتبارسنجی می‌کند.
- [x] مقادیر فیلدهای analytic-enabled در `trade_field_values` ذخیره می‌شوند.
- [x] فیلدهای پویا در پاسخ جزئیات معامله ظاهر می‌شوند.

## اجرای تست‌ها

```bash
cd apps/api
pip install -r requirements-dev.txt
# یک دیتابیس تست جدا بسازید (پیش‌فرض: trade_agent_test)
createdb trade_agent_test
pytest
```

مجموعه تست شامل ۴۸ تست (accounts، symbols، trades با فیلتر/صفحه‌بندی/
فیلد پویا، attachments با تولید thumbnail، و کل موتور فیلد داینامیک) است
که همگی روی یک دیتابیس PostgreSQL واقعی (نه mock) اجرا و تأیید شده‌اند.

## فازهای بعدی

طبق «پرامپت مادر»، فازهای بعدی شامل موتور مهندسی ویژگی، کشف الگو،
امتیازدهی رفتاری/انضباطی، آزمایشگاه فرضیه، نگهبان پراپ‌فرم، و گزارش‌ساز
قالب‌محور فارسی خواهد بود. طبق دستور صریح پرامپت مادر، بدون درخواست
مشخص کاربر به فاز بعدی منتقل نمی‌شویم.
