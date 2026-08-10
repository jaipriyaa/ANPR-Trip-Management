import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import { 
  Calendar, 
  Search, 
  Plus, 
  RefreshCw, 
  Clock, 
  Truck, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  User, 
  Building, 
  MapPin, 
  Package, 
  ShieldCheck, 
  Eye, 
  ChevronLeft, 
  ChevronRight,
  X,
  Check,
  Edit2,
  Trash2,
  History,
  Tag
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function TripsPage() {
  const [trips, setTrips] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [filterApproval, setFilterApproval] = useState('ALL');
  const [page, setPage] = useState(1);
  const limit = 10;

  // Masters for Create/Edit Modal dropdowns
  const [vehicles, setVehicles] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [transporters, setTransporters] = useState([]);
  const [gates, setGates] = useState([]);

  // Modals State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedTrip, setSelectedTrip] = useState(null);

  // Form State
  const [formData, setFormData] = useState({
    recognized_plate: '',
    vehicle_id: '',
    driver_id: '',
    transporter_id: '',
    entry_gate_id: '',
    exit_gate_id: '',
    expected_entry_time: new Date().toISOString().slice(0, 16),
    expected_exit_time: new Date(Date.now() + 4 * 3600 * 1000).toISOString().slice(0, 16),
    purpose: 'Material Delivery',
    material_name: 'Raw Steel Coils',
    material_quantity: '25 Tons',
    source_location: 'Supplier Yard',
    destination_location: 'Main Assembly Plant',
    priority: 'MEDIUM',
    remarks: '',
  });

  // Summary Metrics State
  const [summary, setSummary] = useState({
    active_trips: 0,
    completed_trips: 0,
    waiting_vehicles: 0,
    rejected_trips: 0,
    vehicles_inside: 0,
    todays_trips: 0,
    avg_trip_duration_formatted: '0m'
  });

  const fetchSummary = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/trips/dashboard`);
      if (res.ok) {
        const json = await res.json();
        setSummary(json);
      }
    } catch (err) {
      console.error('Failed to fetch trip dashboard summary:', err);
    }
  };

  const fetchMasters = async () => {
    try {
      const [vRes, dRes, tRes, gRes] = await Promise.all([
        fetch(`${API_BASE_URL}/vehicles?limit=100`),
        fetch(`${API_BASE_URL}/drivers?limit=100`),
        fetch(`${API_BASE_URL}/transporters?limit=100`),
        fetch(`${API_BASE_URL}/gates?limit=100`),
      ]);
      if (vRes.ok) setVehicles((await vRes.json()).items || []);
      if (dRes.ok) setDrivers((await dRes.json()).items || []);
      if (tRes.ok) setTransporters((await tRes.json()).items || []);
      if (gRes.ok) setGates((await gRes.json()).items || []);
    } catch (err) {
      console.error('Failed to fetch master data dropdowns:', err);
    }
  };

  const fetchTrips = async () => {
    setLoading(true);
    try {
      const skip = (page - 1) * limit;
      let url = `${API_BASE_URL}/trips?skip=${skip}&limit=${limit}`;
      if (searchTerm) url += `&search=${encodeURIComponent(searchTerm)}`;
      if (filterStatus !== 'ALL') url += `&trip_status=${filterStatus}`;
      if (filterApproval !== 'ALL') url += `&approval_status=${filterApproval}`;

      const res = await fetch(url);
      if (res.ok) {
        const json = await res.json();
        setTrips(json.items || []);
        setTotal(json.total || 0);
      }
    } catch (err) {
      console.error('Failed to fetch trips:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
    fetchMasters();
  }, []);

  useEffect(() => {
    fetchTrips();
  }, [page, searchTerm, filterStatus, filterApproval]);

  const handleCreateTrip = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...formData,
        vehicle_id: formData.vehicle_id || null,
        driver_id: formData.driver_id || null,
        transporter_id: formData.transporter_id || null,
        entry_gate_id: formData.entry_gate_id || null,
        exit_gate_id: formData.exit_gate_id || null,
        expected_entry_time: new Date(formData.expected_entry_time).toISOString(),
        expected_exit_time: new Date(formData.expected_exit_time).toISOString(),
      };

      const res = await fetch(`${API_BASE_URL}/trips`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        setShowCreateModal(false);
        fetchSummary();
        fetchTrips();
      } else {
        const err = await res.json();
        alert(`Error creating trip: ${err.detail || 'Validation failed'}`);
      }
    } catch (err) {
      console.error('Failed to create trip:', err);
    }
  };

  const handleApproveTrip = async (id) => {
    try {
      const res = await fetch(`${API_BASE_URL}/trips/${id}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approval_status: 'APPROVED', remarks: 'Manual Operator Approval' }),
      });
      if (res.ok) {
        fetchSummary();
        fetchTrips();
        if (selectedTrip && selectedTrip.id === id) {
          const updated = await res.json();
          setSelectedTrip(updated);
        }
      }
    } catch (err) {
      console.error('Failed to approve trip:', err);
    }
  };

  const handleRejectTrip = async (id) => {
    try {
      const res = await fetch(`${API_BASE_URL}/trips/${id}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approval_status: 'REJECTED', remarks: 'Rejected by Security Operator' }),
      });
      if (res.ok) {
        fetchSummary();
        fetchTrips();
        if (selectedTrip && selectedTrip.id === id) {
          const updated = await res.json();
          setSelectedTrip(updated);
        }
      }
    } catch (err) {
      console.error('Failed to reject trip:', err);
    }
  };

  const handleCancelTrip = async (id) => {
    if (!window.confirm('Are you sure you want to cancel this scheduled trip?')) return;
    try {
      const res = await fetch(`${API_BASE_URL}/trips/${id}`, { method: 'DELETE' });
      if (res.ok) {
        fetchSummary();
        fetchTrips();
        setShowDetailModal(false);
      }
    } catch (err) {
      console.error('Failed to cancel trip:', err);
    }
  };

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-[#f2f2f2] text-[#1a3b45] font-sans">
      <Header title="Trip Engine & Dispatch Management" subtitle="Industrial vehicle trip lifecycle, gate entry/exit verification, material dispatching, and status audit logs" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Top 7 Summary Metrics Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
          <div className="bg-white rounded-xl p-3 border border-cyan-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Active Trips</p>
            <p className="text-2xl font-extrabold text-cyan-400 font-mono mt-1">{summary.active_trips}</p>
            <p className="text-[10px] text-cyan-400/80 font-mono mt-0.5">In Progress</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-emerald-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Completed Trips</p>
            <p className="text-2xl font-extrabold text-emerald-400 font-mono mt-1">{summary.completed_trips}</p>
            <p className="text-[10px] text-emerald-400/80 font-mono mt-0.5">Finished</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-blue-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Waiting Vehicles</p>
            <p className="text-2xl font-extrabold text-blue-400 font-mono mt-1">{summary.waiting_vehicles}</p>
            <p className="text-[10px] text-blue-400/80 font-mono mt-0.5">At Gate</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-red-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Rejected Trips</p>
            <p className="text-2xl font-extrabold text-red-400 font-mono mt-1">{summary.rejected_trips}</p>
            <p className="text-[10px] text-red-400/80 font-mono mt-0.5">Denied Entry</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-emerald-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Vehicles Inside</p>
            <p className="text-2xl font-extrabold text-emerald-400 font-mono mt-1">{summary.vehicles_inside}</p>
            <p className="text-[10px] text-emerald-400/80 font-mono mt-0.5">Premises Active</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-purple-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Today's Trips</p>
            <p className="text-2xl font-extrabold text-purple-300 font-mono mt-1">{summary.todays_trips}</p>
            <p className="text-[10px] text-purple-400/80 font-mono mt-0.5">Dispatched</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-amber-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Avg Duration</p>
            <p className="text-lg font-bold text-amber-300 font-mono mt-1.5">{summary.avg_trip_duration_formatted}</p>
            <p className="text-[10px] text-amber-400/80 font-mono mt-0.5">Turnaround</p>
          </div>
        </div>

        {/* Action & Filter Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white rounded-xl p-4 border border-[#c8d8e4] backdrop-blur-md">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-[#5c7885] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search Trip #, Plate, Purpose, Material..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl text-xs text-[#1a3b45] placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto flex-wrap">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl px-3 py-2 text-xs text-[#1a3b45] focus:outline-none focus:border-cyan-500"
            >
              <option value="ALL">All Trip Statuses</option>
              <option value="SCHEDULED">SCHEDULED</option>
              <option value="WAITING">WAITING</option>
              <option value="INSIDE">INSIDE</option>
              <option value="COMPLETED">COMPLETED</option>
              <option value="CANCELLED">CANCELLED</option>
            </select>

            <select
              value={filterApproval}
              onChange={(e) => setFilterApproval(e.target.value)}
              className="bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl px-3 py-2 text-xs text-[#1a3b45] focus:outline-none focus:border-cyan-500"
            >
              <option value="ALL">All Approvals</option>
              <option value="APPROVED">APPROVED</option>
              <option value="PENDING">PENDING</option>
              <option value="REJECTED">REJECTED</option>
            </select>

            <button
              onClick={() => {
                fetchSummary();
                fetchTrips();
              }}
              className="p-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl text-[#5c7885] hover:text-[#1a3b45] transition-all"
              title="Refresh Trips List"
            >
              <RefreshCw className="w-4 h-4" />
            </button>

            <button
              onClick={() => {
                fetchMasters();
                setShowCreateModal(true);
              }}
              className="px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-cyan-500/20 transition-all"
            >
              <Plus className="w-4 h-4" /> Create & Schedule Trip
            </button>
          </div>
        </div>

        {/* Trips Master Table */}
        <div className="bg-white rounded-xl border border-[#c8d8e4] overflow-hidden backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-[#2b6777]">
              <thead className="bg-[#f2f2f2] text-[#5c7885] uppercase text-[10px] tracking-wider border-b border-[#c8d8e4]">
                <tr>
                  <th className="p-4">Trip #</th>
                  <th className="p-4">Vehicle & Plate</th>
                  <th className="p-4">Driver & Transporter</th>
                  <th className="p-4">Purpose & Material</th>
                  <th className="p-4">Source & Destination</th>
                  <th className="p-4">Expected Window</th>
                  <th className="p-4">Trip Status</th>
                  <th className="p-4">Approval</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan="9" className="p-8 text-center text-[#5c7885] font-sans">Loading trips database...</td>
                  </tr>
                ) : trips.length === 0 ? (
                  <tr>
                    <td colSpan="9" className="p-8 text-center text-[#5c7885] font-sans">
                      <Calendar className="w-8 h-8 mx-auto mb-2 opacity-50 text-cyan-400" />
                      No vehicle trips found matching filters. Create a new trip to begin tracking.
                    </td>
                  </tr>
                ) : (
                  trips.map((t) => (
                    <tr key={t.id} className="hover:bg-[#f0f6f8] transition-colors">
                      {/* Trip Number */}
                      <td className="p-4 font-bold text-cyan-400">{t.trip_number}</td>

                      {/* Vehicle & Plate */}
                      <td className="p-4 font-sans space-y-0.5">
                        <p className="font-bold text-[#1a3b45] font-mono">{t.vehicle_number || 'MH14TCF200F'}</p>
                        <p className="text-[11px] text-[#5c7885]">{t.vehicle_type || 'SUV'}</p>
                      </td>

                      {/* Driver & Transporter */}
                      <td className="p-4 font-sans space-y-0.5">
                        <p className="font-semibold text-[#1a3b45]">{t.driver_name || 'Assigned Driver'}</p>
                        <p className="text-[11px] text-purple-400">{t.transporter_name || 'VRL Logistics'}</p>
                      </td>

                      {/* Purpose & Material */}
                      <td className="p-4 font-sans space-y-0.5">
                        <p className="font-semibold text-[#1a3b45]">{t.purpose}</p>
                        {t.material_name && (
                          <p className="text-[11px] text-cyan-300 font-mono">{t.material_name} ({t.material_quantity || 'N/A'})</p>
                        )}
                      </td>

                      {/* Source & Destination */}
                      <td className="p-4 font-sans space-y-0.5">
                        <p className="text-[#5c7885] text-[11px]">From: <span className="text-[#1a3b45]">{t.source_location || 'Factory Depot'}</span></p>
                        <p className="text-[#5c7885] text-[11px]">To: <span className="text-[#1a3b45]">{t.destination_location || 'Assembly Yard'}</span></p>
                      </td>

                      {/* Expected Window */}
                      <td className="p-4 text-[11px] text-[#5c7885] space-y-0.5">
                        <p>In: <span className="text-[#1a3b45]">{new Date(t.expected_entry_time).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}</span></p>
                        <p>Out: <span className="text-[#1a3b45]">{new Date(t.expected_exit_time).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}</span></p>
                      </td>

                      {/* Trip Status */}
                      <td className="p-4">
                        <span className={`px-2.5 py-1 rounded text-[10px] font-bold font-mono border ${
                          t.trip_status === 'INSIDE'
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                            : t.trip_status === 'SCHEDULED'
                            ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30'
                            : t.trip_status === 'COMPLETED'
                            ? 'bg-[#e8eff4] text-[#5c7885] border-[#c8d8e4]'
                            : 'bg-red-500/10 text-red-400 border-red-500/30'
                        }`}>
                          ● {t.trip_status}
                        </span>
                      </td>

                      {/* Approval Status */}
                      <td className="p-4">
                        <span className={`px-2.5 py-1 rounded text-[10px] font-bold font-mono border ${
                          t.approval_status === 'APPROVED'
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                            : t.approval_status === 'PENDING'
                            ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                            : 'bg-red-500/10 text-red-400 border-red-500/30'
                        }`}>
                          {t.approval_status}
                        </span>
                      </td>

                      {/* Actions */}
                      <td className="p-4 text-right space-x-1 font-sans">
                        <button
                          onClick={() => {
                            setSelectedTrip(t);
                            setShowDetailModal(true);
                          }}
                          className="p-1.5 bg-[#f2f2f2] hover:bg-[#e8eff4] border border-[#c8d8e4] rounded-lg text-[#2b6777] transition-all"
                          title="View Details & Status History"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </button>

                        {t.approval_status === 'PENDING' && (
                          <>
                            <button
                              onClick={() => handleApproveTrip(t.id)}
                              className="p-1.5 bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 rounded-lg text-emerald-400 transition-all"
                              title="Approve Trip"
                            >
                              <Check className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => handleRejectTrip(t.id)}
                              className="p-1.5 bg-red-500/20 hover:bg-red-500/30 border border-red-500/40 rounded-lg text-red-400 transition-all"
                              title="Reject Trip"
                            >
                              <X className="w-3.5 h-3.5" />
                            </button>
                          </>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="p-4 border-t border-[#c8d8e4] flex items-center justify-between text-xs text-[#5c7885] font-sans">
            <span>Showing page {page} of {totalPages} ({total} total trips)</span>
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

        {/* Modal 1: Create & Schedule Trip */}
        {showCreateModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-white backdrop-blur-md">
            <div className="bg-white border border-[#c8d8e4] rounded-2xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto space-y-5 shadow-2xl">
              <div className="flex items-center justify-between border-b border-[#c8d8e4] pb-4">
                <h3 className="text-base font-bold text-[#1a3b45] flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-cyan-400" /> Schedule New Industrial Vehicle Trip
                </h3>
                <button onClick={() => setShowCreateModal(false)} className="text-[#5c7885] hover:text-[#1a3b45]">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleCreateTrip} className="space-y-4 text-xs">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-[#5c7885] font-semibold mb-1">Vehicle License Plate</label>
                    <select
                      value={formData.vehicle_id}
                      onChange={(e) => {
                        const vId = e.target.value;
                        const veh = vehicles.find((v) => String(v.id) === String(vId));
                        setFormData({
                          ...formData,
                          vehicle_id: vId,
                          recognized_plate: veh ? veh.vehicle_number : formData.recognized_plate,
                          transporter_id: veh && veh.transporter_id ? veh.transporter_id : formData.transporter_id,
                        });
                      }}
                      className="w-full bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl p-2.5 text-[#1a3b45] focus:border-cyan-500"
                    >
                      <option value="">-- Select Master Vehicle --</option>
                      {vehicles.map((v) => (
                        <option key={v.id} value={v.id}>{v.vehicle_number} ({v.vehicle_type})</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-[#5c7885] font-semibold mb-1">Plate Number Override</label>
                    <input
                      type="text"
                      value={formData.recognized_plate}
                      onChange={(e) => setFormData({ ...formData, recognized_plate: e.target.value.toUpperCase() })}
                      placeholder="e.g. KA05AB1234"
                      className="w-full bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl p-2.5 text-[#1a3b45] focus:border-cyan-500 font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-[#5c7885] font-semibold mb-1">Assigned Driver</label>
                    <select
                      value={formData.driver_id}
                      onChange={(e) => setFormData({ ...formData, driver_id: e.target.value })}
                      className="w-full bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl p-2.5 text-[#1a3b45] focus:border-cyan-500"
                    >
                      <option value="">-- Select Driver --</option>
                      {drivers.map((d) => (
                        <option key={d.id} value={d.id}>{d.full_name} ({d.phone_number})</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-[#5c7885] font-semibold mb-1">Transporter</label>
                    <select
                      value={formData.transporter_id}
                      onChange={(e) => setFormData({ ...formData, transporter_id: e.target.value })}
                      className="w-full bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl p-2.5 text-[#1a3b45] focus:border-cyan-500"
                    >
                      <option value="">-- Select Transporter --</option>
                      {transporters.map((t) => (
                        <option key={t.id} value={t.id}>{t.name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-[#5c7885] font-semibold mb-1">Priority</label>
                    <select
                      value={formData.priority}
                      onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                      className="w-full bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl p-2.5 text-[#1a3b45] focus:border-cyan-500"
                    >
                      <option value="LOW">LOW</option>
                      <option value="MEDIUM">MEDIUM</option>
                      <option value="HIGH">HIGH</option>
                      <option value="URGENT">URGENT</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-[#5c7885] font-semibold mb-1">Expected Entry Time</label>
                    <input
                      type="datetime-local"
                      value={formData.expected_entry_time}
                      onChange={(e) => setFormData({ ...formData, expected_entry_time: e.target.value })}
                      className="w-full bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl p-2.5 text-[#1a3b45] focus:border-cyan-500 font-mono"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-[#5c7885] font-semibold mb-1">Expected Exit Time</label>
                    <input
                      type="datetime-local"
                      value={formData.expected_exit_time}
                      onChange={(e) => setFormData({ ...formData, expected_exit_time: e.target.value })}
                      className="w-full bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl p-2.5 text-[#1a3b45] focus:border-cyan-500 font-mono"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-[#5c7885] font-semibold mb-1">Purpose of Visit</label>
                    <input
                      type="text"
                      value={formData.purpose}
                      onChange={(e) => setFormData({ ...formData, purpose: e.target.value })}
                      placeholder="e.g. Raw Material Supply"
                      className="w-full bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl p-2.5 text-[#1a3b45] focus:border-cyan-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-[#5c7885] font-semibold mb-1">Material Name & Qty</label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={formData.material_name}
                        onChange={(e) => setFormData({ ...formData, material_name: e.target.value })}
                        placeholder="Material Name"
                        className="w-1/2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl p-2.5 text-[#1a3b45] focus:border-cyan-500"
                      />
                      <input
                        type="text"
                        value={formData.material_quantity}
                        onChange={(e) => setFormData({ ...formData, material_quantity: e.target.value })}
                        placeholder="Qty (e.g. 25 Tons)"
                        className="w-1/2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl p-2.5 text-[#1a3b45] focus:border-cyan-500"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-[#5c7885] font-semibold mb-1">Source Location</label>
                    <input
                      type="text"
                      value={formData.source_location}
                      onChange={(e) => setFormData({ ...formData, source_location: e.target.value })}
                      placeholder="Origin Location"
                      className="w-full bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl p-2.5 text-[#1a3b45] focus:border-cyan-500"
                    />
                  </div>

                  <div>
                    <label className="block text-[#5c7885] font-semibold mb-1">Destination Location</label>
                    <input
                      type="text"
                      value={formData.destination_location}
                      onChange={(e) => setFormData({ ...formData, destination_location: e.target.value })}
                      placeholder="Internal Plant Destination"
                      className="w-full bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl p-2.5 text-[#1a3b45] focus:border-cyan-500"
                    />
                  </div>
                </div>

                <div className="flex items-center justify-end gap-3 pt-4 border-t border-[#c8d8e4]">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl text-[#5c7885] hover:text-[#1a3b45]"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-5 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-xl shadow-lg shadow-cyan-500/20"
                  >
                    Dispatch & Schedule Trip
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Modal 2: Trip Details & Status History Audit Log */}
        {showDetailModal && selectedTrip && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-white backdrop-blur-md">
            <div className="bg-white border border-[#c8d8e4] rounded-2xl p-6 w-full max-w-3xl max-h-[90vh] overflow-y-auto space-y-6 shadow-2xl">
              <div className="flex items-center justify-between border-b border-[#c8d8e4] pb-4">
                <div>
                  <h3 className="text-base font-bold text-[#1a3b45] flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-cyan-400" /> Trip Details — <span className="font-mono text-cyan-400">{selectedTrip.trip_number}</span>
                  </h3>
                  <p className="text-xs text-[#5c7885] pt-0.5">Created on {new Date(selectedTrip.created_at).toLocaleString()}</p>
                </div>
                <button onClick={() => setShowDetailModal(false)} className="text-[#5c7885] hover:text-[#1a3b45]">
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Status Header Bar */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-[#f2f2f2] p-4 rounded-xl border border-[#c8d8e4] text-xs">
                <div>
                  <span className="text-[#5c7885] text-[10px] block">Trip Status</span>
                  <span className="font-bold text-emerald-400 font-mono text-sm">{selectedTrip.trip_status}</span>
                </div>
                <div>
                  <span className="text-[#5c7885] text-[10px] block">Approval Status</span>
                  <span className="font-bold text-cyan-400 font-mono text-sm">{selectedTrip.approval_status}</span>
                </div>
                <div>
                  <span className="text-[#5c7885] text-[10px] block">Priority</span>
                  <span className="font-bold text-amber-400 font-mono">{selectedTrip.priority}</span>
                </div>
                <div>
                  <span className="text-[#5c7885] text-[10px] block">Purpose</span>
                  <span className="font-semibold text-[#1a3b45]">{selectedTrip.purpose}</span>
                </div>
              </div>

              {/* Details Breakdown */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div className="bg-white p-4 rounded-xl border border-[#c8d8e4] space-y-2">
                  <h4 className="font-bold text-[#1a3b45] border-b border-[#c8d8e4] pb-1">Vehicle & Driver</h4>
                  <p><span className="text-[#5c7885]">Plate:</span> <span className="font-mono font-bold text-cyan-400">{selectedTrip.vehicle_number || 'MH14TCF200F'}</span></p>
                  <p><span className="text-[#5c7885]">Driver:</span> <span className="text-[#1a3b45] font-semibold">{selectedTrip.driver_name || 'Suresh Kumar'}</span></p>
                  <p><span className="text-[#5c7885]">Transporter:</span> <span className="text-purple-400">{selectedTrip.transporter_name || 'VRL Logistics'}</span></p>
                </div>

                <div className="bg-white p-4 rounded-xl border border-[#c8d8e4] space-y-2">
                  <h4 className="font-bold text-[#1a3b45] border-b border-[#c8d8e4] pb-1">Material & Logistics</h4>
                  <p><span className="text-[#5c7885]">Material:</span> <span className="text-cyan-300 font-mono">{selectedTrip.material_name || 'Steel Coils'} ({selectedTrip.material_quantity || '25 Tons'})</span></p>
                  <p><span className="text-[#5c7885]">From:</span> <span className="text-[#1a3b45]">{selectedTrip.source_location || 'Supplier Yard'}</span></p>
                  <p><span className="text-[#5c7885]">To:</span> <span className="text-[#1a3b45]">{selectedTrip.destination_location || 'Plant Bay 4'}</span></p>
                </div>

                <div className="bg-white p-4 rounded-xl border border-[#c8d8e4] space-y-2 col-span-1 sm:col-span-2">
                  <h4 className="font-bold text-[#1a3b45] border-b border-[#c8d8e4] pb-1">Gate Execution Timestamps</h4>
                  <div className="grid grid-cols-2 gap-4 font-mono">
                    <div>
                      <p className="text-[#5c7885] text-[10px]">Expected Entry Window</p>
                      <p className="text-[#1a3b45]">{new Date(selectedTrip.expected_entry_time).toLocaleString()}</p>
                      <p className="text-[#5c7885] text-[10px] pt-1">Actual Entry Timestamp</p>
                      <p className="text-emerald-400 font-bold">{selectedTrip.actual_entry_time ? new Date(selectedTrip.actual_entry_time).toLocaleString() : 'Pending Entry'}</p>
                    </div>
                    <div>
                      <p className="text-[#5c7885] text-[10px]">Expected Exit Window</p>
                      <p className="text-[#1a3b45]">{new Date(selectedTrip.expected_exit_time).toLocaleString()}</p>
                      <p className="text-[#5c7885] text-[10px] pt-1">Actual Exit Timestamp</p>
                      <p className="text-[#2b6777] font-bold">{selectedTrip.actual_exit_time ? new Date(selectedTrip.actual_exit_time).toLocaleString() : 'In Progress'}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Status History Chronological Log */}
              <div className="space-y-2">
                <h4 className="font-bold text-xs text-[#1a3b45] flex items-center gap-1.5 uppercase tracking-wider">
                  <History className="w-4 h-4 text-cyan-400" /> Trip Status History Audit Log
                </h4>

                <div className="bg-[#f2f2f2] rounded-xl border border-[#c8d8e4] p-3 space-y-2 font-mono text-xs max-h-48 overflow-y-auto">
                  {selectedTrip.status_history?.length === 0 ? (
                    <p className="text-[#5c7885] text-center py-2 font-sans">No status changes recorded.</p>
                  ) : (
                    selectedTrip.status_history?.map((h) => (
                      <div key={h.id} className="flex items-center justify-between border-b border-[#c8d8e4] pb-2 text-[11px]">
                        <div>
                          <span className="text-cyan-400 font-bold">{h.current_status}</span>
                          {h.previous_status && <span className="text-[#5c7885]"> (from {h.previous_status})</span>}
                          {h.remarks && <p className="text-[#5c7885] font-sans text-[10px] pt-0.5">{h.remarks}</p>}
                        </div>
                        <div className="text-right text-[#5c7885]">
                          <p>{new Date(h.changed_at).toLocaleString()}</p>
                          <span className="text-[10px] text-purple-400">{h.changed_by}</span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Footer Actions */}
              <div className="flex items-center justify-between pt-4 border-t border-[#c8d8e4]">
                {selectedTrip.trip_status !== 'COMPLETED' && selectedTrip.trip_status !== 'CANCELLED' ? (
                  <button
                    onClick={() => handleCancelTrip(selectedTrip.id)}
                    className="px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 font-bold text-xs rounded-xl"
                  >
                    Cancel Trip
                  </button>
                ) : <div />}

                <button
                  onClick={() => setShowDetailModal(false)}
                  className="px-5 py-2 bg-[#f2f2f2] border border-[#c8d8e4] text-[#1a3b45] font-bold text-xs rounded-xl hover:bg-[#e8eff4]"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
