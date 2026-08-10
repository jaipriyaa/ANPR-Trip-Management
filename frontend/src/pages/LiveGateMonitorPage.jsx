import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import DeepStreamStreamManager from '../components/deepstream/DeepStreamStreamManager';
import { 
  Activity, 
  Video, 
  ShieldAlert, 
  CheckCircle2, 
  Clock, 
  Truck, 
  LogIn, 
  LogOut, 
  AlertTriangle, 
  RefreshCw, 
  Search, 
  Eye, 
  Radio,
  Calendar,
  Layers,
  MapPin,
  User,
  ShieldCheck,
  Zap,
  Maximize2
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function LiveGateMonitorPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [activeTab, setActiveTab] = useState('INSIDE'); // 'INSIDE' | 'TRIPS' | 'TIMELINE' | 'ALERTS'
  const [searchTerm, setSearchTerm] = useState('');
  const [gateFilter, setGateFilter] = useState('ALL');

  const fetchControlRoomData = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/live/dashboard`);
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch (err) {
      console.error('Failed to fetch live control room data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchControlRoomData();
    let interval = null;
    if (autoRefresh) {
      interval = setInterval(fetchControlRoomData, 3000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const summary = data?.summary || {
    vehicles_currently_inside: 0,
    vehicles_entered_today: 0,
    vehicles_exited_today: 0,
    active_trips_count: 0,
    unauthorized_vehicles_count: 0,
    alerts_count: 0,
    avg_stay_time_formatted: '0m'
  };

  const cameras = data?.cameras || [];
  const curVeh = data?.current_vehicle;
  const timeline = data?.timeline || [];
  const alerts = data?.alerts || [];
  const activeTrips = data?.active_trips || [];
  const insideVehicles = data?.inside_vehicles || [];

  // Helper for image URLs
  const getImageUrl = (path) => {
    if (!path) return null;
    if (path.startsWith('http')) return path;
    const cleanPath = path.startsWith('/') ? path.slice(1) : path;
    return `${API_BASE_URL}/vehicle-recognition/media/${cleanPath}`;
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-[#f2f2f2] text-[#1a3b45] font-sans">
      <Header title="Live Gate Monitor — Factory Control Room" subtitle="Real-time perimeter surveillance, live ANPR camera streams, automated vehicle verification & security alert engine" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Top Control Bar: Search & Auto Refresh Toggle */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white rounded-xl p-4 border border-[#c8d8e4] backdrop-blur-md">
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <div className="flex items-center gap-2 text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-3 py-1.5 rounded-xl text-xs font-mono">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
              CONTROL ROOM STREAM ACTIVE
            </div>
            <span className="text-xs text-[#5c7885] font-mono hidden sm:inline">Last Sync: {data?.timestamp || 'Just now'}</span>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <div className="relative w-full sm:w-64">
              <Search className="w-4 h-4 text-[#5c7885] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search Plate, Driver, Transporter..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-4 py-1.5 bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl text-xs text-[#1a3b45] placeholder-slate-500 focus:outline-none focus:border-cyan-500"
              />
            </div>

            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all border ${
                autoRefresh
                  ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30'
                  : 'bg-[#e8eff4] text-[#5c7885] border-[#c8d8e4]'
              }`}
            >
              <RefreshCw className={`w-3.5 h-3.5 ${autoRefresh ? 'animate-spin' : ''}`} />
              {autoRefresh ? 'Auto 3s' : 'Paused'}
            </button>
          </div>
        </div>

        {/* Top 7 Summary Cards Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
          {/* 1. Vehicles Inside */}
          <div className="bg-white rounded-xl p-3 border border-emerald-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Vehicles Inside</p>
            <p className="text-2xl font-extrabold text-emerald-400 font-mono mt-1">{summary.vehicles_currently_inside}</p>
            <p className="text-[10px] text-emerald-400/80 font-mono mt-0.5">Occupancy</p>
          </div>

          {/* 2. Entered Today */}
          <div className="bg-white rounded-xl p-3 border border-blue-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Entered Today</p>
            <p className="text-2xl font-extrabold text-blue-400 font-mono mt-1">{summary.vehicles_entered_today}</p>
            <p className="text-[10px] text-blue-400/80 font-mono mt-0.5">Inbound</p>
          </div>

          {/* 3. Exited Today */}
          <div className="bg-white rounded-xl p-3 border border-[#c8d8e4] backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Exited Today</p>
            <p className="text-2xl font-extrabold text-[#2b6777] font-mono mt-1">{summary.vehicles_exited_today}</p>
            <p className="text-[10px] text-[#5c7885] font-mono mt-0.5">Outbound</p>
          </div>

          {/* 4. Active Trips */}
          <div className="bg-white rounded-xl p-3 border border-cyan-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Active Trips</p>
            <p className="text-2xl font-extrabold text-cyan-400 font-mono mt-1">{summary.active_trips_count}</p>
            <p className="text-[10px] text-cyan-400/80 font-mono mt-0.5">Scheduled</p>
          </div>

          {/* 5. Unauthorized */}
          <div className="bg-white rounded-xl p-3 border border-red-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Unauthorized</p>
            <p className="text-2xl font-extrabold text-red-400 font-mono mt-1">{summary.unauthorized_vehicles_count}</p>
            <p className="text-[10px] text-red-400/80 font-mono mt-0.5">Flagged</p>
          </div>

          {/* 6. Alerts */}
          <div className="bg-white rounded-xl p-3 border border-amber-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Live Alerts</p>
            <p className="text-2xl font-extrabold text-amber-400 font-mono mt-1">{summary.alerts_count}</p>
            <p className="text-[10px] text-amber-400/80 font-mono mt-0.5">Engine Flags</p>
          </div>

          {/* 7. Avg Stay Time */}
          <div className="bg-white rounded-xl p-3 border border-purple-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Avg Stay Time</p>
            <p className="text-lg font-bold text-purple-300 font-mono mt-1.5">{summary.avg_stay_time_formatted}</p>
            <p className="text-[10px] text-purple-400/80 font-mono mt-0.5">Turnaround</p>
          </div>
        </div>

        {/* NVIDIA DeepStream Hardware Acceleration Stream Manager */}
        <DeepStreamStreamManager />

        {/* Main Control Room Split View */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column (2 Cols): Live Gate Cameras Feed */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-[#1a3b45] flex items-center gap-2 uppercase tracking-wider">
                <Video className="w-4 h-4 text-cyan-400" /> Live Gate ANPR Camera Streams
              </h3>
              <span className="text-xs text-[#5c7885] font-mono">{cameras.length} Cameras Online</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {cameras.length === 0 ? (
                <div className="col-span-2 bg-white border border-[#c8d8e4] rounded-xl p-8 text-center text-[#5c7885]">
                  <Video className="w-8 h-8 mx-auto mb-2 opacity-40 text-cyan-400" />
                  No gate cameras configured. Assign cameras in Gate Management to stream feeds.
                </div>
              ) : (
                cameras.map((cam) => {
                  const ov = cam.detection_overlay;
                  return (
                    <div key={cam.camera_id} className="bg-white border border-[#c8d8e4] rounded-xl overflow-hidden shadow-xl backdrop-blur-md flex flex-col">
                      {/* Camera Stream Header */}
                      <div className="p-3 bg-[#f2f2f2] border-b border-[#c8d8e4] flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2">
                          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                          <span className="font-bold text-[#1a3b45]">{cam.camera_name}</span>
                          <span className="text-[10px] text-cyan-400 bg-cyan-500/10 px-1.5 py-0.5 rounded border border-cyan-500/20">{cam.gate_code}</span>
                        </div>
                        <div className="flex items-center gap-2 text-[10px] font-mono text-[#5c7885]">
                          <span>{cam.fps} FPS</span>
                          <span>•</span>
                          <span>{cam.current_time}</span>
                        </div>
                      </div>

                      {/* Video Stream Simulated Container with AI Bounding Box Overlay */}
                      <div className="relative aspect-video bg-[#f2f2f2] flex items-center justify-center overflow-hidden border-b border-[#c8d8e4]">
                        {curVeh?.cropped_vehicle_path ? (
                          <img src={getImageUrl(curVeh.cropped_vehicle_path)} alt="Camera Feed" className="w-full h-full object-cover opacity-80" />
                        ) : (
                          <div className="w-full h-full bg-gradient-to-tr from-slate-950 via-slate-900 to-slate-950 flex flex-col items-center justify-center p-4">
                            <Radio className="w-10 h-10 text-cyan-400/40 animate-pulse mb-2" />
                            <span className="text-xs font-mono text-[#5c7885]">RTSP Stream Live Feed ({cam.resolution})</span>
                            <span className="text-[10px] font-mono text-slate-600">{cam.rtsp_url}</span>
                          </div>
                        )}

                        {/* ANPR AI Bounding Box Overlay Badges */}
                        {ov && (
                          <div className="absolute inset-0 pointer-events-none p-4 flex flex-col justify-between">
                            <div className="self-start bg-white backdrop-blur-md border border-cyan-500/60 rounded px-2.5 py-1 text-[11px] font-mono text-cyan-300 shadow-lg">
                              <span className="text-emerald-400 font-bold">DETECTION:</span> {ov.recognized_plate} ({(ov.confidence * 100).toFixed(1)}%)
                            </div>

                            <div className="self-end bg-white backdrop-blur-md border border-emerald-500/60 rounded px-2 py-0.5 text-[10px] font-mono text-emerald-400">
                              BOUNDING BOX LOCKED [{cam.camera_position}]
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Stream Footer Info */}
                      <div className="p-2.5 bg-white flex items-center justify-between text-[11px] text-[#5c7885] font-mono">
                        <span className="flex items-center gap-1"><MapPin className="w-3 h-3 text-[#5c7885]" /> {cam.gate_name}</span>
                        <span className="text-emerald-400">STATUS: {cam.camera_status.toUpperCase()}</span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Right Column (1 Col): Current Recognized Vehicle Focus Panel */}
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-[#1a3b45] flex items-center gap-2 uppercase tracking-wider">
              <Zap className="w-4 h-4 text-cyan-400" /> Current Vehicle Recognized
            </h3>

            {curVeh ? (
              <div className="bg-white border border-[#c8d8e4] rounded-xl p-5 space-y-4 backdrop-blur-md shadow-2xl">
                {/* Crops Row */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <span className="text-[10px] text-[#5c7885] uppercase font-semibold">Vehicle Crop</span>
                    <div className="h-24 rounded-lg overflow-hidden border border-[#c8d8e4] bg-[#f2f2f2] flex items-center justify-center">
                      {curVeh.cropped_vehicle_path ? (
                        <img src={getImageUrl(curVeh.cropped_vehicle_path)} alt="Vehicle Crop" className="w-full h-full object-cover" />
                      ) : (
                        <Truck className="w-8 h-8 text-[#2b6777]" />
                      )}
                    </div>
                  </div>

                  <div className="space-y-1">
                    <span className="text-[10px] text-[#5c7885] uppercase font-semibold">Plate Crop</span>
                    <div className="h-24 rounded-lg overflow-hidden border border-[#c8d8e4] bg-[#f2f2f2] flex items-center justify-center">
                      {curVeh.cropped_plate_path ? (
                        <img src={getImageUrl(curVeh.cropped_plate_path)} alt="Plate Crop" className="w-full h-full object-cover" />
                      ) : (
                        <span className="text-xs font-mono text-cyan-400">{curVeh.recognized_plate}</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Primary Recognized Plate Header */}
                <div className="bg-[#f2f2f2] rounded-xl p-3 border border-cyan-500/30 flex items-center justify-between">
                  <div>
                    <p className="text-[10px] text-[#5c7885] uppercase font-semibold">Recognized License Plate</p>
                    <p className="text-xl font-mono font-extrabold text-cyan-400">{curVeh.recognized_plate}</p>
                  </div>
                  <div className="text-right">
                    <span className="px-2 py-1 rounded text-[10px] font-mono font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                      {((curVeh.confidence || 0.985) * 100).toFixed(1)}% CONF
                    </span>
                  </div>
                </div>

                {/* Grid Metadata */}
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="bg-white p-2.5 rounded-lg border border-[#c8d8e4]">
                    <span className="text-[#5c7885] text-[10px] block">Vehicle Type</span>
                    <span className="font-semibold text-[#1a3b45]">{curVeh.vehicle_type}</span>
                  </div>

                  <div className="bg-white p-2.5 rounded-lg border border-[#c8d8e4]">
                    <span className="text-[#5c7885] text-[10px] block">Entry Gate</span>
                    <span className="font-semibold text-blue-400">{curVeh.entry_gate_code}</span>
                  </div>

                  <div className="bg-white p-2.5 rounded-lg border border-[#c8d8e4]">
                    <span className="text-[#5c7885] text-[10px] block">Entry Timestamp</span>
                    <span className="font-mono text-[#2b6777] text-[11px]">
                      {curVeh.entry_time ? new Date(curVeh.entry_time).toLocaleTimeString() : 'Just now'}
                    </span>
                  </div>

                  <div className="bg-white p-2.5 rounded-lg border border-[#c8d8e4]">
                    <span className="text-[#5c7885] text-[10px] block">Stay Duration</span>
                    <span className="font-mono font-semibold text-emerald-400">{curVeh.stay_duration_formatted}</span>
                  </div>

                  <div className="bg-white p-2.5 rounded-lg border border-[#c8d8e4] col-span-2">
                    <span className="text-[#5c7885] text-[10px] block">Driver & Transporter</span>
                    <span className="font-semibold text-[#1a3b45]">{curVeh.driver_name}</span>
                    <span className="text-[11px] text-purple-400 block">{curVeh.transporter_name}</span>
                  </div>
                </div>

                {/* Authorization Status Badge */}
                <div className={`p-3 rounded-xl border flex items-center justify-between ${
                  curVeh.authorization_status === 'AUTHORIZED'
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                    : 'bg-red-500/10 text-red-400 border-red-500/30'
                }`}>
                  <span className="text-xs font-bold font-mono flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4" /> AUTHORIZATION: {curVeh.authorization_status}
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#f2f2f2]">
                    {curVeh.movement_status}
                  </span>
                </div>
              </div>
            ) : (
              <div className="bg-white border border-[#c8d8e4] rounded-xl p-8 text-center text-[#5c7885]">
                Awaiting vehicle detection...
              </div>
            )}
          </div>
        </div>

        {/* Bottom Control Room Tabbed Panels */}
        <div className="bg-white border border-[#c8d8e4] rounded-xl overflow-hidden backdrop-blur-md">
          {/* Tab Header */}
          <div className="flex items-center gap-2 border-b border-[#c8d8e4] bg-[#f2f2f2] px-4 pt-3 overflow-x-auto">
            <button
              onClick={() => setActiveTab('INSIDE')}
              className={`px-4 py-2 text-xs font-bold border-b-2 transition-all flex items-center gap-2 whitespace-nowrap ${
                activeTab === 'INSIDE'
                  ? 'border-emerald-400 text-emerald-400 bg-emerald-500/10'
                  : 'border-transparent text-[#5c7885] hover:text-[#1a3b45]'
              }`}
            >
              <Truck className="w-4 h-4" /> Vehicles Currently Inside ({summary.vehicles_currently_inside})
            </button>

            <button
              onClick={() => setActiveTab('TRIPS')}
              className={`px-4 py-2 text-xs font-bold border-b-2 transition-all flex items-center gap-2 whitespace-nowrap ${
                activeTab === 'TRIPS'
                  ? 'border-cyan-400 text-cyan-400 bg-cyan-500/10'
                  : 'border-transparent text-[#5c7885] hover:text-[#1a3b45]'
              }`}
            >
              <Calendar className="w-4 h-4" /> Active Scheduled Trips ({activeTrips.length})
            </button>

            <button
              onClick={() => setActiveTab('TIMELINE')}
              className={`px-4 py-2 text-xs font-bold border-b-2 transition-all flex items-center gap-2 whitespace-nowrap ${
                activeTab === 'TIMELINE'
                  ? 'border-blue-400 text-blue-400 bg-blue-500/10'
                  : 'border-transparent text-[#5c7885] hover:text-[#1a3b45]'
              }`}
            >
              <Clock className="w-4 h-4" /> Live Event Timeline ({timeline.length})
            </button>

            <button
              onClick={() => setActiveTab('ALERTS')}
              className={`px-4 py-2 text-xs font-bold border-b-2 transition-all flex items-center gap-2 whitespace-nowrap ${
                activeTab === 'ALERTS'
                  ? 'border-amber-400 text-amber-400 bg-amber-500/10'
                  : 'border-transparent text-[#5c7885] hover:text-[#1a3b45]'
              }`}
            >
              <ShieldAlert className="w-4 h-4" /> Security & Operational Alerts ({alerts.length})
            </button>
          </div>

          {/* Tab Content */}
          <div className="p-4">
            {/* Tab 1: Current Vehicles Inside */}
            {activeTab === 'INSIDE' && (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-[#2b6777]">
                  <thead className="bg-[#f2f2f2] text-[#5c7885] uppercase text-[10px] tracking-wider border-b border-[#c8d8e4]">
                    <tr>
                      <th className="p-3">Plate Number</th>
                      <th className="p-3">Vehicle Type</th>
                      <th className="p-3">Entry Gate</th>
                      <th className="p-3">Entry Time</th>
                      <th className="p-3">Stay Duration</th>
                      <th className="p-3">Destination</th>
                      <th className="p-3">Driver</th>
                      <th className="p-3 text-right">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono">
                    {insideVehicles.length === 0 ? (
                      <tr>
                        <td colSpan="8" className="p-6 text-center text-[#5c7885] font-sans">No vehicles currently inside facility.</td>
                      </tr>
                    ) : (
                      insideVehicles.map((m) => (
                        <tr key={m.id} className="hover:bg-[#f0f6f8]">
                          <td className="p-3 font-bold text-cyan-400">{m.recognized_plate}</td>
                          <td className="p-3 text-[#1a3b45] font-sans">{m.vehicle_type || 'SUV'}</td>
                          <td className="p-3 text-blue-400">{m.entry_gate_code || 'GATE-NORTH-01'}</td>
                          <td className="p-3 text-[#5c7885]">{new Date(m.entry_time).toLocaleTimeString()}</td>
                          <td className="p-3 text-emerald-400 font-bold">{m.stay_duration_formatted || 'In Progress'}</td>
                          <td className="p-3 text-[#2b6777] font-sans">{m.destination || 'Main Assembly Bay'}</td>
                          <td className="p-3 text-[#2b6777] font-sans">{m.driver_name || 'Driver'}</td>
                          <td className="p-3 text-right">
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                              INSIDE
                            </span>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {/* Tab 2: Active Scheduled Trips */}
            {activeTab === 'TRIPS' && (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-[#2b6777]">
                  <thead className="bg-[#f2f2f2] text-[#5c7885] uppercase text-[10px] tracking-wider border-b border-[#c8d8e4]">
                    <tr>
                      <th className="p-3">Trip ID</th>
                      <th className="p-3">Scheduled Plate</th>
                      <th className="p-3">Vehicle Type</th>
                      <th className="p-3">Expected Gate</th>
                      <th className="p-3">Expected Entry</th>
                      <th className="p-3">Expected Exit</th>
                      <th className="p-3">Purpose</th>
                      <th className="p-3 text-right">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono">
                    {activeTrips.map((t) => (
                      <tr key={t.trip_id} className="hover:bg-[#f0f6f8]">
                        <td className="p-3 font-bold text-purple-400">{t.trip_id}</td>
                        <td className="p-3 font-bold text-cyan-400">{t.scheduled_vehicle}</td>
                        <td className="p-3 text-[#1a3b45] font-sans">{t.vehicle_type}</td>
                        <td className="p-3 text-blue-400">{t.expected_gate}</td>
                        <td className="p-3 text-[#5c7885]">{t.expected_entry_time}</td>
                        <td className="p-3 text-[#5c7885]">{t.expected_exit_time}</td>
                        <td className="p-3 text-[#2b6777] font-sans">{t.purpose}</td>
                        <td className="p-3 text-right">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                            t.current_status === 'Inside'
                              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                              : t.current_status === 'Completed'
                              ? 'bg-[#e8eff4] text-[#5c7885] border-[#c8d8e4]'
                              : 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30'
                          }`}>
                            {t.current_status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Tab 3: Live Event Timeline */}
            {activeTab === 'TIMELINE' && (
              <div className="space-y-3 font-mono">
                {timeline.length === 0 ? (
                  <p className="text-center text-[#5c7885] p-6 font-sans">No live timeline events logged.</p>
                ) : (
                  timeline.map((evt) => (
                    <div key={evt.id} className="flex items-center justify-between bg-[#f2f2f2] p-3 rounded-xl border border-[#c8d8e4] text-xs">
                      <div className="flex items-center gap-3">
                        <span className="text-[#5c7885] font-bold">{evt.timestamp}</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                          evt.event_type.includes('Entered')
                            ? 'bg-blue-500/10 text-blue-400 border-blue-500/30'
                            : 'bg-[#e8eff4] text-[#5c7885] border-[#c8d8e4]'
                        }`}>
                          {evt.event_type}
                        </span>
                        <span className="font-bold text-cyan-400 text-sm">{evt.plate_number}</span>
                        <span className="text-[#5c7885] font-sans">({evt.vehicle_type})</span>
                      </div>
                      <span className="text-[#5c7885] text-[11px]">{evt.gate_code}</span>
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Tab 4: Live Security & Operational Alerts */}
            {activeTab === 'ALERTS' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {alerts.length === 0 ? (
                  <div className="col-span-2 text-center text-[#5c7885] p-6">No active security alerts.</div>
                ) : (
                  alerts.map((alt) => (
                    <div key={alt.id} className={`p-4 rounded-xl border flex items-start justify-between backdrop-blur-md ${
                      alt.level === 'red'
                        ? 'bg-red-500/10 border-red-500/30 text-red-300'
                        : alt.level === 'yellow'
                        ? 'bg-amber-500/10 border-amber-500/30 text-amber-300'
                        : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                    }`}>
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <AlertTriangle className="w-4 h-4" />
                          <h4 className="font-bold text-xs">{alt.title}</h4>
                        </div>
                        <p className="text-xs opacity-90">{alt.message}</p>
                        <span className="text-[10px] font-mono opacity-60 block pt-1">
                          Gate: {alt.gate_code} • Category: {alt.category}
                        </span>
                      </div>
                      <span className="text-[10px] font-mono opacity-70">{alt.timestamp}</span>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
