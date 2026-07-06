import type { AuditRecord } from "@/lib/types";
import Badge from "./Badge";

interface AuditTableProps {
  records: AuditRecord[];
}

export default function AuditTable({ records }: AuditTableProps) {
  if (records.length === 0) {
    return (
      <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-10 text-center text-sm text-slate-500">
        No audit records found.
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-white/[0.06]">
              {["Timestamp", "Ticket ID", "Customer", "Sensitivity", "Model", "Routing Reason", "Memory", "Latency", "Cost"].map(
                (h) => (
                  <th
                    key={h}
                    className="px-4 py-3 text-[10px] font-semibold text-slate-500 uppercase tracking-wider whitespace-nowrap"
                  >
                    {h}
                  </th>
                )
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {records.map((r) => (
              <tr
                key={r.audit_id}
                className="hover:bg-white/[0.02] transition-colors"
              >
                <td className="px-4 py-3 text-xs text-slate-400 whitespace-nowrap">
                  {new Date(r.timestamp).toLocaleString()}
                </td>
                <td className="px-4 py-3 text-xs text-white font-mono whitespace-nowrap">
                  {r.ticket_id}
                </td>
                <td className="px-4 py-3 text-xs text-slate-300 whitespace-nowrap">
                  {r.customer_id}
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <Badge label={r.sensitivity} variant={r.sensitivity as "low" | "medium" | "high"} />
                </td>
                <td className="px-4 py-3 text-xs text-white font-mono whitespace-nowrap">
                  {r.model_selected}
                </td>
                <td className="px-4 py-3 text-xs text-slate-400 max-w-[200px] truncate">
                  {r.routing_reason}
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <span className={`inline-flex h-5 w-5 items-center justify-center rounded text-[10px] ${r.memory_used ? "bg-emerald-500/15 text-emerald-400" : "bg-slate-500/15 text-slate-500"}`}>
                    {r.memory_used ? "✓" : "—"}
                  </span>
                </td>
                <td className="px-4 py-3 text-xs text-slate-300 font-mono whitespace-nowrap">
                  {r.latency_ms}ms
                </td>
                <td className="px-4 py-3 text-xs text-slate-300 font-mono whitespace-nowrap">
                  ${r.estimated_cost_usd.toFixed(4)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
