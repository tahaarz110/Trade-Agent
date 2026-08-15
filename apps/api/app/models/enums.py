"""Enum های اشتراکی مدل‌ها.

این مقادیر به‌صورت VARCHAR + CHECK constraint (native_enum=False) ذخیره
می‌شوند تا هم روی PostgreSQL و هم در معماری انتزاعی ذخیره‌سازی (احتمال
پشتیبانی از SQLite در آینده طبق پرامپت مادر) قابل استفاده باشند.
"""
from enum import Enum


class AccountType(str, Enum):
    DEMO = "demo"
    REAL = "real"
    PROP = "prop"


class TradeDirection(str, Enum):
    BUY = "buy"
    SELL = "sell"


class TradeStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class FieldType(str, Enum):
    NUMBER = "number"
    PRICE = "price"
    PERCENT = "percent"
    SHORT_TEXT = "short_text"
    LONG_TEXT = "long_text"
    SINGLE_SELECT = "single_select"
    MULTI_SELECT = "multi_select"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TIME = "time"
    SYMBOL = "symbol"
    URL = "url"
    FILE = "file"


class AIJobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ImportSource(str, Enum):
    MT5_PYTHON = "mt5_python"
    EA_BRIDGE = "ea_bridge"
    CSV = "csv"
    MANUAL = "manual"


class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SampleQuality(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ExperimentStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    CONCLUDED = "concluded"
    INCONCLUSIVE = "inconclusive"


class HypothesisStatus(str, Enum):
    DRAFT = "draft"
    TESTING = "testing"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class PropRuleType(str, Enum):
    MAX_DAILY_LOSS = "max_daily_loss"
    MAX_TOTAL_DRAWDOWN = "max_total_drawdown"
    CONSISTENCY_RULE = "consistency_rule"
    NEWS_TRADING_RESTRICTION = "news_trading_restriction"
    WEEKEND_HOLDING_RESTRICTION = "weekend_holding_restriction"
    MAX_TRADES_PER_DAY = "max_trades_per_day"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ReportType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SETUP = "setup"
    MISTAKE = "mistake"
    PSYCHOLOGY = "psychology"
    PROP_GUARDIAN = "prop_guardian"


class PeriodType(str, Enum):
    TRADE = "trade"
    DAY = "day"
    WEEK = "week"
