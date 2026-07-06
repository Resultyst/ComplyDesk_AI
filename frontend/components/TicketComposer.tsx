"use client";

import { useState } from "react";

interface TicketComposerProps {
  onSubmit: (text: string) => void;
  isLoading: boolean;
  disabled?: boolean;
}

export default function TicketComposer({ onSubmit, isLoading, disabled }: TicketComposerProps) {
  const [text, setText] = useState("");

  const handleSubmit = () => {
    if (text.trim() && !isLoading) {
      onSubmit(text.trim());
    }
  };

  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
      <div className="mb-3">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          New Ticket
        </h3>
      </div>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Describe the customer's issue…"
        disabled={disabled || isLoading}
        rows={4}
        className="w-full rounded-lg border border-white/[0.08] bg-white/[0.03] px-3 py-2.5 text-sm text-white placeholder-slate-600 outline-none transition-all focus:border-teal-500/50 focus:ring-1 focus:ring-teal-500/20 resize-none disabled:opacity-50"
      />
      <div className="mt-3 flex items-center justify-between">
        <p className="text-[11px] text-slate-600">
          {text.length > 0 ? `${text.length} chars` : "Type a support ticket message"}
        </p>
        <button
          onClick={handleSubmit}
          disabled={!text.trim() || isLoading || disabled}
          className="rounded-lg bg-gradient-to-r from-teal-600 to-emerald-600 px-4 py-1.5 text-xs font-semibold text-white shadow-lg shadow-teal-500/20 transition-all hover:shadow-teal-500/40 hover:brightness-110 disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none"
        >
          {isLoading ? (
            <span className="flex items-center gap-1.5">
              <span className="h-3 w-3 rounded-full border-2 border-white/30 border-t-white animate-spin" />
              Processing…
            </span>
          ) : (
            "Process Ticket"
          )}
        </button>
      </div>
    </div>
  );
}
