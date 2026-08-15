"""اسکریپت seed برای ایجاد نقطه شروع کامل نسخه حرفه‌ای.

اجرا: python -m app.scripts.seed
Idempotent است: هر بخش قبل از درج، وجود رکورد را با کلید یکتا (slug/key/name)
بررسی می‌کند تا اجرای مجدد داده تکراری نسازد.
"""
import logging

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import (
    ChecklistItem,
    ChecklistTemplate,
    FieldDefinition,
    FieldOption,
    FieldSection,
    MistakeTag,
    PropRule,
    ThemeSetting,
    UITab,
)
from app.models.enums import FieldType, PropRuleType

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# ۱) سکشن‌ها و فیلدهای پیش‌فرض ICT
# ---------------------------------------------------------------------------
SECTIONS = [
    {
        "key": "ict_market_structure",
        "title": "ساختار بازار (ICT)",
        "description": "مفاهیم ساختاری ICT مرتبط با این معامله",
        "sort_order": 10,
        "fields": [
            {
                "slug": "killzone",
                "title": "کیل‌زون",
                "field_type": FieldType.SINGLE_SELECT,
                "show_in_table": True,
                "filterable": True,
                "analytic_enabled": True,
                "sort_order": 1,
                "options": [
                    "کیل‌زون لندن",
                    "نیویورک AM",
                    "نیویورک PM",
                    "کیل‌زون آسیا",
                    "بسته‌شدن لندن",
                ],
            },
            {
                "slug": "session",
                "title": "سشن معاملاتی",
                "field_type": FieldType.SINGLE_SELECT,
                "show_in_table": True,
                "filterable": True,
                "analytic_enabled": True,
                "sort_order": 2,
                "options": ["آسیا", "لندن", "نیویورک", "همپوشانی لندن-نیویورک"],
            },
            {
                "slug": "setup_category",
                "title": "دسته‌بندی ستاپ",
                "field_type": FieldType.SINGLE_SELECT,
                "show_in_table": True,
                "filterable": True,
                "analytic_enabled": True,
                "sort_order": 3,
                "options": [
                    "Order Block",
                    "Fair Value Gap",
                    "جاروب نقدینگی (Liquidity Sweep)",
                    "Breaker Block",
                    "Mitigation Block",
                    "Turtle Soup",
                    "Silver Bullet",
                ],
            },
            {
                "slug": "market_structure_event",
                "title": "رویداد ساختار بازار",
                "field_type": FieldType.SINGLE_SELECT,
                "filterable": True,
                "analytic_enabled": True,
                "sort_order": 4,
                "options": [
                    "شکست ساختار (BOS)",
                    "تغییر کاراکتر (CHoCH)",
                    "ادامه روند",
                    "رنج",
                ],
            },
            {
                "slug": "htf_bias",
                "title": "بایاس تایم‌فریم بالاتر",
                "field_type": FieldType.SINGLE_SELECT,
                "filterable": True,
                "analytic_enabled": True,
                "sort_order": 5,
                "options": ["صعودی", "نزولی", "خنثی"],
            },
        ],
    },
    {
        "key": "risk_management",
        "title": "مدیریت ریسک",
        "description": "پارامترهای ریسک برنامه‌ریزی‌شده و واقعی معامله",
        "sort_order": 20,
        "fields": [
            {
                "slug": "planned_risk_percent",
                "title": "درصد ریسک برنامه‌ریزی‌شده",
                "field_type": FieldType.PERCENT,
                "analytic_enabled": True,
                "sort_order": 1,
            },
            {
                "slug": "planned_rr",
                "title": "نسبت ریسک به ریوارد برنامه‌ریزی‌شده",
                "field_type": FieldType.NUMBER,
                "analytic_enabled": True,
                "sort_order": 2,
            },
            {
                "slug": "moved_stop_loss",
                "title": "جابجایی حد ضرر بعد از ورود",
                "field_type": FieldType.BOOLEAN,
                "analytic_enabled": True,
                "sort_order": 3,
            },
        ],
    },
    {
        "key": "trade_psychology",
        "title": "روان‌شناسی معامله",
        "description": "وضعیت ذهنی قبل و بعد از معامله",
        "sort_order": 30,
        "fields": [
            {
                "slug": "emotion_before",
                "title": "احساس قبل از ورود",
                "field_type": FieldType.SINGLE_SELECT,
                "analytic_enabled": True,
                "ai_enabled": True,
                "sort_order": 1,
                "options": ["آرام", "مضطرب", "هیجان‌زده", "خسته", "عصبانی", "منتقم"],
            },
            {
                "slug": "emotion_after",
                "title": "احساس بعد از خروج",
                "field_type": FieldType.SINGLE_SELECT,
                "analytic_enabled": True,
                "ai_enabled": True,
                "sort_order": 2,
                "options": ["راضی", "پشیمان", "بی‌تفاوت", "ناامید", "مطمئن"],
            },
            {
                "slug": "confidence_level",
                "title": "سطح اطمینان (۱ تا ۱۰)",
                "field_type": FieldType.NUMBER,
                "analytic_enabled": True,
                "sort_order": 3,
            },
            {
                "slug": "followed_plan",
                "title": "پیروی کامل از پلن معاملاتی",
                "field_type": FieldType.BOOLEAN,
                "analytic_enabled": True,
                "sort_order": 4,
            },
        ],
    },
    {
        "key": "review_and_mistakes",
        "title": "بازبینی و اشتباهات",
        "description": "یادداشت پس از معامله و اشتباهات ثبت‌شده",
        "sort_order": 40,
        "fields": [
            {
                "slug": "review_note",
                "title": "یادداشت بازبینی",
                "field_type": FieldType.LONG_TEXT,
                "ai_enabled": True,
                "sort_order": 1,
            },
            {
                "slug": "lesson_note",
                "title": "درس گرفته‌شده",
                "field_type": FieldType.LONG_TEXT,
                "ai_enabled": True,
                "sort_order": 2,
            },
        ],
    },
]


