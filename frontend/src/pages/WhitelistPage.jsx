import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import { 
  CheckCircle2, 
  Search, 
  Plus, 
  Trash2, 
  ShieldCheck, 
  X,
  Building,
  Truck,
  UserCheck
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function WhitelistPage() {
  const [whitelist, setWhitelist] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState({
    recognized_plate: '',
    allowed_entry_gates: 'ALL',
    allowed_exit_gates: 'ALL',
    status: 'ACTIVE',
    remarks: 'Authorized Vehicle',
  });

  const fetchWhitelist = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/whitelist`);
      if (res.ok) {
        const json = await res.json();
        setWhitelist(json.items || []);
      }
    } catch (err) {
      console.error('Failed to fetch whitelist:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWhitelist();
  }, []);

  const handleCreateWhitelist = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE_URL}/whitelist`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (res.ok) {
        setShowAddModal(false);
        setFormData({ recognized_plate: '', allowed_entry_gates: 'ALL', allowed_exit_gates: 'ALL', status: 'ACTIVE', remarks: 'Authorized Vehicle' });
        fetchWhitelist();
      } else {
        const err = await res.json();
        alert(`Error: ${err.detail || 'Failed to add whitelist entry'}`);
      }
    } catch (err) {
      console.error('Failed to create whitelist entry:', err);
    }
  };

  const handleDeleteWhitelist = async (id) => {
    if (!window.confirm('Remove vehicle from Whitelist?')) return;
    try {
      const res = await fetch(`${API_BASE_URL}/whitelist/${id}`, { method: 'DELETE' });
      if (res.ok) fetchWhitelist();
    } catch (err) {
      console.error('Failed to delete whitelist entry:', err);
    }
  };

  const filtered = whitelist.filter(w =>
    !searchTerm || w.recognized_plate?.toLowerCase().includes(searchTerm.toLowerCase()) || w.remarks?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-slate-950 text-slate-100 font-sans">
      <Header title="Vehicle Whitelist Management" subtitle="Manage permanently or temporarily authorized factory vehicles with allowed entry/exit gates and time windows" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Action & Search Bar */}
        <div className="flex items-center justify-between bg-slate-900/80 rounded-xl p-4 border border-slate-800 backdrop-blur-md">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search Whitelist Plate or Remarks..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white font-mono placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-emerald-500/20"
          >
            <Plus className="w-4 h-4" /> Add Vehicle to Whitelist
          </button>
        </div>

        {/* Whitelist Master Table */}
        <div className="bg-slate-900/80 rounded-xl border border-slate-800 overflow-hidden backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-mono">
                <tr>
                  <th className="p-4">License Plate</th>
                  <th className="p-4">Allowed Entry Gates</th>
                  <th className="p-4">Allowed Exit Gates</th>
                  <th className="p-4">Authorization Status</th>
                  <th className="p-4">Remarks</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan="6" className="p-8 text-center text-slate-500 font-sans">Loading Whitelist entries...</td>
                  </tr>
                ) : filtered.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="p-8 text-center text-slate-500 font-sans">
                      <ShieldCheck className="w-8 h-8 mx-auto mb-2 opacity-50 text-emerald-400" />
                      No Whitelist entries found.
                    </td>
                  </tr>
                ) : (
                  filtered.map((w) => (
                    <tr key={w.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="p-4 font-bold text-cyan-400 text-sm">{w.recognized_plate}</td>
                      <td className="p-4 text-purple-300">{w.allowed_entry_gates || 'ALL'}</td>
                      <td className="p-4 text-slate-400">{w.allowed_exit_gates || 'ALL'}</td>
                      <td className="p-4">
                        <span className={`px-2.5 py-1 rounded text-[10px] font-bold border ${
                          w.status === 'ACTIVE'
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                            : 'bg-slate-800 text-slate-400 border-slate-700'
                        }`}>
                          ● {w.status}
                        </span>
                      </td>
                      <td className="p-4 font-sans text-slate-300">{w.remarks}</td>
                      <td className="p-4 text-right">
                        <button
                          onClick={() => handleDeleteWhitelist(w.id)}
                          className="p-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 rounded-lg"
                          title="Remove from Whitelist"
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

        {/* Modal: Add Whitelist */}
        {showAddModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-md space-y-4 shadow-2xl">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-emerald-400" /> Add Vehicle to Whitelist
                </h3>
                <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-white">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleCreateWhitelist} className="space-y-3 text-xs">
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">License Plate Number</label>
                  <input
                    type="text"
                    value={formData.recognized_plate}
                    onChange={(e) => setFormData({ ...formData, recognized_plate: e.target.value })}
                    placeholder="e.g. MH14TCF200F"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white font-mono uppercase focus:border-emerald-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Allowed Entry Gates</label>
                  <input
                    type="text"
                    value={formData.allowed_entry_gates}
                    onChange={(e) => setFormData({ ...formData, allowed_entry_gates: e.target.value })}
                    placeholder="e.g. GATE-NORTH-01, ALL"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white font-mono focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Remarks / Purpose</label>
                  <input
                    type="text"
                    value={formData.remarks}
                    onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
                    placeholder="e.g. Permanent Delivery Fleet"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:border-emerald-500"
                  />
                </div>

                <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="px-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-400 hover:text-white"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-5 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl shadow-lg shadow-emerald-500/20"
                  >
                    Authorize & Save
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
