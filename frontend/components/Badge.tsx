interface BadgeProps {
  label: string;
  variant?: "low" | "medium" | "high" | "local" | "cloud" | "default";
}

const variantStyles: Record<string, string> = {
  low: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  medium: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  high: "bg-red-500/15 text-red-400 border-red-500/30",
  local: "bg-violet-500/15 text-violet-400 border-violet-500/30",
  cloud: "bg-sky-500/15 text-sky-400 border-sky-500/30",
  default: "bg-slate-500/15 text-slate-400 border-slate-500/30",
};

export default function Badge({ label, variant = "default" }: BadgeProps) {
  const style = variantStyles[variant] || variantStyles.default;
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${style} tracking-wide uppercase`}
    >
      {label}
    </span>
  );
}
