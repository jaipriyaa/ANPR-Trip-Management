import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import { AlertTriangle, RefreshCw, Clock } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function OverstayPage() {
  const [overstayList, setOverstayList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [maxMins, setMaxMins] = useState(120);

  const fetchOverstay = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/overstay?max_allowed_mins=${maxMins}`);
      if (res.ok) {
        const json = await res.json();
        setOverstayList(json.items || []);
      }
    } catch (err) {
      console.error('Failed to fetch overstay vehicles:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverstay();
  }, [maxMins]);

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-[#f2f2f2] text-[#1a3b45] font-sans">
      <Header title="Factory Overstay Violation Monitor" subtitle="Real-time detection of vehicles remaining inside industrial premises beyond permitted stay duration limits" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        <div className="flex items-center justify-between bg-white rounded-xl p-4 border border-[#c8d8e4] backdrop-blur-md">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-rose-400" />
            <h2 className="text-sm font-bold text-[#1a3b45]">Factory Overstay Violations</h2>
          </div>

          <div className="flex items-center gap-3 text-xs font-sans">
            <span className="text-[#5c7885]">Max Permitted Duration:</span>
            <select
              value={maxMins}
              onChange={(e) => setMaxMins(Number(e.target.value))}
              className="bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl px-3 py-1.5 text-[#1a3b45] font-semibold focus:outline-none focus:border-rose-500"
            >
              <option value={60}>60 Minutes (1 Hour)</option>
              <option value={120}>120 Minutes (2 Hours)</option>
              <option value={180}>180 Minutes (3 Hours)</option>
              <option value={240}>240 Minutes (4 Hours)</option>
            </select>

            <button
              onClick={fetchOverstay}
              className="p-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl text-[#5c7885] hover:text-[#1a3b45]"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Master Overstay Table */}
        <div className="bg-white rounded-xl border border-[#c8d8e4] overflow-hidden backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-[#2b6777]">
              <thead className="bg-[#f2f2f2] text-[#5c7885] uppercase text-[10px] tracking-wider border-b border-[#c8d8e4] font-mono">
                <tr>
                  <th className="p-4">License Plate</th>
                  <th className="p-4">Gate Entry Time</th>
                  <th className="p-4">Total Stay Duration</th>
                  <th className="p-4">Overstay Minutes</th>
                  <th className="p-4">Overstay Hours</th>
                  <th className="p-4">Severity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan="6" className="p-8 text-center text-[#5c7885] font-sans">Scanning factory premises for overstay violations...</td>
                  </tr>
                ) : overstayList.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="p-8 text-center text-[#5c7885] font-sans">No overstay violations detected. All vehicles within permitted duration limits!</td>
                  </tr>
                ) : (
                  overstayList.map((item) => (
                    <tr key={item.movement_id} className="hover:bg-[#f0f6f8] transition-colors">
                      <td className="p-4 font-bold text-rose-400 text-sm">{item.recognized_plate}</td>
                      <td className="p-4 text-[#2b6777]">{new Date(item.entry_time).toLocaleString()}</td>
                      <td className="p-4 text-amber-400 font-bold">{item.total_stay_minutes} mins</td>
                      <td className="p-4 text-rose-400 font-bold">+{item.overstay_minutes} mins</td>
                      <td className="p-4 text-rose-300 font-bold">{item.overstay_hours} hrs</td>
                      <td className="p-4">
                        <span className={`px-2.5 py-1 rounded text-[10px] font-bold border ${
                          item.severity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400 border-rose-500/40 animate-pulse' :
                          item.severity === 'HIGH' ? 'bg-amber-500/20 text-amber-400 border-amber-500/40' :
                          'bg-blue-500/20 text-blue-400 border-blue-500/40'
                        }`}>
                          {item.severity}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}
