// تایپ‌های مشترک منطبق بر schemaهای Pydantic بک‌اند (apps/api/app/schemas)

export type FieldType =
  | "number"
  | "price"
  | "percent"
  | "short_text"
  | "long_text"
  | "single_select"
  | "multi_select"
  | "radio"
  | "checkbox"
  | "boolean"
  | "date"
  | "datetime"
  | "time"
  | "symbol"
  | "url"
  | "file";

export interface FieldOption {
  id: string;
  field_id: string;
  value: string;
  label: string;
  color: string | null;
  sort_order: number;
  is_active: boolean;
}

export interface FieldDefinition {
  id: string;
  section_id: string;
  slug: string;
  title: string;
  field_type: FieldType;
  placeholder: string | null;
  help_text: string | null;
  default_value: string | null;
  unit: string | null;
  is_required: boolean;
  is_system: boolean;
  is_active: boolean;
  rtl_display: boolean;
  ltr_input: boolean;
  show_in_form: boolean;
  show_in_table: boolean;
  show_in_detail: boolean;
  filterable: boolean;
  analytic_enabled: boolean;
  ai_enabled: boolean;
  validation_rules: Record<string, unknown> | null;
  sort_order: number;
  options: FieldOption[];
}

export interface FieldSection {
  id: string;
  key: string;
  title: string;
  description: string | null;
  is_system: boolean;
  is_active: boolean;
  sort_order: number;
}

export interface SectionWithFields extends FieldSection {
  fields: FieldDefinition[];
}

export type AccountType = "demo" | "real" | "prop";

export interface Account {
  id: string;
  name: string;
  account_type: AccountType;
  broker: string | null;
  currency: string;
  initial_balance: number | null;
  current_balance: number | null;
  leverage: number | null;
  is_active: boolean;
  notes: string | null;
}

export interface Symbol {
  id: string;
  name: string;
  display_name: string | null;
  asset_class: string | null;
  pip_size: number | null;
  contract_size: number | null;
  is_active: boolean;
}

export type TradeDirection = "buy" | "sell";
export type TradeStatus = "open" | "closed" | "cancelled";

export interface Trade {
  id: string;
  account_id: string;
  symbol_id: string;
  direction: TradeDirection;
  status: TradeStatus;
  entry_time: string;
  exit_time: string | null;
  duration_minutes: number | null;
  entry_price: number;
  exit_price: number | null;
  stop_loss: number | null;
  take_profit: number | null;
  volume: number;
  commission: number;
  swap: number;
  gross_profit: number | null;
  net_profit: number | null;
  risk_amount: number | null;
  risk_percent: number | null;
  r_multiple: number | null;
  pips: number | null;
  needs_review: boolean;
  review_status: string | null;
  created_at: string;
  updated_at: string;
}

export interface TradeFieldValueRead {
  field_slug: string;
  field_title: string;
  field_type: string;
  value: unknown;
}

export interface TradeDetail extends Trade {
  custom_fields: TradeFieldValueRead[];
}

export interface Attachment {
  id: string;
  trade_id: string;
  file_path: string;
  thumbnail_path: string | null;
  file_name: string;
  mime_type: string | null;
  file_size: number | null;
  caption: string | null;
  sort_order: number;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export type CustomFieldValues = Record<string, unknown>;
