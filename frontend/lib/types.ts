// ──────────────────────────────────────────────
// ComplyDesk — TypeScript type definitions
// Mirrors the Pydantic schemas on the backend
// ──────────────────────────────────────────────

export interface Customer {
  customer_id: string;
  name: string;
  plan_tier: string;
  preferred_channel: string;
  account_type: string;
  last_ticket_at: string;
}

export interface MemoryItem {
  key: string;
  value: string;
  source: string;
  timestamp: string;
}

export interface MemorySummary {
  total_interactions: number;
  key_preferences: string[];
  items: MemoryItem[];
}

export interface TicketSummary {
  ticket_id: string;
  subject: string;
  status: string;
  sensitivity: string;
  created_at: string;
  summary: string;
}

export interface CustomerDetail extends Customer {
  memory_summary: MemorySummary;
  recent_tickets: TicketSummary[];
}

export interface Memory {
  used: boolean;
  items: MemoryItem[];
  summary: string;
}

export interface Sensitivity {
  level: "low" | "medium" | "high";
  risk_tags: string[];
  reasoning: string;
}

export interface Routing {
  selected_provider: string;
  selected_model: string;
  route_type: "local" | "cloud";
  reason: string;
}

export interface Metrics {
  latency_ms: number;
  estimated_cost_usd: number;
}

export interface AuditEntry {
  audit_id: string;
  timestamp: string;
  decision_summary: string;
}

export interface TicketProcessRequest {
  customer_id: string;
  ticket_text: string;
  use_demo_mode: boolean;
}

export interface TicketProcessResponse {
  ticket_id: string;
  customer_id: string;
  response_text: string;
  memory: Memory;
  sensitivity: Sensitivity;
  routing: Routing;
  metrics: Metrics;
  audit: AuditEntry;
}

export interface AuditRecord {
  audit_id: string;
  timestamp: string;
  ticket_id: string;
  customer_id: string;
  sensitivity: string;
  model_selected: string;
  routing_reason: string;
  memory_used: boolean;
  latency_ms: number;
  estimated_cost_usd: number;
}
