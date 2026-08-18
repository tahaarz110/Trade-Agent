import type {
  Account,
  Attachment,
  ChecklistItem,
  ChecklistTemplate,
  FieldDefinition,
  FieldOption,
  FieldSection,
  FieldType,
  Page,
  Symbol,
  ThemeSetting,
  Trade,
  TradeDetail,
  UITab,
} from "./types";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface HealthResponse {
  status: string;
  app: string;
  env: string;
  time: string;
  database: string;
  low_resource_mode: boolean;
  ai_narrator_enabled: boolean;
}

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, detail: unknown) {
    const message =
      typeof detail === "string"
        ? detail
        : (detail as { detail?: string })?.detail ?? "خطای ناشناخته از سرور";
    super(typeof message === "string" ? message : JSON.stringify(message));
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers:
      options.body && !(options.body instanceof FormData)
        ? { "Content-Type": "application/json", ...options.headers }
        : options.headers,
    cache: "no-store",
  });

  if (!res.ok) {
    let detail: unknown = null;
    try {
      detail = await res.json();
    } catch {
      detail = await res.text();
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) {
    return undefined as T;
  }
  return res.json();
}

export async function fetchHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

// --- Accounts ------------------------------------------------------------------
export async function fetchAccounts(page = 1, pageSize = 100): Promise<Page<Account>> {
  return request(`/accounts?page=${page}&page_size=${pageSize}`);
}

// --- Symbols -------------------------------------------------------------------
export async function fetchSymbols(page = 1, pageSize = 200): Promise<Page<Symbol>> {
  return request(`/symbols?page=${page}&page_size=${pageSize}`);
}

// --- Field sections / definitions ------------------------------------------------
export async function fetchFieldSections(includeInactive = false): Promise<FieldSection[]> {
  return request(`/field-sections?include_inactive=${includeInactive}`);
}

export async function fetchFieldDefinitions(
  includeInactive = false
): Promise<FieldDefinition[]> {
  return request(`/field-definitions?include_inactive=${includeInactive}`);
}

export async function fetchFieldOptions(fieldId: string): Promise<FieldOption[]> {
  return request(`/field-definitions/${fieldId}/options`);
}

// --- Trades --------------------------------------------------------------------
export interface TradeListFilters {
  account_id?: string;
  symbol_id?: string;
  direction?: string;
  status?: string;
  review_status?: string;
  date_from?: string;
  date_to?: string;
  field_id?: string;
  field_value?: string;
}

export async function fetchTrades(
  page: number,
  pageSize: number,
  filters: TradeListFilters = {}
): Promise<Page<Trade>> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== "" && value !== null) {
      params.set(key, String(value));
    }
  });
  return request(`/trades?${params.toString()}`);
}

export async function fetchTradeDetail(tradeId: string): Promise<TradeDetail> {
  return request(`/trades/${tradeId}`);
}

export interface TradeCreatePayload {
  account_id: string;
  symbol_id: string;
  direction: string;
  status?: string;
  entry_time: string;
  exit_time?: string | null;
  entry_price: number | string;
  exit_price?: number | string | null;
  stop_loss?: number | string | null;
  take_profit?: number | string | null;
  volume: number | string;
  commission?: number | string;
  swap?: number | string;
  custom_fields?: Record<string, unknown>;
}

export async function createTrade(payload: TradeCreatePayload): Promise<Trade> {
  return request("/trades", { method: "POST", body: JSON.stringify(payload) });
}

