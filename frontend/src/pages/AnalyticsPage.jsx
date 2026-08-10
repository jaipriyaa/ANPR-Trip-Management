import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import { 
  BarChart2, 
  TrendingUp, 
  Clock, 
  Truck, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Activity, 
  Camera, 
  ShieldAlert, 
  RefreshCw,
  PieChart,
  Calendar
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function AnalyticsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/admin/dashboard`);
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch (err) {
      console.error('Failed to fetch analytics dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 5000); // 5s auto-refresh
    return () => clearInterval(interval);
  }, []);

  const kpis = data?.kpis || {};
  const charts = data?.charts || {};

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-[#f2f2f2] text-[#1a3b45] font-sans">
      <Header title="Analytics Dashboard" subtitle="Real-time operational KPIs, vehicle volume trends, gate distribution, and AI recognition performance metrics" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Header Action Bar */}
        <div className="flex items-center justify-between bg-white rounded-xl p-4 border border-[#c8d8e4] backdrop-blur-md">
          <div className="flex items-center gap-3">
            <BarChart2 className="w-5 h-5 text-cyan-400" />
            <div>
              <h2 className="text-sm font-bold text-[#1a3b45]">Executive Control Room Analytics</h2>
              <p className="text-xs text-[#5c7885]">Live 5s auto-refresh active</p>
            </div>
          </div>

          <button
            onClick={fetchAnalytics}
            className="px-3 py-1.5 bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl text-[#2b6777] hover:text-[#1a3b45] text-xs flex items-center gap-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Refresh Metrics
          </button>
        </div>

        {/* 1. Real-Time KPI Cards Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
          <div className="bg-white rounded-xl p-3 border border-emerald-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Entered Today</p>
            <p className="text-2xl font-extrabold text-emerald-400 font-mono mt-1">{kpis.vehicles_entered_today ?? 0}</p>
            <p className="text-[10px] text-emerald-400/80 font-mono mt-0.5">Gate Entries</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-blue-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Exited Today</p>
            <p className="text-2xl font-extrabold text-blue-400 font-mono mt-1">{kpis.vehicles_exited_today ?? 0}</p>
            <p className="text-[10px] text-blue-400/80 font-mono mt-0.5">Gate Dispatches</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-cyan-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Currently Inside</p>
            <p className="text-2xl font-extrabold text-cyan-400 font-mono mt-1">{kpis.vehicles_currently_inside ?? 0}</p>
            <p className="text-[10px] text-cyan-400/80 font-mono mt-0.5">Active Premises</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-purple-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Total Trips</p>
            <p className="text-2xl font-extrabold text-purple-300 font-mono mt-1">{kpis.total_trips ?? 0}</p>
            <p className="text-[10px] text-purple-400/80 font-mono mt-0.5">Dispatched</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-amber-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Avg Stay Duration</p>
            <p className="text-lg font-bold text-amber-300 font-mono mt-1.5">{kpis.avg_stay_duration_formatted || '1h 45m'}</p>
            <p className="text-[10px] text-amber-400/80 font-mono mt-0.5">Turnaround</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-emerald-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">OCR Accuracy</p>
            <p className="text-2xl font-extrabold text-emerald-400 font-mono mt-1">{kpis.recognition_accuracy_pct ?? 99.2}%</p>
            <p className="text-[10px] text-emerald-400/80 font-mono mt-0.5">Multi-Frame AI</p>
          </div>
        </div>

        {/* 2. Interactive Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Chart 1: Hourly Vehicle Traffic Volume */}
          <div className="bg-white rounded-xl border border-[#c8d8e4] p-5 backdrop-blur-md space-y-4">
            <h3 className="text-xs font-bold text-[#1a3b45] uppercase tracking-wider flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-cyan-400" /> Hourly Vehicle Traffic (Entries vs Exits)
            </h3>

            <div className="space-y-3 pt-2">
              {(charts.hourly_counts || []).map((h, i) => (
                <div key={i} className="space-y-1 font-mono text-xs">
                  <div className="flex justify-between text-[#5c7885] text-[11px]">
                    <span>{h.hour}</span>
                    <span className="text-emerald-400">{h.entries} in / <span className="text-blue-400">{h.exits} out</span></span>
                  </div>
                  <div className="w-full bg-[#f2f2f2] rounded-full h-3 flex overflow-hidden border border-[#c8d8e4]">
                    <div className="bg-emerald-500 h-full transition-all" style={{ width: `${Math.min(100, h.entries * 3)}%` }} title={`Entries: ${h.entries}`} />
                    <div className="bg-blue-500 h-full transition-all" style={{ width: `${Math.min(100, h.exits * 3)}%` }} title={`Exits: ${h.exits}`} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Chart 2: Gate Volume Distribution */}
          <div className="bg-white rounded-xl border border-[#c8d8e4] p-5 backdrop-blur-md space-y-4">
            <h3 className="text-xs font-bold text-[#1a3b45] uppercase tracking-wider flex items-center gap-2">
              <Camera className="w-4 h-4 text-purple-400" /> Traffic Volume by Factory Gate
            </h3>

            <div className="space-y-3 pt-2">
              {(charts.gate_counts || []).map((g, i) => (
                <div key={i} className="space-y-1 font-mono text-xs">
                  <div className="flex justify-between text-[#2b6777] text-[11px]">
                    <span className="font-bold">{g.gate}</span>
                    <span className="text-cyan-400 font-bold">{g.count} Vehicles</span>
                  </div>
                  <div className="w-full bg-[#f2f2f2] rounded-full h-3 overflow-hidden border border-[#c8d8e4]">
                    <div className="bg-gradient-to-r from-purple-500 to-cyan-500 h-full transition-all" style={{ width: `${Math.min(100, g.count * 10)}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Chart 3: Top Transporters by Dispatched Trips */}
          <div className="bg-white rounded-xl border border-[#c8d8e4] p-5 backdrop-blur-md space-y-4">
            <h3 className="text-xs font-bold text-[#1a3b45] uppercase tracking-wider flex items-center gap-2">
              <Truck className="w-4 h-4 text-amber-400" /> Top Transporters Trip Distribution
            </h3>

            <div className="space-y-3 pt-2">
              {(charts.transporter_trips || []).map((t, i) => (
                <div key={i} className="space-y-1 font-mono text-xs">
                  <div className="flex justify-between text-[#2b6777] text-[11px]">
                    <span>{t.transporter}</span>
                    <span className="text-amber-400 font-bold">{t.trips} Trips</span>
                  </div>
                  <div className="w-full bg-[#f2f2f2] rounded-full h-3 overflow-hidden border border-[#c8d8e4]">
                    <div className="bg-amber-500 h-full transition-all" style={{ width: `${Math.min(100, t.trips * 15)}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Chart 4: Recognition Accuracy Trend */}
          <div className="bg-white rounded-xl border border-[#c8d8e4] p-5 backdrop-blur-md space-y-4">
            <h3 className="text-xs font-bold text-[#1a3b45] uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4 text-emerald-400" /> Weekly AI Recognition Accuracy Trend (%)
            </h3>

            <div className="grid grid-cols-7 gap-2 pt-4 text-center font-mono">
              {(charts.accuracy_trend || []).map((a, i) => (
                <div key={i} className="space-y-2">
                  <div className="h-24 flex items-end justify-center bg-[#f2f2f2] rounded-lg p-1 border border-[#c8d8e4]">
                    <div
                      className="w-full bg-emerald-500/80 rounded transition-all"
                      style={{ height: `${(a.accuracy - 90) * 10}%` }}
                      title={`${a.day}: ${a.accuracy}%`}
                    />
                  </div>
                  <p className="text-[10px] text-[#5c7885]">{a.day}</p>
                  <p className="text-[10px] font-bold text-emerald-400">{a.accuracy}%</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
