import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import { Calendar, RefreshCw, FileText, CheckCircle2, ChevronLeft, ChevronRight } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function DailySummaryPage() {
  const [summaries, setSummaries] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const limit = 15;

  const fetchSummaries = async () => {
    setLoading(true);
    try {
      const skip = (page - 1) * limit;
      const res = await fetch(`${API_BASE_URL}/daily-summary?skip=${skip}&limit=${limit}`);
      if (res.ok) {
        const json = await res.json();
        setSummaries(json.items || []);
        setTotal(json.total || 0);
      }
    } catch (err) {
      console.error('Failed to fetch daily summary:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummaries();
  }, [page]);

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-[#f2f2f2] text-[#1a3b45] font-sans">
      <Header title="Factory Daily Operational Summaries" subtitle="Daily aggregated metrics for vehicle traffic, completed trips, late arrivals, overstay cases, and OCR accuracy" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        <div className="flex items-center justify-between bg-white rounded-xl p-4 border border-[#c8d8e4] backdrop-blur-md">
          <div className="flex items-center gap-3">
            <Calendar className="w-5 h-5 text-cyan-400" />
            <h2 className="text-sm font-bold text-[#1a3b45]">Daily Operational Aggregates</h2>
          </div>

          <button
            onClick={fetchSummaries}
            className="p-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl text-[#5c7885] hover:text-[#1a3b45]"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Master Daily Summary Table */}
        <div className="bg-white rounded-xl border border-[#c8d8e4] overflow-hidden backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-[#2b6777]">
              <thead className="bg-[#f2f2f2] text-[#5c7885] uppercase text-[10px] tracking-wider border-b border-[#c8d8e4] font-mono">
                <tr>
                  <th className="p-4">Date</th>
                  <th className="p-4">Entered</th>
                  <th className="p-4">Exited</th>
                  <th className="p-4">Still Inside</th>
                  <th className="p-4">Trips Completed</th>
                  <th className="p-4">Late Arrivals</th>
                  <th className="p-4">Overstay Cases</th>
                  <th className="p-4">Avg Stay</th>
                  <th className="p-4">OCR Accuracy</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan="9" className="p-8 text-center text-[#5c7885] font-sans">Loading daily summaries...</td>
                  </tr>
                ) : summaries.length === 0 ? (
                  <tr>
                    <td colSpan="9" className="p-8 text-center text-[#5c7885] font-sans">No daily summary records found.</td>
                  </tr>
                ) : (
                  summaries.map((s) => (
                    <tr key={s.id} className="hover:bg-[#f0f6f8] transition-colors">
                      <td className="p-4 font-bold text-cyan-400">{s.summary_date}</td>
                      <td className="p-4 text-emerald-400 font-bold">{s.vehicles_entered}</td>
                      <td className="p-4 text-blue-400 font-bold">{s.vehicles_exited}</td>
                      <td className="p-4 text-amber-400 font-bold">{s.vehicles_still_inside}</td>
                      <td className="p-4 text-purple-300 font-bold">{s.trips_completed}</td>
                      <td className="p-4 text-amber-400">{s.late_arrivals}</td>
                      <td className="p-4 text-rose-400">{s.overstay_cases}</td>
                      <td className="p-4 text-[#2b6777]">{s.avg_stay_duration_mins} mins</td>
                      <td className="p-4 text-emerald-400 font-bold">{s.recognition_accuracy}%</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="p-4 border-t border-[#c8d8e4] flex items-center justify-between text-xs text-[#5c7885] font-sans">
            <span>Page {page} of {totalPages} ({total} total summary records)</span>
            <div className="flex items-center gap-2 font-mono">
              <button
                disabled={page <= 1}
                onClick={() => setPage(p => p - 1)}
                className="p-1.5 bg-[#f2f2f2] border border-[#c8d8e4] rounded-lg disabled:opacity-40 hover:bg-[#e8eff4]"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage(p => p + 1)}
                className="p-1.5 bg-[#f2f2f2] border border-[#c8d8e4] rounded-lg disabled:opacity-40 hover:bg-[#e8eff4]"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