export async function updateTrade(
  tradeId: string,
  payload: Partial<TradeCreatePayload>
): Promise<Trade> {
  return request(`/trades/${tradeId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

// --- Attachments --------------------------------------------------------------
export async function fetchAttachments(tradeId: string): Promise<Attachment[]> {
  return request(`/trades/${tradeId}/attachments`);
}

export async function uploadAttachment(
  tradeId: string,
  file: File,
  caption?: string
): Promise<Attachment> {
  const form = new FormData();
  form.append("file", file);
  if (caption) form.append("caption", caption);
  return request(`/trades/${tradeId}/attachments`, { method: "POST", body: form });
}

export async function deleteAttachment(attachmentId: string): Promise<void> {
  return request(`/attachments/${attachmentId}`, { method: "DELETE" });
}

export function attachmentUrl(relativePath: string): string {
  // بک‌اند پیوست‌ها را از مسیر امن /attachments/files (نسبی به ATTACHMENT_DIR)
  // serve می‌کند؛ هرگز مسیر مطلق فایل‌سیستم سرور در پاسخ API وجود ندارد.
  return `${API_BASE_URL}/attachments/files/${relativePath}`;
}

// --- Accounts (مدیریت کامل) --------------------------------------------------------
export async function createAccount(payload: Partial<Account>): Promise<Account> {
  return request("/accounts", { method: "POST", body: JSON.stringify(payload) });
}
export async function updateAccount(id: string, payload: Partial<Account>): Promise<Account> {
  return request(`/accounts/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
}
export async function deleteAccount(id: string): Promise<void> {
  return request(`/accounts/${id}`, { method: "DELETE" });
}

// --- Symbols (مدیریت کامل) ---------------------------------------------------------
export async function createSymbol(payload: Partial<Symbol>): Promise<Symbol> {
  return request("/symbols", { method: "POST", body: JSON.stringify(payload) });
}
export async function updateSymbol(id: string, payload: Partial<Symbol>): Promise<Symbol> {
  return request(`/symbols/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
}
export async function deleteSymbol(id: string): Promise<void> {
  return request(`/symbols/${id}`, { method: "DELETE" });
}

// --- Field manager (سکشن/فیلد/گزینه) -------------------------------------------------
export interface ReorderItem {
  id: string;
  sort_order: number;
}

export async function createFieldSection(payload: {
  key: string;
  title: string;
  description?: string | null;
  sort_order?: number;
}): Promise<FieldSection> {
  return request("/field-sections", { method: "POST", body: JSON.stringify(payload) });
}
export async function updateFieldSection(
  id: string,
  payload: Partial<FieldSection>
): Promise<FieldSection> {
  return request(`/field-sections/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
}
export async function toggleFieldSection(id: string, enable: boolean): Promise<FieldSection> {
  return request(`/field-sections/${id}/${enable ? "enable" : "disable"}`, { method: "POST" });
}
export async function reorderFieldSections(items: ReorderItem[]): Promise<FieldSection[]> {
  return request("/field-sections/reorder", { method: "POST", body: JSON.stringify({ items }) });
}
export async function deleteFieldSection(id: string): Promise<void> {
  return request(`/field-sections/${id}`, { method: "DELETE" });
}

export async function createFieldDefinition(payload: {
  section_id: string;
  slug: string;
  title: string;
  field_type: FieldType;
  is_required?: boolean;
  ltr_input?: boolean;
  show_in_form?: boolean;
  show_in_table?: boolean;
  show_in_detail?: boolean;
  filterable?: boolean;
  analytic_enabled?: boolean;
  ai_enabled?: boolean;
  unit?: string | null;
  help_text?: string | null;
  sort_order?: number;
  options?: string[];
}): Promise<FieldDefinition> {
  return request("/field-definitions", { method: "POST", body: JSON.stringify(payload) });
}
export async function updateFieldDefinition(
  id: string,
  payload: Partial<FieldDefinition>
): Promise<FieldDefinition> {
  return request(`/field-definitions/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
}
export async function toggleFieldDefinition(id: string, enable: boolean): Promise<FieldDefinition> {
  return request(`/field-definitions/${id}/${enable ? "enable" : "disable"}`, { method: "POST" });
}
export async function reorderFieldDefinitions(items: ReorderItem[]): Promise<FieldDefinition[]> {
  return request("/field-definitions/reorder", { method: "POST", body: JSON.stringify({ items }) });
}
export async function deleteFieldDefinition(id: string): Promise<void> {
  return request(`/field-definitions/${id}`, { method: "DELETE" });
}

export async function createFieldOption(payload: {
  field_id: string;
  value: string;
  label: string;
  color?: string | null;
  sort_order?: number;
}): Promise<FieldOption> {
  return request("/field-options", { method: "POST", body: JSON.stringify(payload) });
}
export async function updateFieldOption(
  id: string,
  payload: Partial<FieldOption>
): Promise<FieldOption> {
  return request(`/field-options/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
}
export async function toggleFieldOption(id: string, enable: boolean): Promise<FieldOption> {
  return request(`/field-options/${id}/${enable ? "enable" : "disable"}`, { method: "POST" });
}
export async function reorderFieldOptions(
  fieldId: string,
  items: ReorderItem[]
): Promise<FieldOption[]> {
  return request(`/field-definitions/${fieldId}/options/reorder`, {
    method: "POST",
    body: JSON.stringify({ items }),
  });
}
export async function deleteFieldOption(id: string): Promise<void> {
  return request(`/field-options/${id}`, { method: "DELETE" });
}

// --- Checklist manager -------------------------------------------------------------
export async function fetchChecklistTemplates(): Promise<ChecklistTemplate[]> {
  return request("/checklist-templates?include_inactive=true");
}
export async function createChecklistTemplate(payload: {
  name: string;
  description?: string | null;
}): Promise<ChecklistTemplate> {
  return request("/checklist-templates", { method: "POST", body: JSON.stringify(payload) });
}
export async function toggleChecklistTemplate(
  id: string,
  enable: boolean
): Promise<ChecklistTemplate> {
  return request(`/checklist-templates/${id}/${enable ? "enable" : "disable"}`, { method: "POST" });
}
export async function deleteChecklistTemplate(id: string): Promise<void> {
  return request(`/checklist-templates/${id}`, { method: "DELETE" });
}
export async function fetchChecklistItems(templateId: string): Promise<ChecklistItem[]> {
  return request(`/checklist-templates/${templateId}/items`);
}
export async function createChecklistItem(payload: {
  template_id: string;
  title: string;
  description?: string | null;
  is_required?: boolean;
  sort_order?: number;
}): Promise<ChecklistItem> {
  return request("/checklist-templates/items", { method: "POST", body: JSON.stringify(payload) });
}
export async function reorderChecklistItems(
  templateId: string,
  items: ReorderItem[]
): Promise<ChecklistItem[]> {
  return request(`/checklist-templates/${templateId}/items/reorder`, {
    method: "POST",
    body: JSON.stringify({ items }),
  });
}
export async function deleteChecklistItem(id: string): Promise<void> {
  return request(`/checklist-templates/items/${id}`, { method: "DELETE" });
}

// --- Theme ---------------------------------------------------------------------
export async function fetchTheme(): Promise<ThemeSetting> {
  return request("/theme-settings");
}
export async function updateTheme(payload: Partial<ThemeSetting>): Promise<ThemeSetting> {
  return request("/theme-settings", { method: "PATCH", body: JSON.stringify(payload) });
}

// --- UI Tabs -----------------------------------------------------------------------
export async function fetchUITabs(): Promise<UITab[]> {
  return request("/ui-tabs");
}
export async function createUITab(payload: {
  key: string;
  title: string;
  icon?: string | null;
  sort_order?: number;
}): Promise<UITab> {
  return request("/ui-tabs", { method: "POST", body: JSON.stringify(payload) });
}
export async function toggleUITab(id: string, visible: boolean): Promise<UITab> {
  return request(`/ui-tabs/${id}/${visible ? "show" : "hide"}`, { method: "POST" });
}
export async function reorderUITabs(items: ReorderItem[]): Promise<UITab[]> {
  return request("/ui-tabs/reorder", { method: "POST", body: JSON.stringify({ items }) });
}
export async function deleteUITab(id: string): Promise<void> {
  return request(`/ui-tabs/${id}`, { method: "DELETE" });
}

