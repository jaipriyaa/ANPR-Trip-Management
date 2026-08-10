import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import { 
  FileCheck, 
  Search, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function GateDecisionsPage() {
  const [decisions, setDecisions] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const limit = 15;

  const fetchDecisions = async () => {
    setLoading(true);
    try {
      const skip = (page - 1) * limit;
      const res = await fetch(`${API_BASE_URL}/gate-decisions?skip=${skip}&limit=${limit}`);
      if (res.ok) {
        const json = await res.json();
        setDecisions(json.items || []);
        setTotal(json.total || 0);
      }
    } catch (err) {
      console.error('Failed to fetch gate decisions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDecisions();
  }, [page]);

  const totalPages = Math.ceil(total / limit) || 1;

  const filtered = decisions.filter(d =>
    !searchTerm ||
    d.recognized_plate?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.decision?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.reason?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-slate-950 text-slate-100 font-sans">
      <Header title="Gate Decisions Audit History" subtitle="Complete audit log of all automated AI and Security Officer gate decisions (ALLOW, DENY, MANUAL_APPROVAL, MANUAL_REJECTION)" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Search & Status Bar */}
        <div className="flex items-center justify-between bg-slate-900/80 rounded-xl p-4 border border-slate-800 backdrop-blur-md">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search Plate, Decision, Reason..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white font-mono placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="text-xs text-slate-400 font-mono">
            Total Gate Decision Logs: <span className="text-cyan-400 font-bold">{total}</span>
          </div>
        </div>

        {/* Master Decisions Table */}
        <div className="bg-slate-900/80 rounded-xl border border-slate-800 overflow-hidden backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-mono">
                <tr>
                  <th className="p-4">Recognized Plate</th>
                  <th className="p-4">Decision</th>
                  <th className="p-4">Decision Reason</th>
                  <th className="p-4">AI Confidence</th>
                  <th className="p-4">Decision By</th>
                  <th className="p-4">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan="6" className="p-8 text-center text-slate-500 font-sans">Loading decision logs...</td>
                  </tr>
                ) : filtered.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="p-8 text-center text-slate-500 font-sans">No gate decisions recorded.</td>
                  </tr>
                ) : (
                  filtered.map((d) => (
                    <tr key={d.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="p-4 font-bold text-cyan-400">{d.recognized_plate}</td>
                      <td className="p-4">
                        <span className={`px-2.5 py-1 rounded text-[10px] font-bold border ${
                          d.decision === 'ALLOW' || d.decision === 'MANUAL_APPROVAL'
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                            : d.decision === 'UNKNOWN_VEHICLE' || d.decision === 'MANUAL_REVIEW'
                            ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                            : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                        }`}>
                          ● {d.decision}
                        </span>
                      </td>
                      <td className="p-4 font-sans text-slate-200">{d.reason}</td>
                      <td className="p-4 text-emerald-400 font-bold">{int((d.confidence || 0.95) * 100)}%</td>
                      <td className="p-4 text-purple-300 font-sans">{d.decision_by}</td>
                      <td className="p-4 text-slate-400 text-[11px]">{d.decision_time ? new Date(d.decision_time).toLocaleString() : '-'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="p-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400 font-sans">
            <span>Page {page} of {totalPages} ({total} total decisions)</span>
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

function int(val) {
  return Math.round(val);
}
