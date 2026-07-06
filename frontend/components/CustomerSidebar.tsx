"use client";

import type { Customer } from "@/lib/types";
import Badge from "./Badge";

interface CustomerSidebarProps {
  customers: Customer[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export default function CustomerSidebar({
  customers,
  selectedId,
  onSelect,
}: CustomerSidebarProps) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] overflow-hidden">
      <div className="border-b border-white/[0.06] px-4 py-3">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Customers
        </h3>
      </div>
      <div className="divide-y divide-white/[0.04]">
        {customers.map((c) => (
          <button
            key={c.customer_id}
            onClick={() => onSelect(c.customer_id)}
            className={`w-full text-left px-4 py-3 transition-all duration-200 ${
              selectedId === c.customer_id
                ? "bg-teal-500/10 border-l-2 border-l-teal-500"
                : "hover:bg-white/[0.03] border-l-2 border-l-transparent"
            }`}
          >
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-white">{c.name}</p>
              <Badge
                label={c.plan_tier}
                variant={
                  c.plan_tier.toLowerCase() === "enterprise"
                    ? "high"
                    : c.plan_tier.toLowerCase() === "pro"
                    ? "medium"
                    : "default"
                }
              />
            </div>
            <div className="mt-1 flex items-center gap-2 text-xs text-slate-500">
              <span>{c.customer_id}</span>
              <span>·</span>
              <span>{c.account_type}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
