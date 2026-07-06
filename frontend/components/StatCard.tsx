interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: string;
  accentColor?: string;
}

export default function StatCard({
  title,
  value,
  subtitle,
  icon,
  accentColor = "from-teal-500 to-emerald-500",
}: StatCardProps) {
  return (
    <div className="relative overflow-hidden rounded-xl border border-white/[0.06] bg-white/[0.03] p-5 backdrop-blur-sm transition-all duration-300 hover:border-white/[0.12] hover:bg-white/[0.05] group">
      <div className={`absolute top-0 left-0 h-[2px] w-full bg-gradient-to-r ${accentColor} opacity-60 group-hover:opacity-100 transition-opacity`} />
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            {title}
          </p>
          <p className="mt-2 text-2xl font-bold text-white tracking-tight">
            {value}
          </p>
          {subtitle && (
            <p className="mt-1 text-xs text-slate-500">{subtitle}</p>
          )}
        </div>
        {icon && (
          <span className="text-2xl opacity-40 group-hover:opacity-60 transition-opacity">
            {icon}
          </span>
        )}
      </div>
    </div>
  );
}
