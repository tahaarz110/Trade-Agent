"""خطاهای مشترک لایه سرویس. روترها این خطاها را به HTTPException تبدیل
می‌کنند تا لایه سرویس به FastAPI وابسته نباشد."""


class NotFoundError(Exception):
    def __init__(self, entity: str, entity_id) -> None:
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"{entity} با شناسه {entity_id} یافت نشد")


class ValidationAppError(Exception):
    """خطای اعتبارسنجی سطح کسب‌وکار (متفاوت از خطای اعتبارسنجی Pydantic)."""


class ConflictError(Exception):
    """نقض یک محدودیت یکتایی/تعارض داده (مثلاً نام نماد تکراری)."""