def seed_sections_and_fields(db: Session) -> None:
    for section_data in SECTIONS:
        section = db.query(FieldSection).filter_by(key=section_data["key"]).first()
        if not section:
            section = FieldSection(
                key=section_data["key"],
                title=section_data["title"],
                description=section_data.get("description"),
                is_system=True,
                sort_order=section_data["sort_order"],
            )
            db.add(section)
            db.flush()
            logger.info("سکشن ایجاد شد: %s", section.title)

        for field_data in section_data["fields"]:
            field = db.query(FieldDefinition).filter_by(slug=field_data["slug"]).first()
            if field:
                continue
            field = FieldDefinition(
                section_id=section.id,
                slug=field_data["slug"],
                title=field_data["title"],
                field_type=field_data["field_type"],
                is_system=True,
                show_in_table=field_data.get("show_in_table", False),
                filterable=field_data.get("filterable", False),
                analytic_enabled=field_data.get("analytic_enabled", False),
                ai_enabled=field_data.get("ai_enabled", False),
                ltr_input=field_data["field_type"] in (FieldType.NUMBER, FieldType.PRICE, FieldType.PERCENT),
                sort_order=field_data["sort_order"],
            )
            db.add(field)
            db.flush()
            logger.info("  فیلد ایجاد شد: %s", field.title)

            for i, option_label in enumerate(field_data.get("options", [])):
                db.add(
                    FieldOption(
                        field_id=field.id,
                        value=option_label,
                        label=option_label,
                        sort_order=i,
                    )
                )


# ---------------------------------------------------------------------------
# ۲) چک‌لیست پیش‌فرض ورود ICT
# ---------------------------------------------------------------------------
DEFAULT_CHECKLIST_ITEMS = [
    "جاروب نقدینگی (Liquidity Sweep) قبل از ورود مشاهده شد",
    "وجود Fair Value Gap در جهت معامله",
    "هم‌راستایی ورود با بایاس تایم‌فریم بالاتر",
    "ورود داخل یک کیل‌زون معتبر انجام شد",
    "حد ضرر بر اساس ساختار بازار تعیین شد (نه یک عدد دلخواه)",
    "نسبت ریسک به ریوارد از پیش تعیین‌شده رعایت شد",
]


def seed_checklist(db: Session) -> None:
    template = db.query(ChecklistTemplate).filter_by(name="چک‌لیست ورود ICT").first()
    if template:
        return
    template = ChecklistTemplate(
        name="چک‌لیست ورود ICT",
        description="چک‌لیست پیش‌فرض پیش از تایید ورود به معامله",
        is_default=True,
    )
    db.add(template)
    db.flush()
    for i, title in enumerate(DEFAULT_CHECKLIST_ITEMS):
        db.add(
            ChecklistItem(
                template_id=template.id,
                title=title,
                is_required=True,
                sort_order=i,
            )
        )
    logger.info("قالب چک‌لیست پیش‌فرض ایجاد شد")


# ---------------------------------------------------------------------------
# ۳) تب‌های پیش‌فرض رابط کاربری
# ---------------------------------------------------------------------------
DEFAULT_TABS = [
    ("dashboard", "داشبورد", "layout-dashboard"),
    ("journal", "ژورنال", "notebook-pen"),
    ("history", "تاریخچه معاملات", "history"),
    ("insights", "بینش‌ها", "lightbulb"),
    ("pre_trade", "دروازه پیش از معامله", "shield-check"),
    ("reports", "گزارش‌ها", "file-bar-chart"),
    ("settings", "تنظیمات", "settings"),
]


