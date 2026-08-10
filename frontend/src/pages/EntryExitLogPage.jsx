import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import { 
  Eye, 
  Search, 
  RefreshCw, 
  Clock, 
  Truck, 
  CheckCircle2, 
  LogOut, 
  LogIn, 
  ChevronLeft, 
  ChevronRight,
  ShieldCheck,
  AlertTriangle,
  Activity,
  MapPin,
  Calendar,
  Layers
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function EntryExitLogPage() {
  const [movements, setMovements] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('ALL'); // 'ALL' | 'INSIDE' | 'OUTSIDE'
  const [page, setPage] = useState(1);
  const limit = 10;

  // Summary Metrics State
  const [summary, setSummary] = useState({
    vehicles_currently_inside: 0,
    vehicles_entered_today: 0,
    vehicles_exited_today: 0,
    avg_stay_duration_formatted: '0 Minutes'
  });

  const fetchSummary = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/movements/summary`);
      if (res.ok) {
        const data = await res.json();
        setSummary(data);
      }
    } catch (err) {
      console.error('Failed to fetch movements summary:', err);
    }
  };

  const fetchMovements = async () => {
    setLoading(true);
    try {
      const skip = (page - 1) * limit;
      let url = `${API_BASE_URL}/movements?skip=${skip}&limit=${limit}`;
      if (searchTerm) url += `&search=${encodeURIComponent(searchTerm)}`;
      if (filterStatus !== 'ALL') url += `&movement_status=${filterStatus}`;

      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setMovements(data.items || []);
        setTotal(data.total || 0);
      }
    } catch (err) {
      console.error('Failed to fetch movements log:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
    fetchMovements();
  }, [page, searchTerm, filterStatus]);

  const totalPages = Math.ceil(total / limit) || 1;

  // Format Helper for Image Paths
  const getImageUrl = (path) => {
    if (!path) return null;
    if (path.startsWith('http')) return path;
    const cleanPath = path.startsWith('/') ? path.slice(1) : path;
    return `${API_BASE_URL}/vehicle-recognition/media/${cleanPath}`;
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-slate-950 text-slate-100">
      <Header title="Entry / Exit Vehicle Movement Log" subtitle="Real-time gate event processing, live facility occupancy, and stay duration analytics" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Live Status Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Card 1: Currently Inside */}
          <div className="bg-slate-900/60 rounded-xl p-4 border border-emerald-500/30 backdrop-blur-md flex items-center justify-between relative overflow-hidden">
            <div className="space-y-1">
              <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Vehicles Currently Inside</p>
              <p className="text-3xl font-extrabold text-emerald-400 font-mono">
                {summary.vehicles_currently_inside}
              </p>
              <p className="text-[11px] text-emerald-400/80 font-mono flex items-center gap-1.5 pt-1">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Facility Occupancy Active
              </p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shadow-lg shadow-emerald-500/20">
              <CheckCircle2 className="w-6 h-6" />
            </div>
          </div>

          {/* Card 2: Entered Today */}
          <div className="bg-slate-900/60 rounded-xl p-4 border border-blue-500/30 backdrop-blur-md flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Vehicles Entered Today</p>
              <p className="text-3xl font-extrabold text-blue-400 font-mono">
                {summary.vehicles_entered_today}
              </p>
              <p className="text-[11px] text-blue-400/80 font-mono pt-1">Inbound Gate Registrations</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 shadow-lg shadow-blue-500/20">
              <LogIn className="w-6 h-6" />
            </div>
          </div>

          {/* Card 3: Exited Today */}
          <div className="bg-slate-900/60 rounded-xl p-4 border border-slate-700/60 backdrop-blur-md flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Vehicles Exited Today</p>
              <p className="text-3xl font-extrabold text-slate-300 font-mono">
                {summary.vehicles_exited_today}
              </p>
              <p className="text-[11px] text-slate-400 font-mono pt-1">Completed Outbound Gate Departures</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
              <LogOut className="w-6 h-6" />
            </div>
          </div>

          {/* Card 4: Average Stay Duration */}
          <div className="bg-slate-900/60 rounded-xl p-4 border border-purple-500/30 backdrop-blur-md flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Average Stay Duration</p>
              <p className="text-xl font-bold text-purple-300 font-mono mt-1">
                {summary.avg_stay_duration_formatted}
              </p>
              <p className="text-[11px] text-purple-400/80 font-mono pt-1">Turnaround Time Metric</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 shadow-lg shadow-purple-500/20">
              <Clock className="w-6 h-6" />
            </div>
          </div>
        </div>

        {/* Search & Filter Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900/60 rounded-xl p-4 border border-slate-800 backdrop-blur-md">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by Plate Number, Vehicle Type, Purpose..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <div className="flex items-center gap-2">
              <label className="text-xs font-semibold text-slate-400">Filter Status:</label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
              >
                <option value="ALL">All Movements</option>
                <option value="INSIDE">Currently Inside (Green)</option>
                <option value="OUTSIDE">Completed History (Gray)</option>
              </select>
            </div>

            <button
              onClick={() => {
                fetchSummary();
                fetchMovements();
              }}
              className="p-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-400 hover:text-white transition-all"
              title="Refresh Event Log"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Movements Table */}
        <div className="bg-slate-900/60 rounded-xl border border-slate-800 overflow-hidden backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
                <tr>
                  <th className="p-4">Crop</th>
                  <th className="p-4">Plate Number</th>
                  <th className="p-4">Vehicle Details</th>
                  <th className="p-4">Entry Gate & Time</th>
                  <th className="p-4">Exit Gate & Time</th>
                  <th className="p-4">Stay Duration</th>
                  <th className="p-4">Movement Status</th>
                  <th className="p-4 text-right">Confidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {loading ? (
                  <tr>
                    <td colSpan="8" className="p-8 text-center text-slate-500">Loading vehicle movements log...</td>
                  </tr>
                ) : movements.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="p-8 text-center text-slate-500">
                      <Truck className="w-8 h-8 mx-auto mb-2 opacity-50 text-cyan-400" />
                      No vehicle movement records found. Trigger AI Vehicle Recognition to record gate movements.
                    </td>
                  </tr>
                ) : (
                  movements.map((m) => {
                    const vehicleCropUrl = getImageUrl(m.cropped_vehicle_path);
                    const plateCropUrl = getImageUrl(m.cropped_plate_path);

                    return (
                      <tr key={m.id} className="hover:bg-slate-800/40 transition-colors">
                        {/* Vehicle / Plate Image */}
                        <td className="p-3">
                          <div className="w-14 h-10 rounded-lg overflow-hidden border border-slate-800 bg-slate-950 flex items-center justify-center">
                            {plateCropUrl ? (
                              <img src={plateCropUrl} alt={m.recognized_plate} className="w-full h-full object-cover" />
                            ) : vehicleCropUrl ? (
                              <img src={vehicleCropUrl} alt={m.recognized_plate} className="w-full h-full object-cover" />
                            ) : (
                              <Truck className="w-5 h-5 text-slate-600" />
                            )}
                          </div>
                        </td>

                        {/* Plate Number */}
                        <td className="p-4 font-mono font-bold text-sm text-cyan-400">
                          {m.recognized_plate}
                        </td>

                        {/* Vehicle Details */}
                        <td className="p-4 space-y-0.5">
                          <p className="font-semibold text-white">{m.vehicle_type || 'Vehicle'}</p>
                          {m.make_model && <p className="text-[11px] text-slate-400">{m.make_model} {m.color ? `(${m.color})` : ''}</p>}
                          {m.transporter_name && <p className="text-[10px] text-purple-400">Transporter: {m.transporter_name}</p>}
                        </td>

                        {/* Entry Gate & Time */}
                        <td className="p-4 space-y-0.5">
                          <p className="font-semibold text-blue-400 flex items-center gap-1">
                            <LogIn className="w-3.5 h-3.5" /> {m.entry_gate_code || 'Main Entry Gate'}
                          </p>
                          <p className="text-[11px] text-slate-400 font-mono">
                            {new Date(m.entry_time).toLocaleString()}
                          </p>
                        </td>

                        {/* Exit Gate & Time */}
                        <td className="p-4 space-y-0.5">
                          {m.exit_time ? (
                            <>
                              <p className="font-semibold text-slate-300 flex items-center gap-1">
                                <LogOut className="w-3.5 h-3.5 text-slate-500" /> {m.exit_gate_code || 'Main Exit Gate'}
                              </p>
                              <p className="text-[11px] text-slate-400 font-mono">
                                {new Date(m.exit_time).toLocaleString()}
                              </p>
                            </>
                          ) : (
                            <span className="text-[11px] text-emerald-400 font-mono italic">Still On Premises</span>
                          )}
                        </td>

                        {/* Stay Duration */}
                        <td className="p-4 font-mono font-semibold">
                          {m.movement_status === 'INSIDE' ? (
                            <span className="text-emerald-400 flex items-center gap-1">
                              <Clock className="w-3.5 h-3.5 animate-spin" /> In Progress...
                            </span>
                          ) : (
                            <span className="text-purple-300">{m.stay_duration_formatted || '0 Minutes'}</span>
                          )}
                        </td>

                        {/* Status Badges */}
                        <td className="p-4">
                          <span className={`px-2.5 py-1 rounded text-[11px] font-bold font-mono border ${
                            m.movement_status === 'INSIDE'
                              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                              : m.vehicle_status === 'ENTERED'
                              ? 'bg-blue-500/10 text-blue-400 border-blue-500/30'
                              : 'bg-slate-800 text-slate-400 border-slate-700'
                          }`}>
                            ● {m.movement_status === 'INSIDE' ? 'INSIDE' : m.vehicle_status}
                          </span>
                        </td>

                        {/* Recognition Confidence */}
                        <td className="p-4 text-right font-mono font-semibold text-cyan-400">
                          {((m.recognition_confidence || 0) * 100).toFixed(1)}%
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="p-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span>Showing page {page} of {totalPages} ({total} total movements)</span>
            <div className="flex items-center gap-2">
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
