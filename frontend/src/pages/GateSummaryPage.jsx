import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import { Video, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function GateSummaryPage() {
  const [gateSums, setGateSums] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const limit = 15;

  const fetchGateSummaries = async () => {
    setLoading(true);
    try {
      const skip = (page - 1) * limit;
      const res = await fetch(`${API_BASE_URL}/gate-summary?skip=${skip}&limit=${limit}`);
      if (res.ok) {
        const json = await res.json();
        setGateSums(json.items || []);
        setTotal(json.total || 0);
      }
    } catch (err) {
      console.error('Failed to fetch gate summaries:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGateSummaries();
  }, [page]);

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-slate-950 text-slate-100 font-sans">
      <Header title="Daily Per-Gate Performance Summaries" subtitle="Per-gate traffic analysis, average processing times, stay durations, and ANPR recognition accuracy" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        <div className="flex items-center justify-between bg-slate-900/80 rounded-xl p-4 border border-slate-800 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <Video className="w-5 h-5 text-cyan-400" />
            <h2 className="text-sm font-bold text-white">Daily Per-Gate Aggregates</h2>
          </div>

          <button
            onClick={fetchGateSummaries}
            className="p-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-400 hover:text-white"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Master Gate Summary Table */}
        <div className="bg-slate-900/80 rounded-xl border border-slate-800 overflow-hidden backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-mono">
                <tr>
                  <th className="p-4">Date</th>
                  <th className="p-4">Gate Name</th>
                  <th className="p-4">Entered</th>
                  <th className="p-4">Exited</th>
                  <th className="p-4">Avg Processing Time</th>
                  <th className="p-4">Avg Stay Duration</th>
                  <th className="p-4">Alerts Raised</th>
                  <th className="p-4">Accuracy %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan="8" className="p-8 text-center text-slate-500 font-sans">Loading gate summaries...</td>
                  </tr>
                ) : gateSums.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="p-8 text-center text-slate-500 font-sans">No gate summary records found.</td>
                  </tr>
                ) : (
                  gateSums.map((gs) => (
                    <tr key={gs.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="p-4 font-bold text-cyan-400">{gs.summary_date}</td>
                      <td className="p-4 font-bold text-white font-sans">{gs.gate_name}</td>
                      <td className="p-4 text-emerald-400 font-bold">{gs.vehicles_entered}</td>
                      <td className="p-4 text-blue-400 font-bold">{gs.vehicles_exited}</td>
                      <td className="p-4 text-purple-300">{gs.avg_processing_time_secs}s</td>
                      <td className="p-4 text-slate-300">{gs.avg_stay_duration_mins} mins</td>
                      <td className="p-4 text-amber-400">{gs.alerts_generated}</td>
                      <td className="p-4 text-emerald-400 font-bold">{gs.recognition_accuracy}%</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="p-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400 font-sans">
            <span>Page {page} of {totalPages} ({total} total gate summary records)</span>
            <div className="flex items-center gap-2 font-mono">
              <button
                disabled={page <= 1}
                onClick={() => setPage(p => p - 1)}
                className="p-1.5 bg-slate-950 border border-slate-800 rounded-lg disabled:opacity-40 hover:bg-slate-800"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage(p => p + 1)}
                className="p-1.5 bg-slate-950 border border-slate-800 rounded-lg disabled:opacity-40 hover:bg-slate-800"
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