def seed_ui_tabs(db: Session) -> None:
    created = 0
    for i, (key, title, icon) in enumerate(DEFAULT_TABS):
        if db.query(UITab).filter_by(key=key).first():
            continue
        db.add(UITab(key=key, title=title, icon=icon, sort_order=i))
        created += 1
    if created:
        logger.info("تب‌های پیش‌فرض رابط کاربری ایجاد شدند (%d مورد جدید)", created)


# ---------------------------------------------------------------------------
# ۴) تم پیش‌فرض
# ---------------------------------------------------------------------------
def seed_theme(db: Session) -> None:
    if db.query(ThemeSetting).filter_by(key="default").first():
        return
    db.add(
        ThemeSetting(
            key="default",
            theme_name="light",
            font_family="Vazirmatn",
            font_size="medium",
            density="comfortable",
            primary_color="#2f7de1",
        )
    )
    logger.info("تم پیش‌فرض ایجاد شد")


# ---------------------------------------------------------------------------
# ۵) برچسب‌های پیش‌فرض اشتباه
# ---------------------------------------------------------------------------
DEFAULT_MISTAKE_TAGS = [
    ("ورود زودهنگام", "#ef4444"),
    ("جابجایی حد ضرر", "#f97316"),
    ("حجم بیش از حد", "#f59e0b"),
    ("معامله انتقامی", "#dc2626"),
    ("معامله بدون ستاپ معتبر", "#e11d48"),
    ("خروج زودهنگام از سود", "#f97316"),
    ("نادیده گرفتن چک‌لیست", "#eab308"),
    ("معامله در ساعات نامناسب", "#a855f7"),
    ("اضافه‌معامله (Overtrading)", "#dc2626"),
    ("عدم رعایت ریسک تعیین‌شده", "#ef4444"),
]


def seed_mistake_tags(db: Session) -> None:
    created = 0
    for name, color in DEFAULT_MISTAKE_TAGS:
        if db.query(MistakeTag).filter_by(name=name).first():
            continue
        db.add(MistakeTag(name=name, color=color))
        created += 1
    if created:
        logger.info("برچسب‌های پیش‌فرض اشتباه ایجاد شدند (%d مورد جدید)", created)


# ---------------------------------------------------------------------------
# ۶) قالب‌های پیش‌فرض قوانین پراپ (account_id خالی = قالب)
# ---------------------------------------------------------------------------
DEFAULT_PROP_RULE_TEMPLATES = [
    (PropRuleType.MAX_DAILY_LOSS, None, 5.0, "حداکثر ضرر مجاز روزانه (درصد از موجودی)"),
    (PropRuleType.MAX_TOTAL_DRAWDOWN, None, 10.0, "حداکثر افت سرمایه کل مجاز"),
    (PropRuleType.CONSISTENCY_RULE, None, None, "قانون ثبات سود بین روزها"),
    (PropRuleType.MAX_TRADES_PER_DAY, 5, None, "حداکثر تعداد معامله در هر روز"),
    (PropRuleType.WEEKEND_HOLDING_RESTRICTION, None, None, "ممنوعیت نگه‌داشتن پوزیشن باز تا آخر هفته"),
    (PropRuleType.NEWS_TRADING_RESTRICTION, None, None, "محدودیت معامله در بازه اخبار پرتاثیر"),
]


def seed_prop_rule_templates(db: Session) -> None:
    created = 0
    for rule_type, threshold_value, threshold_percent, description in DEFAULT_PROP_RULE_TEMPLATES:
        exists = (
            db.query(PropRule)
            .filter_by(rule_type=rule_type, is_template=True, account_id=None)
            .first()
        )
        if exists:
            continue
        db.add(
            PropRule(
                account_id=None,
                rule_type=rule_type,
                threshold_value=threshold_value,
                threshold_percent=threshold_percent,
                is_template=True,
                config={"description": description},
            )
        )
        created += 1
    if created:
        logger.info("قالب‌های پیش‌فرض قوانین پراپ ایجاد شدند (%d مورد جدید)", created)


def run_seed() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    db = SessionLocal()
    try:
        seed_sections_and_fields(db)
        seed_checklist(db)
        seed_ui_tabs(db)
        seed_theme(db)
        seed_mistake_tags(db)
        seed_prop_rule_templates(db)
        db.commit()
        logger.info("✅ Seed با موفقیت کامل شد")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
