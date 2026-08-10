import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import { 
  FileCheck, 
  Search, 
  Clock, 
  User, 
  ShieldAlert, 
  Activity, 
  ChevronLeft, 
  ChevronRight,
  Filter
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function AuditLogsPage() {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const limit = 15;

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const skip = (page - 1) * limit;
      const res = await fetch(`${API_BASE_URL}/admin/audit?skip=${skip}&limit=${limit}`);
      if (res.ok) {
        const json = await res.json();
        setLogs(json.items || []);
        setTotal(json.total || 0);
      }
    } catch (err) {
      console.error('Failed to fetch audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [page]);

  const totalPages = Math.ceil(total / limit) || 1;

  const filteredLogs = logs.filter(l => 
    !searchTerm || 
    l.action?.toLowerCase().includes(searchTerm.toLowerCase()) || 
    l.entity_type?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    l.ip_address?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-slate-950 text-slate-100 font-sans">
      <Header title="Security Audit Trail & Compliance Logs" subtitle="Tamper-proof audit logs recording user authentication, administrative changes, gate rule updates, and trip approvals" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Search & Action Bar */}
        <div className="flex items-center justify-between bg-slate-900/80 rounded-xl p-4 border border-slate-800 backdrop-blur-md">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search Action, Entity, IP Address..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
            />
          </div>

          <div className="text-xs text-slate-400 font-mono">
            Total Logged Audit Events: <span className="text-cyan-400 font-bold">{total}</span>
          </div>
        </div>

        {/* Audit Logs Table */}
        <div className="bg-slate-900/80 rounded-xl border border-slate-800 overflow-hidden backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-mono">
                <tr>
                  <th className="p-4">Action</th>
                  <th className="p-4">Entity Type</th>
                  <th className="p-4">Entity ID</th>
                  <th className="p-4">Audit Details</th>
                  <th className="p-4">IP Address</th>
                  <th className="p-4">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan="6" className="p-8 text-center text-slate-500 font-sans">Loading audit log events...</td>
                  </tr>
                ) : filteredLogs.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="p-8 text-center text-slate-500 font-sans">
                      <FileCheck className="w-8 h-8 mx-auto mb-2 opacity-50 text-cyan-400" />
                      No audit events found matching filters.
                    </td>
                  </tr>
                ) : (
                  filteredLogs.map((l) => (
                    <tr key={l.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="p-4 font-bold text-cyan-400">{l.action}</td>
                      <td className="p-4 font-sans text-purple-300">{l.entity_type}</td>
                      <td className="p-4 text-slate-400 text-[11px]">{l.entity_id || '-'}</td>
                      <td className="p-4 font-sans text-slate-200">
                        {l.details ? JSON.stringify(l.details) : 'Executed'}
                      </td>
                      <td className="p-4 text-slate-400">{l.ip_address}</td>
                      <td className="p-4 text-[11px] text-slate-400">{new Date(l.created_at).toLocaleString()}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="p-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400 font-sans">
            <span>Showing page {page} of {totalPages} ({total} total audit records)</span>
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
