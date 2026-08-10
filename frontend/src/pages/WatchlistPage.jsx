import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import { 
  ShieldAlert, 
  Search, 
  Plus, 
  Trash2, 
  AlertTriangle, 
  X
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function WatchlistPage() {
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState({
    plate_number: '',
    reason: 'Stolen Vehicle Alert',
    severity: 'CRITICAL',
    status: 'ACTIVE',
    remarks: 'Police Flagged Stolen Vehicle',
  });

  const fetchWatchlist = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/watchlist`);
      if (res.ok) {
        const json = await res.json();
        setWatchlist(json.items || []);
      }
    } catch (err) {
      console.error('Failed to fetch watchlist:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWatchlist();
  }, []);

  const handleCreateWatchlist = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE_URL}/watchlist`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (res.ok) {
        setShowAddModal(false);
        setFormData({ plate_number: '', reason: 'Stolen Vehicle Alert', severity: 'CRITICAL', status: 'ACTIVE', remarks: 'Police Flagged Stolen Vehicle' });
        fetchWatchlist();
      } else {
        const err = await res.json();
        alert(`Error: ${err.detail || 'Failed to add watchlist entry'}`);
      }
    } catch (err) {
      console.error('Failed to create watchlist entry:', err);
    }
  };

  const handleDeleteWatchlist = async (id) => {
    if (!window.confirm('Remove vehicle from Watchlist?')) return;
    try {
      const res = await fetch(`${API_BASE_URL}/watchlist/${id}`, { method: 'DELETE' });
      if (res.ok) fetchWatchlist();
    } catch (err) {
      console.error('Failed to delete watchlist entry:', err);
    }
  };

  const filtered = watchlist.filter(w =>
    !searchTerm || w.plate_number?.toLowerCase().includes(searchTerm.toLowerCase()) || w.reason?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-[#f2f2f2] text-[#1a3b45] font-sans">
      <Header title="Vehicle Security Watchlist" subtitle="Manage blacklisted, stolen, expired, or flagged vehicles requiring immediate gate denial & security alerts" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Action & Search Bar */}
        <div className="flex items-center justify-between bg-white rounded-xl p-4 border border-[#c8d8e4] backdrop-blur-md">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-[#5c7885] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search Watchlist Plate or Reason..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl text-xs text-[#1a3b45] font-mono placeholder-slate-500 focus:outline-none focus:border-rose-500"
            />
          </div>

          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-rose-500 hover:bg-rose-400 text-[#1a3b45] font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-rose-500/20"
          >
            <Plus className="w-4 h-4" /> Add Vehicle to Watchlist
          </button>
        </div>

        {/* Watchlist Master Table */}
        <div className="bg-white rounded-xl border border-[#c8d8e4] overflow-hidden backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-[#2b6777]">
              <thead className="bg-[#f2f2f2] text-[#5c7885] uppercase text-[10px] tracking-wider border-b border-[#c8d8e4] font-mono">
                <tr>
                  <th className="p-4">License Plate</th>
                  <th className="p-4">Reason</th>
                  <th className="p-4">Severity Level</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Remarks</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan="6" className="p-8 text-center text-[#5c7885] font-sans">Loading Watchlist entries...</td>
                  </tr>
                ) : filtered.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="p-8 text-center text-[#5c7885] font-sans">
                      <ShieldAlert className="w-8 h-8 mx-auto mb-2 opacity-50 text-rose-400" />
                      No Watchlist entries found.
                    </td>
                  </tr>
                ) : (
                  filtered.map((w) => (
                    <tr key={w.id} className="hover:bg-[#f0f6f8] transition-colors">
                      <td className="p-4 font-bold text-rose-400 text-sm">{w.plate_number}</td>
                      <td className="p-4 font-sans text-[#1a3b45] font-semibold">{w.reason}</td>
                      <td className="p-4">
                        <span className={`px-2.5 py-1 rounded text-[10px] font-bold border ${
                          w.severity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400 border-rose-500/40' :
                          w.severity === 'HIGH' ? 'bg-amber-500/20 text-amber-400 border-amber-500/40' :
                          'bg-blue-500/20 text-blue-400 border-blue-500/40'
                        }`}>
                          {w.severity}
                        </span>
                      </td>
                      <td className="p-4">
                        <span className="text-rose-400 font-bold">● {w.status}</span>
                      </td>
                      <td className="p-4 font-sans text-[#2b6777]">{w.remarks}</td>
                      <td className="p-4 text-right">
                        <button
                          onClick={() => handleDeleteWatchlist(w.id)}
                          className="p-1.5 bg-[#f2f2f2] hover:bg-[#e8eff4] text-[#5c7885] rounded-lg border border-[#c8d8e4]"
                          title="Remove from Watchlist"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Modal: Add Watchlist */}
        {showAddModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-white backdrop-blur-md">
            <div className="bg-white border border-[#c8d8e4] rounded-2xl p-6 w-full max-w-md space-y-4 shadow-2xl">
              <div className="flex items-center justify-between border-b border-[#c8d8e4] pb-3">
                <h3 className="text-base font-bold text-[#1a3b45] flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5 text-rose-400" /> Add Vehicle to Watchlist
                </h3>
                <button onClick={() => setShowAddModal(false)} className="text-[#5c7885] hover:text-[#1a3b45]">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleCreateWatchlist} className="space-y-3 text-xs">
                <div>
                  <label className="block text-[#5c7885] font-semibold mb-1">License Plate Number</label>
                  <input
                    type="text"
                    value={formData.plate_number}
                    onChange={(e) => setFormData({ ...formData, plate_number: e.target.value })}
                    placeholder="e.g. KA01AB9999"
                    className="w-full bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl p-2.5 text-[#1a3b45] font-mono uppercase focus:border-rose-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-[#5c7885] font-semibold mb-1">Reason for Watchlist</label>
                  <input
                    type="text"
                    value={formData.reason}
                    onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                    placeholder="e.g. Stolen Vehicle Alert / Expired Registration"
                    className="w-full bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl p-2.5 text-[#1a3b45] focus:border-rose-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-[#5c7885] font-semibold mb-1">Severity Level</label>
                  <select
                    value={formData.severity}
                    onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                    className="w-full bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl p-2.5 text-[#1a3b45] focus:border-rose-500"
                  >
                    <option value="CRITICAL">CRITICAL (Immediate Denial & Police Alert)</option>
                    <option value="HIGH">HIGH (Deny Entry & Alert Security)</option>
                    <option value="MEDIUM">MEDIUM (Manual Verification Required)</option>
                    <option value="LOW">LOW (Informational Alert)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[#5c7885] font-semibold mb-1">Remarks</label>
                  <input
                    type="text"
                    value={formData.remarks}
                    onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
                    placeholder="e.g. Flagged by State Traffic Department"
                    className="w-full bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl p-2.5 text-[#1a3b45] focus:border-rose-500"
                  />
                </div>

                <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#c8d8e4]">
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="px-4 py-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl text-[#5c7885] hover:text-[#1a3b45]"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-5 py-2 bg-rose-500 hover:bg-rose-400 text-[#1a3b45] font-bold rounded-xl shadow-lg shadow-rose-500/20"
                  >
                    Flag Vehicle
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
