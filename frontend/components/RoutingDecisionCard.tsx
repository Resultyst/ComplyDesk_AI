import type { Routing } from "@/lib/types";
import Badge from "./Badge";

interface RoutingDecisionCardProps {
  routing: Routing;
}

export default function RoutingDecisionCard({ routing }: RoutingDecisionCardProps) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          🔀 Routing Decision
        </h3>
        <Badge label={routing.route_type} variant={routing.route_type} />
      </div>

      <div className="space-y-2.5">
        <InfoRow label="Provider" value={routing.selected_provider} />
        <InfoRow label="Model" value={routing.selected_model} />
        <div>
          <p className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">Reason</p>
          <p className="mt-0.5 text-xs text-slate-300 leading-relaxed">{routing.reason}</p>
        </div>
      </div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">{label}</span>
      <span className="text-xs text-white font-mono bg-white/[0.04] px-2 py-0.5 rounded">{value}</span>
    </div>
  );
}
