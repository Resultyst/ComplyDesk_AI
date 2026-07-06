import type { CustomerDetail } from "@/lib/types";
import Badge from "./Badge";

interface CustomerProfileCardProps {
  customer: CustomerDetail;
}

export default function CustomerProfileCard({ customer }: CustomerProfileCardProps) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-5">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-lg font-semibold text-white">{customer.name}</h2>
          <p className="mt-0.5 text-xs text-slate-500">{customer.customer_id}</p>
        </div>
        <Badge label={customer.plan_tier} variant={customer.plan_tier.toLowerCase() === "enterprise" ? "high" : customer.plan_tier.toLowerCase() === "pro" ? "medium" : "default"} />
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3">
        <InfoRow label="Account Type" value={customer.account_type} />
        <InfoRow label="Channel" value={customer.preferred_channel} />
        <InfoRow label="Last Ticket" value={new Date(customer.last_ticket_at).toLocaleDateString()} />
        <InfoRow label="Interactions" value={String(customer.memory_summary.total_interactions)} />
      </div>

      {customer.memory_summary.key_preferences.length > 0 && (
        <div className="mt-4 border-t border-white/[0.06] pt-3">
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
            Key Preferences
          </p>
          <ul className="space-y-1">
            {customer.memory_summary.key_preferences.map((pref, i) => (
              <li key={i} className="text-xs text-slate-300 flex items-start gap-1.5">
                <span className="text-teal-500 mt-0.5">›</span>
                {pref}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">{label}</p>
      <p className="mt-0.5 text-sm text-slate-300 capitalize">{value}</p>
    </div>
  );
}
