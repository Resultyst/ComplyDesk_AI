"use client";

import { useEffect, useState } from "react";
import { fetchAuditLog } from "@/lib/api";
import type { AuditRecord } from "@/lib/types";
import AuditTable from "@/components/AuditTable";
import StatCard from "@/components/StatCard";

export default function AuditPage() {
  const [records, setRecords] = useState<AuditRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAuditLog()
      .then(setRecords)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="h-8 w-8 rounded-full border-2 border-teal-500/30 border-t-teal-500 animate-spin" />
      </div>
    );
  }

  const totalRecords = records.length;
  const localRouted = records.filter((r) => r.model_selected.startsWith("Ollama")).length;
  const cloudRouted = records.filter((r) => r.model_selected.startsWith("Groq")).length;
  const avgLatency = totalRecords > 0
    ? Math.round(records.reduce((sum, r) => sum + r.latency_ms, 0) / totalRecords)
    : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">
          Audit Log
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          Complete audit trail of AI routing decisions for compliance review
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <StatCard
          title="Total Decisions"
          value={totalRecords}
          icon="📋"
          accentColor="from-teal-500 to-emerald-500"
        />
        <StatCard
          title="Local Routed"
          value={localRouted}
          subtitle="High/medium sensitivity"
          icon="🔒"
          accentColor="from-violet-500 to-purple-500"
        />
        <StatCard
          title="Cloud Routed"
          value={cloudRouted}
          subtitle="Low sensitivity"
          icon="☁️"
          accentColor="from-sky-500 to-blue-500"
        />
        <StatCard
          title="Avg Latency"
          value={`${avgLatency}ms`}
          icon="⚡"
          accentColor="from-amber-500 to-orange-500"
        />
      </div>

      {/* Audit Table */}
      <AuditTable records={records} />
    </div>
  );
}
