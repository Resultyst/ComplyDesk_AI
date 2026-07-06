// ──────────────────────────────────────────────
// ComplyDesk — API client
// HTTP calls to FastAPI backend
// ──────────────────────────────────────────────

import type {
  Customer,
  CustomerDetail,
  TicketProcessRequest,
  TicketProcessResponse,
  AuditRecord,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

/** Fetch all customers. */
export function fetchCustomers(): Promise<Customer[]> {
  return apiFetch<Customer[]>("/customers/");
}

/** Fetch a single customer with memory + recent tickets. */
export function fetchCustomerDetail(customerId: string): Promise<CustomerDetail> {
  return apiFetch<CustomerDetail>(`/customers/${customerId}`);
}

/** Submit a ticket for processing. */
export function processTicket(request: TicketProcessRequest): Promise<TicketProcessResponse> {
  return apiFetch<TicketProcessResponse>("/tickets/process", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

/** Fetch all audit log records. */
export function fetchAuditLog(): Promise<AuditRecord[]> {
  return apiFetch<AuditRecord[]>("/audit/");
}
