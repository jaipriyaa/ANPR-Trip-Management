import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import { Clock, RefreshCw, AlertTriangle } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function LateArrivalsPage() {
  const [lateList, setLateList] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchLateArrivals = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/late-arrivals`);
      if (res.ok) {
        const json = await res.json();
        setLateList(json.items || []);
      }
    } catch (err) {
      console.error('Failed to fetch late arrivals:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLateArrivals();
  }, []);

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-slate-950 text-slate-100 font-sans">
      <Header title="Late Arrival Detection Engine" subtitle="Automated schedule variance tracking comparing expected entry time vs actual gate arrival timestamp" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        <div className="flex items-center justify-between bg-slate-900/80 rounded-xl p-4 border border-slate-800 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <Clock className="w-5 h-5 text-amber-400" />
            <h2 className="text-sm font-bold text-white">Active Late Arrival Scans</h2>
          </div>

          <button
            onClick={fetchLateArrivals}
            className="p-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-400 hover:text-white"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Master Late Arrivals Table */}
        <div className="bg-slate-900/80 rounded-xl border border-slate-800 overflow-hidden backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-mono">
                <tr>
                  <th className="p-4">Trip Number</th>
                  <th className="p-4">License Plate</th>
                  <th className="p-4">Transporter</th>
                  <th className="p-4">Driver</th>
                  <th className="p-4">Expected Entry</th>
                  <th className="p-4">Actual Entry</th>
                  <th className="p-4">Delay (mins)</th>
                  <th className="p-4">Severity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan="8" className="p-8 text-center text-slate-500 font-sans">Scanning late arrivals...</td>
                  </tr>
                ) : lateList.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="p-8 text-center text-slate-500 font-sans">No late arrival violations detected. All trips on schedule!</td>
                  </tr>
                ) : (
                  lateList.map((item) => (
                    <tr key={item.trip_id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="p-4 font-bold text-purple-400">{item.trip_number}</td>
                      <td className="p-4 font-bold text-cyan-400">{item.recognized_plate}</td>
                      <td className="p-4 text-slate-200 font-sans">{item.transporter_name}</td>
                      <td className="p-4 text-slate-300 font-sans">{item.driver_name}</td>
                      <td className="p-4 text-slate-400">{new Date(item.expected_entry).toLocaleString()}</td>
                      <td className="p-4 text-slate-300">{new Date(item.actual_entry).toLocaleString()}</td>
                      <td className="p-4 text-amber-400 font-bold">+{item.delay_minutes} mins</td>
                      <td className="p-4">
                        <span className={`px-2.5 py-1 rounded text-[10px] font-bold border ${
                          item.severity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400 border-rose-500/40' :
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
