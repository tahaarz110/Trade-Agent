from __future__ import annotations

import uuid
from pathlib import Path
from typing import BinaryIO, Optional

from PIL import Image
from sqlalchemy.orm import Session

from app.config import settings
from app.models.attachment import Attachment
from app.repositories.attachment import AttachmentRepository
from app.repositories.trade import TradeRepository
from app.services import NotFoundError, ValidationAppError

THUMBNAIL_SIZE = (320, 320)
IMAGE_MIME_PREFIXES = ("image/",)


class AttachmentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AttachmentRepository(db)
        self.trade_repo = TradeRepository(db)

    def _trade_dir(self, trade_id: uuid.UUID) -> Path:
        d = Path(settings.attachment_dir) / str(trade_id)
        d.mkdir(parents=True, exist_ok=True)
        return d

    def upload(
        self,
        *,
        trade_id: uuid.UUID,
        file_name: str,
        content_type: Optional[str],
        file_obj: BinaryIO,
        caption: Optional[str] = None,
    ) -> Attachment:
        trade = self.trade_repo.get(trade_id)
        if not trade:
            raise NotFoundError("معامله", trade_id)

        safe_name = f"{uuid.uuid4().hex}_{Path(file_name).name}"
        dest_dir = self._trade_dir(trade_id)
        dest_path = dest_dir / safe_name

        data = file_obj.read()
        if not data:
            raise ValidationAppError("فایل ارسالی خالی است")

        dest_path.write_bytes(data)
        file_size = len(data)

        thumbnail_path: Optional[str] = None
        is_image = bool(content_type) and content_type.startswith(IMAGE_MIME_PREFIXES)
        if is_image:
            thumbnail_path = self._generate_thumbnail(dest_path, dest_dir, safe_name)

        attachment = Attachment(
            trade_id=trade_id,
            file_path=str(dest_path),
            thumbnail_path=thumbnail_path,
            file_name=file_name,
            mime_type=content_type,
            file_size=file_size,
            caption=caption,
        )
        self.repo.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)
        return attachment

    def _generate_thumbnail(self, source_path: Path, dest_dir: Path, safe_name: str) -> Optional[str]:
        """تصویر بندانگشتی ۳۲۰x۳۲۰ (حفظ نسبت ابعاد) می‌سازد. اگر فایل
        تصویر معتبر نباشد (مثلاً corrupt) بدون خطا None برمی‌گرداند تا
        آپلود اصلی fail نشود."""
        try:
            with Image.open(source_path) as img:
                img = img.convert("RGB") if img.mode not in ("RGB", "L") else img
                img.thumbnail(THUMBNAIL_SIZE)
                thumb_name = f"thumb_{safe_name.rsplit('.', 1)[0]}.jpg"
                thumb_path = dest_dir / thumb_name
                img.save(thumb_path, format="JPEG", quality=85)
                return str(thumb_path)
        except Exception:  # noqa: BLE001 - فایل تصویر نامعتبر، نادیده گرفته می‌شود
            return None

    def list_for_trade(self, trade_id: uuid.UUID) -> list[Attachment]:
        if not self.trade_repo.get(trade_id):
            raise NotFoundError("معامله", trade_id)
        return (
            self.db.query(Attachment)
            .filter_by(trade_id=trade_id)
            .order_by(Attachment.sort_order.asc(), Attachment.created_at.asc())
            .all()
        )

    def delete(self, attachment_id: uuid.UUID) -> None:
        attachment = self.repo.get(attachment_id)
        if not attachment:
            raise NotFoundError("پیوست", attachment_id)

        for path_str in (attachment.file_path, attachment.thumbnail_path):
            if path_str:
                Path(path_str).unlink(missing_ok=True)

        self.repo.delete(attachment)
        self.db.commit()
