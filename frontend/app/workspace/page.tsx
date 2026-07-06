"use client";

import { useEffect, useState } from "react";
import { fetchCustomers, fetchCustomerDetail, processTicket } from "@/lib/api";
import type { Customer, CustomerDetail, TicketProcessResponse } from "@/lib/types";
import CustomerSidebar from "@/components/CustomerSidebar";
import TicketComposer from "@/components/TicketComposer";
import ResponseCard from "@/components/ResponseCard";
import MemoryPanel from "@/components/MemoryPanel";
import SensitivityCard from "@/components/SensitivityCard";
import RoutingDecisionCard from "@/components/RoutingDecisionCard";
import MetricsCard from "@/components/MetricsCard";

export default function WorkspacePage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<CustomerDetail | null>(null);
  const [response, setResponse] = useState<TicketProcessResponse | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    fetchCustomers().then((data) => {
      setCustomers(data);
      if (data.length > 0) setSelectedId(data[0].customer_id);
    });
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    setDetail(null);
    setResponse(null);
    fetchCustomerDetail(selectedId).then(setDetail);
  }, [selectedId]);

  const handleProcessTicket = async (text: string) => {
    if (!selectedId) return;
    setIsProcessing(true);
    setResponse(null);
    try {
      const result = await processTicket({
        customer_id: selectedId,
        ticket_text: text,
        use_demo_mode: true,
      });
      setResponse(result);
    } catch (err) {
      console.error("Failed to process ticket:", err);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">
          Workspace
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          Process support tickets with AI-powered sensitivity routing
        </p>
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Selector + Composer + Response */}
        <div className="lg:col-span-5 space-y-4">
          <CustomerSidebar
            customers={customers}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
          <TicketComposer
            onSubmit={handleProcessTicket}
            isLoading={isProcessing}
            disabled={!selectedId}
          />
          {response && <ResponseCard response={response} />}
        </div>

        {/* Right Column: Analysis Panels */}
        <div className="lg:col-span-7 space-y-4">
          {response ? (
            <>
              <MemoryPanel memory={response.memory} />
              <SensitivityCard sensitivity={response.sensitivity} />
              <RoutingDecisionCard routing={response.routing} />
              <MetricsCard metrics={response.metrics} />
            </>
          ) : (
            <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-16 text-center">
              <div className="text-4xl mb-4 opacity-30">⚡</div>
              <h3 className="text-sm font-medium text-slate-400">
                No ticket processed yet
              </h3>
              <p className="mt-1 text-xs text-slate-600">
                Select a customer and submit a ticket to see the AI analysis
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
