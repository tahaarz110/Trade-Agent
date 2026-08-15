"""تمام مدل‌های ORM باید اینجا ایمپورت شوند تا روی `Base.metadata` ثبت
شده و Alembic autogenerate و `Base.metadata.create_all` آن‌ها را ببینند.
"""
from app.models.account import Account
from app.models.symbol import Symbol
from app.models.trade import Trade
from app.models.attachment import Attachment
from app.models.field import FieldSection, FieldDefinition, FieldOption, TradeFieldValue
from app.models.checklist import ChecklistTemplate, ChecklistItem, TradeChecklistAnswer
from app.models.ai import AIInsight, AIJob
from app.models.import_batch import ImportBatch
from app.models.ui import UITab, ThemeSetting
from app.models.audit import AuditLog

from app.models.insights import (
    FeatureSnapshot,
    InsightSegment,
    InsightMetric,
    InsightPattern,
    InsightValidation,
)
from app.models.behavior import BehaviorScore, DisciplineScore
from app.models.mistakes import MistakeTag, MistakeCost, Lesson, LessonLink
from app.models.experiments import Hypothesis, Experiment, ExperimentResult, PreTradeCheck
from app.models.prop import PropRule, PropViolation
from app.models.alerts import Alert, ReportRun
from app.models.text_analytics import TextTerm, TextTheme

__all__ = [
    "Account",
    "Symbol",
    "Trade",
    "Attachment",
    "FieldSection",
    "FieldDefinition",
    "FieldOption",
    "TradeFieldValue",
    "ChecklistTemplate",
    "ChecklistItem",
    "TradeChecklistAnswer",
    "AIInsight",
    "AIJob",
    "ImportBatch",
    "UITab",
    "ThemeSetting",
    "AuditLog",
    "FeatureSnapshot",
    "InsightSegment",
    "InsightMetric",
    "InsightPattern",
    "InsightValidation",
    "BehaviorScore",
    "DisciplineScore",
    "MistakeTag",
    "MistakeCost",
    "Lesson",
    "LessonLink",
    "Hypothesis",
    "Experiment",
    "ExperimentResult",
    "PreTradeCheck",
    "PropRule",
    "PropViolation",
    "Alert",
    "ReportRun",
    "TextTerm",
    "TextTheme",
]
