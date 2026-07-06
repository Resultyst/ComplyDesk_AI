import type { TicketProcessResponse } from "@/lib/types";

interface ResponseCardProps {
  response: TicketProcessResponse;
}

export default function ResponseCard({ response }: ResponseCardProps) {
  return (
    <div className="rounded-xl border border-teal-500/20 bg-teal-500/[0.04] p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-semibold text-teal-400 uppercase tracking-wider">
          AI Response
        </h3>
        <span className="font-mono text-[11px] text-slate-500">{response.ticket_id}</span>
      </div>
      <p className="text-sm text-slate-200 leading-relaxed">
        {response.response_text}
      </p>
      <div className="mt-3 pt-3 border-t border-white/[0.06] flex items-center gap-4 text-[11px] text-slate-500">
        <span>Customer: {response.customer_id}</span>
        <span>·</span>
        <span>Audit: {response.audit.audit_id}</span>
      </div>
    </div>
  );
}
