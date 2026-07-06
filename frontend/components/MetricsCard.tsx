import type { Metrics } from "@/lib/types";

interface MetricsCardProps {
  metrics: Metrics;
}

export default function MetricsCard({ metrics }: MetricsCardProps) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
        📈 Metrics
      </h3>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">
            Latency
          </p>
          <p className="mt-1 text-xl font-bold text-white">
            {metrics.latency_ms}
            <span className="text-xs font-normal text-slate-500 ml-0.5">ms</span>
          </p>
          <div className="mt-1.5 h-1 rounded-full bg-white/[0.06] overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-teal-500 to-emerald-500 transition-all duration-500"
              style={{ width: `${Math.min((metrics.latency_ms / 1000) * 100, 100)}%` }}
            />
          </div>
        </div>
        <div>
          <p className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">
            Est. Cost
          </p>
          <p className="mt-1 text-xl font-bold text-white">
            ${metrics.estimated_cost_usd.toFixed(4)}
          </p>
          <p className="mt-1.5 text-[10px] text-slate-500">
            {metrics.estimated_cost_usd === 0 ? "Local model — no cost" : "Cloud inference cost"}
          </p>
        </div>
      </div>
    </div>
  );
}
