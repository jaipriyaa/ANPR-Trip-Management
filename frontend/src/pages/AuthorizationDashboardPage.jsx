import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import { 
  ShieldCheck, 
  ShieldAlert, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Clock, 
  RefreshCw, 
  UserCheck, 
  Check, 
  X,
  FileCheck
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function AuthorizationDashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchDashboard = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/authorization/dashboard`);
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch (err) {
      console.error('Failed to fetch authorization dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
    const interval = setInterval(fetchDashboard, 5000); // 5s auto-refresh
    return () => clearInterval(interval);
  }, []);

  const handleManualOverride = async (decision_id, action) => {
    const remarks = prompt(`Enter Security Officer remarks for ${action}:`, "Security Officer Gate Verification Approved");
    if (remarks === null) return;

    try {
      const res = await fetch(`${API_BASE_URL}/manual-approval`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          decision_id,
          action,
          officer_name: "Major Rajesh Verma",
          remarks,
        }),
      });

      if (res.ok) {
        fetchDashboard();
      }
    } catch (err) {
      console.error('Failed to process manual override:', err);
    }
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-[#f2f2f2] text-[#1a3b45] font-sans">
      <Header title="Authorization Engine & Control Room" subtitle="Automated AI vehicle gate access verification, active security watchlist hits, and manual officer approval queue" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Header Action Bar */}
        <div className="flex items-center justify-between bg-white rounded-xl p-4 border border-[#c8d8e4] backdrop-blur-md">
          <div className="flex items-center gap-3">
            <ShieldCheck className="w-5 h-5 text-cyan-400" />
            <div>
              <h2 className="text-sm font-bold text-[#1a3b45]">Central Security Decision Engine</h2>
              <p className="text-xs text-[#5c7885]">Live 5s auto-refresh active</p>
            </div>
          </div>

          <button
            onClick={fetchDashboard}
            className="px-3 py-1.5 bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl text-[#2b6777] hover:text-[#1a3b45] text-xs flex items-center gap-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Refresh Decision Queue
          </button>
        </div>

        {/* 1. KPI Cards Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-white rounded-xl p-3 border border-emerald-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Authorized Today</p>
            <p className="text-2xl font-extrabold text-emerald-400 font-mono mt-1">{data?.authorized_today ?? 0}</p>
            <p className="text-[10px] text-emerald-400/80 font-mono mt-0.5">Access Granted</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-rose-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Denied Today</p>
            <p className="text-2xl font-extrabold text-rose-400 font-mono mt-1">{data?.denied_today ?? 0}</p>
            <p className="text-[10px] text-rose-400/80 font-mono mt-0.5">Gate Blocked</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-purple-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Manual Approvals</p>
            <p className="text-2xl font-extrabold text-purple-300 font-mono mt-1">{data?.manual_approvals ?? 0}</p>
            <p className="text-[10px] text-purple-400/80 font-mono mt-0.5">Officer Override</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-amber-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Unknown Vehicles</p>
            <p className="text-2xl font-extrabold text-amber-300 font-mono mt-1">{data?.unknown_vehicles ?? 0}</p>
            <p className="text-[10px] text-amber-400/80 font-mono mt-0.5">Unregistered</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-rose-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Watchlist Hits</p>
            <p className="text-2xl font-extrabold text-rose-400 font-mono mt-1">{data?.watchlist_hits ?? 0}</p>
            <p className="text-[10px] text-rose-400/80 font-mono mt-0.5">Security Flagged</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-cyan-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Whitelist Count</p>
            <p className="text-2xl font-extrabold text-cyan-400 font-mono mt-1">{data?.whitelist_count ?? 0}</p>
            <p className="text-[10px] text-cyan-400/80 font-mono mt-0.5">Active Authorized</p>
          </div>
        </div>

        {/* 2. Security Officer Manual Override Queue */}
        <div className="bg-white rounded-xl border border-[#c8d8e4] p-5 space-y-4 backdrop-blur-md">
          <div className="flex items-center justify-between border-b border-[#c8d8e4] pb-3">
            <div>
              <h3 className="text-sm font-bold text-[#1a3b45] uppercase tracking-wider flex items-center gap-2">
                <UserCheck className="w-4 h-4 text-cyan-400" /> Security Officer Manual Approval Queue
              </h3>
              <p className="text-xs text-[#5c7885] mt-0.5">Pending unregistered & manual verification vehicle access requests</p>
            </div>
          </div>

          <div className="space-y-3 font-mono text-xs">
            {!data?.pending_manual_queue || data.pending_manual_queue.length === 0 ? (
              <p className="text-[#5c7885] text-center py-6 font-sans">No pending manual review requests at gate.</p>
            ) : (
              data.pending_manual_queue.map((item) => (
                <div key={item.id} className="bg-[#f2f2f2] p-4 rounded-xl border border-[#c8d8e4] flex items-center justify-between flex-wrap gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-cyan-400">{item.plate_number}</span>
                      <span className="px-2 py-0.5 bg-amber-500/10 text-amber-400 font-bold text-[10px] rounded border border-amber-500/30">
                        {item.decision}
                      </span>
                    </div>
                    <p className="text-[#2b6777] font-sans text-xs">{item.reason}</p>
                    <p className="text-[10px] text-[#5c7885]">Timestamp: {new Date(item.time).toLocaleString()}</p>
                  </div>

                  <div className="flex items-center gap-2 font-sans">
                    <button
                      onClick={() => handleManualOverride(item.id, 'MANUAL_APPROVAL')}
                      className="px-4 py-2 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 border border-emerald-500/40 rounded-xl font-bold text-xs flex items-center gap-1.5 transition-all"
                    >
                      <Check className="w-4 h-4" /> Approve Entry
                    </button>
                    <button
                      onClick={() => handleManualOverride(item.id, 'MANUAL_REJECTION')}
                      className="px-4 py-2 bg-rose-500/20 hover:bg-rose-500/30 text-rose-400 border border-rose-500/40 rounded-xl font-bold text-xs flex items-center gap-1.5 transition-all"
                    >
                      <X className="w-4 h-4" /> Reject Entry
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
