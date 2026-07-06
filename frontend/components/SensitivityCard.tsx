import type { Sensitivity } from "@/lib/types";
import Badge from "./Badge";

interface SensitivityCardProps {
  sensitivity: Sensitivity;
}

const levelIcons: Record<string, string> = {
  low: "🟢",
  medium: "🟡",
  high: "🔴",
};

export default function SensitivityCard({ sensitivity }: SensitivityCardProps) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          🛡️ Sensitivity
        </h3>
        <span className="text-lg">{levelIcons[sensitivity.level] || "⚪"}</span>
      </div>

      <div className="flex items-center gap-2 mb-3">
        <Badge label={sensitivity.level} variant={sensitivity.level} />
        <span className="text-xs text-slate-500">classification</span>
      </div>

      <p className="text-xs text-slate-300 leading-relaxed mb-3">
        {sensitivity.reasoning}
      </p>

      <div className="flex flex-wrap gap-1.5">
        {sensitivity.risk_tags.map((tag, i) => (
          <span
            key={i}
            className="rounded-md bg-white/[0.04] px-2 py-0.5 text-[10px] text-slate-400 font-mono"
          >
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
}
