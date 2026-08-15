"""تایپ‌های کمکی مشترک برای تعریف ستون‌ها.

`PortableEnum` یک Enum پایتونی را به‌صورت VARCHAR + CHECK constraint
پیاده‌سازی می‌کند (نه native PostgreSQL ENUM) تا در معماری انتزاعی
ذخیره‌سازی (پشتیبانی احتمالی از SQLite طبق پرامپت مادر) هم قابل استفاده
باشد و افزودن مقادیر جدید به Enum نیازمند ALTER TYPE نباشد.
"""
from enum import Enum
from typing import Type

from sqlalchemy import Enum as SAEnum


def portable_enum(enum_cls: Type[Enum], name: str) -> SAEnum:
    return SAEnum(
        enum_cls,
        name=name,
        native_enum=False,
        values_callable=lambda obj: [e.value for e in obj],
        validate_strings=True,
    )
