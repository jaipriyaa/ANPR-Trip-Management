import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import { 
  Activity, 
  Layers, 
  Clock, 
  AlertTriangle, 
  Archive, 
  Database, 
  CheckCircle2, 
  RefreshCw,
  Sliders,
  Filter,
  ArrowUpRight
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function PipelineDashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/pipeline/statistics`);
      if (res.ok) {
        setStats(await res.json());
      }
    } catch (err) {
      console.error('Failed to fetch pipeline stats:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 10000); // 10s auto-refresh
    return () => clearInterval(interval);
  }, []);

  const triggerCleanup = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/cleanup`, { method: 'POST' });
      if (res.ok) {
        alert('Pipeline cleanup & duplicate removal executed!');
        fetchStats();
      }
    } catch (err) {
      console.error('Failed to trigger cleanup:', err);
    }
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-[#f2f2f2] text-[#1a3b45] font-sans">
      <Header title="Enterprise Data Engineering Pipeline Dashboard" subtitle="Real-time operational data processing stream: AI duplicate removal, entry/exit matching, overstay scans, and archival retention" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Header Action Bar */}
        <div className="flex items-center justify-between bg-white rounded-xl p-4 border border-[#c8d8e4] backdrop-blur-md">
          <div className="flex items-center gap-3">
            <Activity className="w-5 h-5 text-cyan-400" />
            <div>
              <h2 className="text-sm font-bold text-[#1a3b45]">Live Data Pipeline Status</h2>
              <p className="text-xs text-[#5c7885]">Stream Status: <span className="text-emerald-400 font-mono font-bold">ONLINE & AGGREGATING</span></p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={triggerCleanup}
              className="px-3 py-1.5 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 border border-emerald-500/40 rounded-xl text-xs font-bold font-sans flex items-center gap-2"
            >
              <Sliders className="w-3.5 h-3.5" /> Run Duplicate Cleanup & Aggregation
            </button>
            <button
              onClick={fetchStats}
              className="p-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl text-[#5c7885] hover:text-[#1a3b45]"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* 1. Main Pipeline KPI Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-white rounded-xl p-3 border border-purple-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Duplicates Removed</p>
            <p className="text-2xl font-extrabold text-purple-300 font-mono mt-1">{stats?.duplicate_events_removed ?? 0}</p>
            <p className="text-[10px] text-purple-400/80 font-mono mt-0.5">30s Window Suppression</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-emerald-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Matched Entry/Exit</p>
            <p className="text-2xl font-extrabold text-emerald-400 font-mono mt-1">{stats?.entry_exit_pairs ?? 0}</p>
            <p className="text-[10px] text-emerald-400/80 font-mono mt-0.5">Stay Durations Computed</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-amber-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Late Arrival Cases</p>
            <p className="text-2xl font-extrabold text-amber-400 font-mono mt-1">{stats?.late_arrivals_count ?? 0}</p>
            <p className="text-[10px] text-amber-400/80 font-mono mt-0.5">Schedule Variance</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-rose-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Overstay Violations</p>
            <p className="text-2xl font-extrabold text-rose-400 font-mono mt-1">{stats?.overstay_vehicles_count ?? 0}</p>
            <p className="text-[10px] text-rose-400/80 font-mono mt-0.5">&gt;120 mins Factory Stay</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-cyan-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">OCR Retraining Samples</p>
            <p className="text-2xl font-extrabold text-cyan-400 font-mono mt-1">{stats?.ocr_feedback_count ?? 0}</p>
            <p className="text-[10px] text-cyan-400/80 font-mono mt-0.5">Feedback Dataset</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-[#c8d8e4] backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Archive Jobs Executed</p>
            <p className="text-2xl font-extrabold text-[#1a3b45] font-mono mt-1">{stats?.archive_jobs_count ?? 0}</p>
            <p className="text-[10px] text-[#5c7885]/80 font-mono mt-0.5">180 Days Policy</p>
          </div>
        </div>

        {/* 2. Today's Factory Movement Flow Card */}
        <div className="bg-white rounded-xl border border-[#c8d8e4] p-5 space-y-4 backdrop-blur-md">
          <h3 className="text-xs font-bold text-[#1a3b45] uppercase tracking-wider flex items-center gap-2">
            <Layers className="w-4 h-4 text-cyan-400" /> Today's Factory Operational Flow Summary
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono">
            <div className="bg-[#f2f2f2] p-4 rounded-xl border border-[#c8d8e4] flex items-center justify-between">
              <div>
                <span className="text-[#5c7885] text-xs block font-sans">Vehicles Entered Today</span>
                <span className="text-2xl font-extrabold text-emerald-400">{stats?.todays_entered ?? 0}</span>
              </div>
              <ArrowUpRight className="w-8 h-8 text-emerald-500/40" />
            </div>

            <div className="bg-[#f2f2f2] p-4 rounded-xl border border-[#c8d8e4] flex items-center justify-between">
              <div>
                <span className="text-[#5c7885] text-xs block font-sans">Vehicles Exited Today</span>
                <span className="text-2xl font-extrabold text-blue-400">{stats?.todays_exited ?? 0}</span>
              </div>
              <ArrowUpRight className="w-8 h-8 text-blue-500/40" />
            </div>

            <div className="bg-[#f2f2f2] p-4 rounded-xl border border-[#c8d8e4] flex items-center justify-between">
              <div>
                <span className="text-[#5c7885] text-xs block font-sans">Vehicles Currently Inside</span>
                <span className="text-2xl font-extrabold text-cyan-400">{stats?.todays_inside ?? 0}</span>
              </div>
              <Activity className="w-8 h-8 text-cyan-500/40" />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
