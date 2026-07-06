import type { TicketSummary } from "@/lib/types";
import Badge from "./Badge";

interface TicketHistoryListProps {
  tickets: TicketSummary[];
}

const statusColors: Record<string, string> = {
  open: "text-amber-400",
  resolved: "text-emerald-400",
  pending: "text-sky-400",
};

export default function TicketHistoryList({ tickets }: TicketHistoryListProps) {
  if (tickets.length === 0) {
    return (
      <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-6 text-center text-sm text-slate-500">
        No tickets found.
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] overflow-hidden">
      <div className="border-b border-white/[0.06] px-4 py-3">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Recent Tickets
        </h3>
      </div>
      <div className="divide-y divide-white/[0.04]">
        {tickets.map((t) => (
          <div key={t.ticket_id} className="px-4 py-3 hover:bg-white/[0.02] transition-colors">
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-white truncate">{t.subject}</p>
                <p className="mt-0.5 text-xs text-slate-500 line-clamp-1">{t.summary}</p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <Badge label={t.sensitivity} variant={t.sensitivity as "low" | "medium" | "high"} />
              </div>
            </div>
            <div className="mt-1.5 flex items-center gap-3 text-[11px] text-slate-500">
              <span className="font-mono">{t.ticket_id}</span>
              <span>·</span>
              <span className={statusColors[t.status] || "text-slate-400"}>
                {t.status}
              </span>
              <span>·</span>
              <span>{new Date(t.created_at).toLocaleDateString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
