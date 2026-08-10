import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import { Archive, RefreshCw, Play, ShieldCheck, ChevronLeft, ChevronRight } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function ArchiveManagerPage() {
  const [jobs, setJobs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [retentionDays, setRetentionDays] = useState(180);
  const [page, setPage] = useState(1);
  const limit = 10;

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const skip = (page - 1) * limit;
      const res = await fetch(`${API_BASE_URL}/archive/jobs?skip=${skip}&limit=${limit}`);
      if (res.ok) {
        const json = await res.json();
        setJobs(json.items || []);
        setTotal(json.total || 0);
      }
    } catch (err) {
      console.error('Failed to fetch archive jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [page]);

  const triggerArchiveJob = async () => {
    if (!window.confirm(`Run data retention archival for records older than ${retentionDays} days? Active trips and inside vehicles will be safely preserved.`)) return;

    try {
      const res = await fetch(`${API_BASE_URL}/archive/run?retention_days=${retentionDays}`, { method: 'POST' });
      if (res.ok) {
        alert('Data Archival job completed successfully!');
        fetchJobs();
      }
    } catch (err) {
      console.error('Failed to trigger archive job:', err);
    }
  };

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-slate-950 text-slate-100 font-sans">
      <Header title="Retention Policy & Data Archival Manager" subtitle="Automated data lifecycle management archiving completed trips and movement logs older than retention threshold" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        <div className="flex items-center justify-between bg-slate-900/80 rounded-xl p-4 border border-slate-800 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <Archive className="w-5 h-5 text-cyan-400" />
            <h2 className="text-sm font-bold text-white">Archival & Retention Policy</h2>
          </div>

          <div className="flex items-center gap-3 text-xs font-sans">
            <span className="text-slate-400">Retention Threshold:</span>
            <select
              value={retentionDays}
              onChange={(e) => setRetentionDays(Number(e.target.value))}
              className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-white font-semibold focus:outline-none focus:border-cyan-500"
            >
              <option value={90}>90 Days</option>
              <option value={180}>180 Days (6 Months)</option>
              <option value={365}>365 Days (1 Year)</option>
            </select>

            <button
              onClick={triggerArchiveJob}
              className="px-3 py-1.5 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-xl flex items-center gap-2 shadow-lg shadow-cyan-500/20"
            >
              <Play className="w-3.5 h-3.5 fill-current" /> Trigger Manual Archival Job
            </button>

            <button
              onClick={fetchJobs}
              className="p-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-400 hover:text-white"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Archival Job Execution Log Table */}
        <div className="bg-slate-900/80 rounded-xl border border-slate-800 overflow-hidden backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-mono">
                <tr>
                  <th className="p-4">Job Name</th>
                  <th className="p-4">Target Tables</th>
                  <th className="p-4">Records Archived</th>
                  <th className="p-4">Retention Threshold</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan="6" className="p-8 text-center text-slate-500 font-sans">Loading archive jobs...</td>
                  </tr>
                ) : jobs.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="p-8 text-center text-slate-500 font-sans">No archival jobs executed yet.</td>
                  </tr>
                ) : (
                  jobs.map((j) => (
                    <tr key={j.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="p-4 font-bold text-white font-sans">{j.job_name}</td>
                      <td className="p-4 text-purple-300">{j.target_table}</td>
                      <td className="p-4 text-emerald-400 font-bold">{j.records_archived}</td>
                      <td className="p-4 text-slate-300">{j.retention_days} Days</td>
                      <td className="p-4">
                        <span className="px-2.5 py-1 rounded text-[10px] font-bold border bg-emerald-500/10 text-emerald-400 border-emerald-500/30">
                          ● {j.status}
                        </span>
                      </td>
                      <td className="p-4 text-slate-400">{j.completed_at ? new Date(j.completed_at).toLocaleString() : '-'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="p-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400 font-sans">
            <span>Page {page} of {totalPages} ({total} total archive jobs)</span>
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
