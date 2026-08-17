import type {
  Account,
  Attachment,
  FieldDefinition,
  FieldOption,
  FieldSection,
  Page,
  Symbol,
  Trade,
  TradeDetail,
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

export function attachmentUrl(path: string): string {
  // در فاز‌های بعدی، بک‌اند یک endpoint استاتیک برای پیوست‌ها ارائه می‌دهد.
  // فعلاً مسیر خام را برمی‌گردانیم تا بعداً به‌سادگی جایگزین شود.
  return `${API_BASE_URL}/static/${path}`;
}

