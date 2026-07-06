"use client";

import { useEffect, useState } from "react";
import { fetchCustomers, fetchCustomerDetail, fetchAuditLog } from "@/lib/api";
import type { Customer, CustomerDetail, AuditRecord } from "@/lib/types";
import StatCard from "@/components/StatCard";
import CustomerSidebar from "@/components/CustomerSidebar";
import CustomerProfileCard from "@/components/CustomerProfileCard";
import TicketHistoryList from "@/components/TicketHistoryList";

export default function DashboardPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<CustomerDetail | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchCustomers(), fetchAuditLog()])
      .then(([customerData, auditData]) => {
        setCustomers(customerData);
        setAuditLogs(auditData);
        if (customerData.length > 0) setSelectedId(customerData[0].customer_id);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    setDetail(null);
    fetchCustomerDetail(selectedId)
      .then(setDetail)
      .catch(console.error);
  }, [selectedId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="h-8 w-8 rounded-full border-2 border-teal-500/30 border-t-teal-500 animate-spin" />
      </div>
    );
  }

  // Compute dashboard stats from loaded data
  const totalTickets = detail?.recent_tickets.length ?? 0;
  const sensitiveTickets =
    detail?.recent_tickets.filter((t) => t.sensitivity === "high" || t.sensitivity === "medium").length ?? 0;

  // Calculate cost savings based on audited tickets
  const totalCostSaved = auditLogs.reduce((acc, log) => {
    const baseline = log.sensitivity === "low" ? 0.003 : 0.050;
    const actual = log.estimated_cost_usd;
    const saved = Math.max(0, baseline - actual);
    return acc + saved;
  }, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">
          Dashboard
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          Compliance-aware AI support agent — customer overview
        </p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard
          title="Tickets Processed"
          value={totalTickets}
          subtitle="Recent customer tickets"
          icon="🎫"
          accentColor="from-teal-500 to-emerald-500"
        />
        <StatCard
          title="Sensitive Tickets"
          value={sensitiveTickets}
          subtitle="Medium + High sensitivity"
          icon="🛡️"
          accentColor="from-amber-500 to-orange-500"
        />
        <StatCard
          title="Est. Cost Saved"
          value={`$${totalCostSaved.toFixed(2)}`}
          subtitle="Via local model routing"
          icon="💰"
          accentColor="from-violet-500 to-purple-500"
        />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Customer Sidebar */}
        <div className="lg:col-span-3">
          <CustomerSidebar
            customers={customers}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
        </div>

        {/* Customer Detail */}
        <div className="lg:col-span-9 space-y-4">
          {detail ? (
            <>
              <CustomerProfileCard customer={detail} />
              <TicketHistoryList tickets={detail.recent_tickets} />
            </>
          ) : (
            <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-10 text-center">
              <div className="h-6 w-6 rounded-full border-2 border-teal-500/30 border-t-teal-500 animate-spin mx-auto" />
              <p className="mt-3 text-sm text-slate-500">Loading customer details…</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
