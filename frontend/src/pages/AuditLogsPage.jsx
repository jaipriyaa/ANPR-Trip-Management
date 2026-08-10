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
    <div className="flex-1 flex flex-col min-w-0 bg-[#f2f2f2] text-[#1a3b45] font-sans">
      <Header title="Security Audit Trail & Compliance Logs" subtitle="Tamper-proof audit logs recording user authentication, administrative changes, gate rule updates, and trip approvals" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Search & Action Bar */}
        <div className="flex items-center justify-between bg-white rounded-xl p-4 border border-[#c8d8e4] backdrop-blur-md">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-[#5c7885] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search Action, Entity, IP Address..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl text-xs text-[#1a3b45] placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
            />
          </div>

          <div className="text-xs text-[#5c7885] font-mono">
            Total Logged Audit Events: <span className="text-cyan-400 font-bold">{total}</span>
          </div>
        </div>

        {/* Audit Logs Table */}
        <div className="bg-white rounded-xl border border-[#c8d8e4] overflow-hidden backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-[#2b6777]">
              <thead className="bg-[#f2f2f2] text-[#5c7885] uppercase text-[10px] tracking-wider border-b border-[#c8d8e4] font-mono">
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
                    <td colSpan="6" className="p-8 text-center text-[#5c7885] font-sans">Loading audit log events...</td>
                  </tr>
                ) : filteredLogs.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="p-8 text-center text-[#5c7885] font-sans">
                      <FileCheck className="w-8 h-8 mx-auto mb-2 opacity-50 text-cyan-400" />
                      No audit events found matching filters.
                    </td>
                  </tr>
                ) : (
                  filteredLogs.map((l) => (
                    <tr key={l.id} className="hover:bg-[#f0f6f8] transition-colors">
                      <td className="p-4 font-bold text-cyan-400">{l.action}</td>
                      <td className="p-4 font-sans text-purple-300">{l.entity_type}</td>
                      <td className="p-4 text-[#5c7885] text-[11px]">{l.entity_id || '-'}</td>
                      <td className="p-4 font-sans text-[#1a3b45]">
                        {l.details ? JSON.stringify(l.details) : 'Executed'}
                      </td>
                      <td className="p-4 text-[#5c7885]">{l.ip_address}</td>
                      <td className="p-4 text-[11px] text-[#5c7885]">{new Date(l.created_at).toLocaleString()}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="p-4 border-t border-[#c8d8e4] flex items-center justify-between text-xs text-[#5c7885] font-sans">
            <span>Showing page {page} of {totalPages} ({total} total audit records)</span>
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
