import type { Memory } from "@/lib/types";

interface MemoryPanelProps {
  memory: Memory;
}

export default function MemoryPanel({ memory }: MemoryPanelProps) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          🧠 Memory Context
        </h3>
        <span className={`inline-flex items-center gap-1 text-[11px] font-medium ${memory.used ? "text-emerald-400" : "text-slate-500"}`}>
          <span className={`h-1.5 w-1.5 rounded-full ${memory.used ? "bg-emerald-400" : "bg-slate-600"}`} />
          {memory.used ? "Active" : "Inactive"}
        </span>
      </div>

      <p className="text-xs text-slate-400 mb-3">{memory.summary}</p>

      <div className="space-y-2">
        {memory.items.map((item, i) => (
          <div
            key={i}
            className="rounded-lg border border-white/[0.04] bg-white/[0.02] px-3 py-2"
          >
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold text-teal-400">{item.key}</span>
              <span className="text-[10px] text-slate-600">{item.source}</span>
            </div>
            <p className="mt-0.5 text-xs text-slate-300">{item.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
