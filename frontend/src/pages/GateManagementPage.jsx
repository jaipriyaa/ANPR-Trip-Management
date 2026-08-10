import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import Modal from '../components/Modal';
import { 
  Video, 
  Camera, 
  Sliders, 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  CheckCircle, 
  XCircle, 
  RefreshCw, 
  ShieldCheck, 
  Activity, 
  MapPin, 
  Layers, 
  Clock, 
  ChevronLeft, 
  ChevronRight,
  AlertTriangle,
  Info,
  Check,
  X
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function GateManagementPage() {
  const [activeTab, setActiveTab] = useState('gates'); // 'gates' | 'cameras' | 'rules'

  // Gates State
  const [gates, setGates] = useState([]);
  const [gatesTotal, setGatesTotal] = useState(0);
  const [gatesLoading, setGatesLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const limit = 10;

  // Selected Gate for Modals / Rule editing
  const [selectedGate, setSelectedGate] = useState(null);

  // Modals
  const [isAddGateOpen, setIsAddGateOpen] = useState(false);
  const [isEditGateOpen, setIsEditGateOpen] = useState(false);
  const [isDeleteGateOpen, setIsDeleteGateOpen] = useState(false);

  // Form State - Gate
  const [gateForm, setGateForm] = useState({
    gate_code: '',
    gate_name: '',
    gate_type: 'Entry & Exit',
    location: '',
    description: '',
    status: 'ACTIVE',
    is_active: true
  });

  // Cameras State
  const [cameras, setCameras] = useState([]);
  const [camerasTotal, setCamerasTotal] = useState(0);
  const [camerasLoading, setCamerasLoading] = useState(false);
  const [cameraFilterGateId, setCameraFilterGateId] = useState('');
  const [isAddCameraOpen, setIsAddCameraOpen] = useState(false);
  const [isEditCameraOpen, setIsEditCameraOpen] = useState(false);
  const [isDeleteCameraOpen, setIsDeleteCameraOpen] = useState(false);
  const [selectedCamera, setSelectedCamera] = useState(null);

  const [cameraForm, setCameraForm] = useState({
    gate_id: '',
    camera_name: '',
    camera_position: 'Entry Camera',
    rtsp_url: '',
    ip_address: '',
    camera_status: 'Online',
    resolution: '1080p',
    fps: 30,
    is_active: true
  });

  // Gate Rules State
  const [rulesGateId, setRulesGateId] = useState('');
  const [rulesLoading, setRulesLoading] = useState(false);
  const [ruleForm, setRuleForm] = useState({
    allow_entry: true,
    allow_exit: true,
    allow_trucks: true,
    allow_buses: true,
    allow_cars: true,
    allow_two_wheelers: false,
    maximum_vehicle_height: 4.5,
    maximum_vehicle_weight: 40.0,
    authorized_only: true,
    working_hours_start: '06:00',
    working_hours_end: '22:00',
    remarks: ''
  });

  // Notification Banner State
  const [notification, setNotification] = useState(null);

  const showNotification = (msg, type = 'success') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4000);
  };

  // Fetch Gates
  const fetchGates = async () => {
    setGatesLoading(true);
    try {
      const skip = (page - 1) * limit;
      let url = `${API_BASE_URL}/gates?skip=${skip}&limit=${limit}`;
      if (searchTerm) url += `&search=${encodeURIComponent(searchTerm)}`;

      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setGates(data.items || []);
        setGatesTotal(data.total || 0);

        // Auto select first gate for rules if not selected
        if (data.items?.length > 0 && !rulesGateId) {
          setRulesGateId(data.items[0].id);
        }
      }
    } catch (err) {
      console.error('Failed to fetch gates:', err);
    } finally {
      setGatesLoading(false);
    }
  };

  // Fetch Cameras
  const fetchCameras = async () => {
    setCamerasLoading(true);
    try {
      let url = `${API_BASE_URL}/gate-cameras?limit=100`;
      if (cameraFilterGateId) url += `&gate_id=${cameraFilterGateId}`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setCameras(data.items || []);
        setCamerasTotal(data.total || 0);
      }
    } catch (err) {
      console.error('Failed to fetch cameras:', err);
    } finally {
      setCamerasLoading(false);
    }
  };

  // Fetch Gate Rule
  const fetchGateRule = async (gateId) => {
    if (!gateId) return;
    setRulesLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/gate-rules/${gateId}`);
      if (res.ok) {
        const data = await res.json();
        setRuleForm({
          allow_entry: data.allow_entry ?? true,
          allow_exit: data.allow_exit ?? true,
          allow_trucks: data.allow_trucks ?? true,
          allow_buses: data.allow_buses ?? true,
          allow_cars: data.allow_cars ?? true,
          allow_two_wheelers: data.allow_two_wheelers ?? false,
          maximum_vehicle_height: data.maximum_vehicle_height ?? 4.5,
          maximum_vehicle_weight: data.maximum_vehicle_weight ?? 40.0,
          authorized_only: data.authorized_only ?? true,
          working_hours_start: data.working_hours_start || '06:00',
          working_hours_end: data.working_hours_end || '22:00',
          remarks: data.remarks || ''
        });
      }
    } catch (err) {
      console.error('Failed to fetch gate rules:', err);
    } finally {
      setRulesLoading(false);
    }
  };

  useEffect(() => {
    fetchGates();
  }, [page, searchTerm]);

  useEffect(() => {
    if (activeTab === 'cameras') {
      fetchCameras();
    }
  }, [activeTab, cameraFilterGateId]);

  useEffect(() => {
    if (activeTab === 'rules' && rulesGateId) {
      fetchGateRule(rulesGateId);
    }
  }, [activeTab, rulesGateId]);

  // Handlers - Gate
  const handleCreateGate = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE_URL}/gates`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(gateForm)
      });
      if (res.ok) {
        showNotification(`Gate '${gateForm.gate_code}' created successfully!`);
        setIsAddGateOpen(false);
        setGateForm({
          gate_code: '',
          gate_name: '',
          gate_type: 'Entry & Exit',
          location: '',
          description: '',
          status: 'ACTIVE',
          is_active: true
        });
        fetchGates();
      } else {
        const errorData = await res.json();
        showNotification(errorData.detail || 'Failed to create gate', 'error');
      }
    } catch (err) {
      showNotification('Network error while creating gate', 'error');
    }
  };

  const handleUpdateGate = async (e) => {
    e.preventDefault();
    if (!selectedGate) return;
    try {
      const res = await fetch(`${API_BASE_URL}/gates/${selectedGate.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(gateForm)
      });
      if (res.ok) {
        showNotification(`Gate '${selectedGate.gate_code}' updated successfully!`);
        setIsEditGateOpen(false);
        fetchGates();
      } else {
        const errorData = await res.json();
        showNotification(errorData.detail || 'Failed to update gate', 'error');
      }
    } catch (err) {
      showNotification('Network error while updating gate', 'error');
    }
  };

  const handleDeleteGate = async () => {
    if (!selectedGate) return;
    try {
      const res = await fetch(`${API_BASE_URL}/gates/${selectedGate.id}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        showNotification(`Gate '${selectedGate.gate_code}' deleted successfully!`);
        setIsDeleteGateOpen(false);
        fetchGates();
      } else {
        const errorData = await res.json();
        showNotification(errorData.detail || 'Failed to delete gate', 'error');
      }
    } catch (err) {
      showNotification('Network error while deleting gate', 'error');
    }
  };

  // Handlers - Camera
  const handleCreateCamera = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE_URL}/gate-cameras`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cameraForm)
      });
      if (res.ok) {
        showNotification(`Camera '${cameraForm.camera_name}' assigned successfully!`);
        setIsAddCameraOpen(false);
        fetchCameras();
        fetchGates();
      } else {
        const errorData = await res.json();
        showNotification(errorData.detail || 'Failed to assign camera', 'error');
      }
    } catch (err) {
      showNotification('Network error while assigning camera', 'error');
    }
  };

  const handleUpdateCamera = async (e) => {
    e.preventDefault();
    if (!selectedCamera) return;
    try {
      const res = await fetch(`${API_BASE_URL}/gate-cameras/${selectedCamera.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cameraForm)
      });
      if (res.ok) {
        showNotification(`Camera '${selectedCamera.camera_name}' updated successfully!`);
        setIsEditCameraOpen(false);
        fetchCameras();
      } else {
        const errorData = await res.json();
        showNotification(errorData.detail || 'Failed to update camera', 'error');
      }
    } catch (err) {
      showNotification('Network error while updating camera', 'error');
    }
  };

  const handleDeleteCamera = async () => {
    if (!selectedCamera) return;
    try {
      const res = await fetch(`${API_BASE_URL}/gate-cameras/${selectedCamera.id}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        showNotification(`Camera '${selectedCamera.camera_name}' removed!`);
        setIsDeleteCameraOpen(false);
        fetchCameras();
        fetchGates();
      } else {
        const errorData = await res.json();
        showNotification(errorData.detail || 'Failed to remove camera', 'error');
      }
    } catch (err) {
      showNotification('Network error while removing camera', 'error');
    }
  };

  // Handlers - Gate Rules
  const handleSaveRules = async (e) => {
    e.preventDefault();
    if (!rulesGateId) return;
    try {
      const res = await fetch(`${API_BASE_URL}/gate-rules`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          gate_id: rulesGateId,
          ...ruleForm
        })
      });
      if (res.ok) {
        showNotification('Gate rules updated successfully!');
      } else {
        const errorData = await res.json();
        showNotification(errorData.detail || 'Failed to save gate rules', 'error');
      }
    } catch (err) {
      showNotification('Network error while saving gate rules', 'error');
    }
  };

  const totalPages = Math.ceil(gatesTotal / limit) || 1;

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-slate-950 text-slate-100">
      <Header title="Gate & Camera Management" subtitle="Manage factory perimeter gates, assigned RTSP cameras, and security gate rules" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Notification Toast */}
        {notification && (
          <div className={`p-4 rounded-xl border flex items-center justify-between shadow-lg backdrop-blur-md transition-all ${
            notification.type === 'error'
              ? 'bg-rose-500/10 border-rose-500/30 text-rose-400'
              : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
          }`}>
            <div className="flex items-center gap-2.5 text-xs font-semibold">
              {notification.type === 'error' ? <AlertTriangle className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />}
              <span>{notification.msg}</span>
            </div>
            <button onClick={() => setNotification(null)} className="text-slate-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Header Summary Statistics Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-900/60 rounded-xl p-4 border border-slate-800 backdrop-blur-md flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-400 font-medium">Total Gates</p>
              <p className="text-2xl font-bold text-white mt-1 font-mono">{gatesTotal}</p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
              <Video className="w-5 h-5" />
            </div>
          </div>

          <div className="bg-slate-900/60 rounded-xl p-4 border border-slate-800 backdrop-blur-md flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-400 font-medium">Active Gates</p>
              <p className="text-2xl font-bold text-emerald-400 mt-1 font-mono">
                {gates.filter(g => g.status === 'ACTIVE').length}
              </p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
          </div>

          <div className="bg-slate-900/60 rounded-xl p-4 border border-slate-800 backdrop-blur-md flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-400 font-medium">Assigned Cameras</p>
              <p className="text-2xl font-bold text-purple-400 mt-1 font-mono">{camerasTotal}</p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
              <Camera className="w-5 h-5" />
            </div>
          </div>

          <div className="bg-slate-900/60 rounded-xl p-4 border border-slate-800 backdrop-blur-md flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-400 font-medium">Gate Security Engine</p>
              <p className="text-xs font-semibold text-emerald-400 mt-1 flex items-center gap-1 font-mono">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Active Enforcer
              </p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
              <Sliders className="w-5 h-5" />
            </div>
          </div>
        </div>

        {/* Tab Sub-Navigation */}
        <div className="flex border-b border-slate-800 gap-6">
          <button
            onClick={() => setActiveTab('gates')}
            className={`pb-3 text-xs font-semibold flex items-center gap-2 border-b-2 transition-all ${
              activeTab === 'gates'
                ? 'border-cyan-400 text-cyan-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Video className="w-4 h-4" /> Gate Master Table ({gatesTotal})
          </button>

          <button
            onClick={() => setActiveTab('cameras')}
            className={`pb-3 text-xs font-semibold flex items-center gap-2 border-b-2 transition-all ${
              activeTab === 'cameras'
                ? 'border-cyan-400 text-cyan-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Camera className="w-4 h-4" /> Camera Assignment
          </button>

          <button
            onClick={() => setActiveTab('rules')}
            className={`pb-3 text-xs font-semibold flex items-center gap-2 border-b-2 transition-all ${
              activeTab === 'rules'
                ? 'border-cyan-400 text-cyan-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sliders className="w-4 h-4" /> Gate Rules & Limits Configuration
          </button>
        </div>

        {/* TAB 1: GATE MASTER TABLE */}
        {activeTab === 'gates' && (
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="relative w-full sm:w-80">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search by Gate Code, Name, or Location..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="flex items-center gap-3 w-full sm:w-auto">
                <button
                  onClick={fetchGates}
                  className="p-2 bg-slate-900 border border-slate-800 rounded-xl text-slate-400 hover:text-white transition-all"
                  title="Refresh Gates"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>

                <button
                  onClick={() => {
                    setGateForm({
                      gate_code: '',
                      gate_name: '',
                      gate_type: 'Entry & Exit',
                      location: '',
                      description: '',
                      status: 'ACTIVE',
                      is_active: true
                    });
                    setIsAddGateOpen(true);
                  }}
                  className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-2 shadow-lg shadow-cyan-500/20"
                >
                  <Plus className="w-4 h-4" /> Add Factory Gate
                </button>
              </div>
            </div>

            {/* Gates Table */}
            <div className="bg-slate-900/60 rounded-xl border border-slate-800 overflow-hidden backdrop-blur-md">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
                    <tr>
                      <th className="p-4">Gate Code</th>
                      <th className="p-4">Gate Name</th>
                      <th className="p-4">Gate Type</th>
                      <th className="p-4">Location</th>
                      <th className="p-4">Status</th>
                      <th className="p-4">Cameras</th>
                      <th className="p-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {gatesLoading ? (
                      <tr>
                        <td colSpan="7" className="p-8 text-center text-slate-500">Loading factory gates...</td>
                      </tr>
                    ) : gates.length === 0 ? (
                      <tr>
                        <td colSpan="7" className="p-8 text-center text-slate-500">
                          <Video className="w-8 h-8 mx-auto mb-2 opacity-50 text-cyan-400" />
                          No factory gates found. Click "Add Factory Gate" to create one.
                        </td>
                      </tr>
                    ) : (
                      gates.map((g) => (
                        <tr key={g.id} className="hover:bg-slate-800/40 transition-colors">
                          <td className="p-4 font-mono font-bold text-cyan-400">{g.gate_code}</td>
                          <td className="p-4 font-semibold text-white">{g.gate_name}</td>
                          <td className="p-4">
                            <span className={`px-2.5 py-1 rounded text-[11px] font-semibold border ${
                              g.gate_type === 'Entry'
                                ? 'bg-blue-500/10 text-blue-400 border-blue-500/30'
                                : g.gate_type === 'Exit'
                                ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                                : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                            }`}>
                              {g.gate_type}
                            </span>
                          </td>
                          <td className="p-4 text-slate-400 flex items-center gap-1.5">
                            <MapPin className="w-3.5 h-3.5 text-slate-500" /> {g.location || 'N/A'}
                          </td>
                          <td className="p-4">
                            <span className={`px-2.5 py-1 rounded text-[11px] font-bold font-mono border ${
                              g.status === 'ACTIVE'
                                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                                : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                            }`}>
                              {g.status}
                            </span>
                          </td>
                          <td className="p-4 font-mono text-purple-400 font-semibold">
                            {g.camera_count || g.cameras?.length || 0} Cameras
                          </td>
                          <td className="p-4 text-right">
                            <div className="flex items-center justify-end gap-2">
                              <button
                                onClick={() => {
                                  setCameraFilterGateId(g.id);
                                  setActiveTab('cameras');
                                }}
                                className="p-1.5 bg-purple-500/10 border border-purple-500/30 text-purple-400 hover:bg-purple-500/20 rounded-lg text-[11px] font-semibold flex items-center gap-1"
                                title="Manage Cameras"
                              >
                                <Camera className="w-3.5 h-3.5" /> Cameras
                              </button>

                              <button
                                onClick={() => {
                                  setRulesGateId(g.id);
                                  setActiveTab('rules');
                                }}
                                className="p-1.5 bg-blue-500/10 border border-blue-500/30 text-blue-400 hover:bg-blue-500/20 rounded-lg text-[11px] font-semibold flex items-center gap-1"
                                title="Configure Rules"
                              >
                                <Sliders className="w-3.5 h-3.5" /> Rules
                              </button>

                              <button
                                onClick={() => {
                                  setSelectedGate(g);
                                  setGateForm({
                                    gate_code: g.gate_code,
                                    gate_name: g.gate_name,
                                    gate_type: g.gate_type,
                                    location: g.location || '',
                                    description: g.description || '',
                                    status: g.status,
                                    is_active: g.is_active
                                  });
                                  setIsEditGateOpen(true);
                                }}
                                className="p-1.5 bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 rounded-lg"
                                title="Edit Gate"
                              >
                                <Edit className="w-3.5 h-3.5" />
                              </button>

                              <button
                                onClick={() => {
                                  setSelectedGate(g);
                                  setIsDeleteGateOpen(true);
                                }}
                                className="p-1.5 bg-rose-500/10 border border-rose-500/20 text-rose-400 hover:bg-rose-500/20 rounded-lg"
                                title="Delete Gate"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="p-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
                <span>Showing page {page} of {totalPages} ({gatesTotal} total gates)</span>
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
          </div>
        )}

        {/* TAB 2: CAMERA ASSIGNMENT */}
        {activeTab === 'cameras' && (
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900/60 rounded-xl p-4 border border-slate-800 backdrop-blur-md">
              <div className="flex items-center gap-3 w-full sm:w-auto">
                <label className="text-xs font-semibold text-slate-300">Filter by Gate:</label>
                <select
                  value={cameraFilterGateId}
                  onChange={(e) => setCameraFilterGateId(e.target.value)}
                  className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                >
                  <option value="">All Factory Gates</option>
                  {gates.map(g => (
                    <option key={g.id} value={g.id}>{g.gate_code} - {g.gate_name}</option>
                  ))}
                </select>
              </div>

              <button
                onClick={() => {
                  setCameraForm({
                    gate_id: cameraFilterGateId || (gates[0]?.id || ''),
                    camera_name: '',
                    camera_position: 'Entry Camera',
                    rtsp_url: '',
                    ip_address: '',
                    camera_status: 'Online',
                    resolution: '1080p',
                    fps: 30,
                    is_active: true
                  });
                  setIsAddCameraOpen(true);
                }}
                className="px-4 py-2 bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-400 hover:to-indigo-500 text-white rounded-xl text-xs font-semibold flex items-center gap-2 shadow-lg shadow-purple-500/20"
              >
                <Plus className="w-4 h-4" /> Assign New Camera
              </button>
            </div>

            {/* Camera Cards Grid */}
            {camerasLoading ? (
              <div className="p-8 text-center text-slate-500">Loading assigned cameras...</div>
            ) : cameras.length === 0 ? (
              <div className="bg-slate-900/60 rounded-xl border border-slate-800 p-12 text-center text-slate-500">
                <Camera className="w-8 h-8 mx-auto mb-2 opacity-50 text-purple-400" />
                No assigned cameras found. Click "Assign New Camera" to register an ANPR RTSP stream.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {cameras.map((c) => {
                  const assignedGate = gates.find(g => g.id === c.gate_id);
                  return (
                    <div key={c.id} className="bg-slate-900/70 rounded-xl border border-slate-800 p-4 space-y-3 backdrop-blur-md">
                      <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
                        <div className="flex items-center gap-2">
                          <Camera className="w-4 h-4 text-purple-400" />
                          <h4 className="text-xs font-bold text-white">{c.camera_name}</h4>
                        </div>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono border ${
                          c.camera_status === 'Online'
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                            : c.camera_status === 'Offline'
                            ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                            : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                        }`}>
                          ● {c.camera_status}
                        </span>
                      </div>

                      <div className="text-xs space-y-1 text-slate-300">
                        <p><span className="text-slate-500">Gate:</span> <span className="font-semibold text-cyan-400">{assignedGate?.gate_code || 'Assigned Gate'}</span> ({assignedGate?.gate_name || 'N/A'})</p>
                        <p><span className="text-slate-500">Position:</span> <span className="text-purple-300 font-mono">{c.camera_position}</span></p>
                        <p><span className="text-slate-500">IP Address:</span> <span className="font-mono text-amber-300">{c.ip_address || 'N/A'}</span></p>
                        <p><span className="text-slate-500">Stream RTSP:</span> <span className="font-mono text-[11px] text-slate-400 truncate block bg-slate-950 p-1.5 rounded border border-slate-800 mt-0.5">{c.rtsp_url}</span></p>
                        <p><span className="text-slate-500">Spec:</span> {c.resolution || '1080p'} @ {c.fps || 30} FPS</p>
                      </div>

                      <div className="pt-2 border-t border-slate-800 flex items-center justify-end gap-2">
                        <button
                          onClick={() => {
                            setSelectedCamera(c);
                            setCameraForm({
                              gate_id: c.gate_id,
                              camera_name: c.camera_name,
                              camera_position: c.camera_position,
                              rtsp_url: c.rtsp_url,
                              ip_address: c.ip_address || '',
                              camera_status: c.camera_status,
                              resolution: c.resolution || '1080p',
                              fps: c.fps || 30,
                              is_active: c.is_active
                            });
                            setIsEditCameraOpen(true);
                          }}
                          className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => {
                            setSelectedCamera(c);
                            setIsDeleteCameraOpen(true);
                          }}
                          className="px-2.5 py-1 bg-rose-500/10 border border-rose-500/30 text-rose-400 hover:bg-rose-500/20 rounded-lg text-xs font-semibold"
                        >
                          Remove
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* TAB 3: GATE RULES CONFIGURATION */}
        {activeTab === 'rules' && (
          <div className="space-y-6 max-w-4xl">
            <div className="bg-slate-900/60 rounded-xl p-4 border border-slate-800 flex items-center gap-4 backdrop-blur-md">
              <label className="text-xs font-semibold text-slate-300">Select Gate to Configure Rules:</label>
              <select
                value={rulesGateId}
                onChange={(e) => setRulesGateId(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
              >
                {gates.map(g => (
                  <option key={g.id} value={g.id}>{g.gate_code} - {g.gate_name}</option>
                ))}
              </select>
            </div>

            {rulesLoading ? (
              <div className="p-8 text-center text-slate-500">Loading gate rules...</div>
            ) : (
              <form onSubmit={handleSaveRules} className="bg-slate-900/60 rounded-xl border border-slate-800 p-6 space-y-6 backdrop-blur-md">
                <div className="border-b border-slate-800 pb-3">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                    <Sliders className="w-4 h-4 text-cyan-400" /> Operational & Security Gate Rules
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">Configure entry/exit permissions, allowed vehicle types, physical vehicle dimensions, and operating hours.</p>
                </div>

                {/* Toggles */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-white">Allow Entry</span>
                      <input
                        type="checkbox"
                        checked={ruleForm.allow_entry}
                        onChange={(e) => setRuleForm({ ...ruleForm, allow_entry: e.target.checked })}
                        className="w-4 h-4 accent-cyan-500 rounded"
                      />
                    </div>
                    <p className="text-[11px] text-slate-400">Permit inbound vehicles at this gate</p>
                  </div>

                  <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-white">Allow Exit</span>
                      <input
                        type="checkbox"
                        checked={ruleForm.allow_exit}
                        onChange={(e) => setRuleForm({ ...ruleForm, allow_exit: e.target.checked })}
                        className="w-4 h-4 accent-cyan-500 rounded"
                      />
                    </div>
                    <p className="text-[11px] text-slate-400">Permit outbound vehicles at this gate</p>
                  </div>

                  <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-emerald-400">Authorized Vehicles Only</span>
                      <input
                        type="checkbox"
                        checked={ruleForm.authorized_only}
                        onChange={(e) => setRuleForm({ ...ruleForm, authorized_only: e.target.checked })}
                        className="w-4 h-4 accent-emerald-500 rounded"
                      />
                    </div>
                    <p className="text-[11px] text-slate-400">Require scheduled trip / master authorization</p>
                  </div>
                </div>

                {/* Allowed Vehicle Types */}
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-300">Allowed Vehicle Categories:</label>
                  <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                    {[
                      { key: 'allow_trucks', label: 'Trucks / Heavy' },
                      { key: 'allow_buses', label: 'Buses' },
                      { key: 'allow_cars', label: 'Cars / SUVs' },
                      { key: 'allow_two_wheelers', label: 'Two Wheelers' },
                    ].map(vType => (
                      <label key={vType.key} className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex items-center justify-between text-xs text-white cursor-pointer hover:border-slate-700">
                        <span>{vType.label}</span>
                        <input
                          type="checkbox"
                          checked={ruleForm[vType.key]}
                          onChange={(e) => setRuleForm({ ...ruleForm, [vType.key]: e.target.checked })}
                          className="w-4 h-4 accent-cyan-500 rounded"
                        />
                      </label>
                    ))}
                  </div>
                </div>

                {/* Dimension & Weight Limits */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">Maximum Vehicle Height (Meters):</label>
                    <input
                      type="number"
                      step="0.1"
                      value={ruleForm.maximum_vehicle_height}
                      onChange={(e) => setRuleForm({ ...ruleForm, maximum_vehicle_height: parseFloat(e.target.value) || 0 })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">Maximum Vehicle Weight (Tons):</label>
                    <input
                      type="number"
                      step="0.5"
                      value={ruleForm.maximum_vehicle_weight}
                      onChange={(e) => setRuleForm({ ...ruleForm, maximum_vehicle_weight: parseFloat(e.target.value) || 0 })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>

                {/* Working Hours */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">Working Hours Start (HH:MM):</label>
                    <input
                      type="text"
                      placeholder="06:00"
                      value={ruleForm.working_hours_start}
                      onChange={(e) => setRuleForm({ ...ruleForm, working_hours_start: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-cyan-500"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">Working Hours End (HH:MM):</label>
                    <input
                      type="text"
                      placeholder="22:00"
                      value={ruleForm.working_hours_end}
                      onChange={(e) => setRuleForm({ ...ruleForm, working_hours_end: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>

                {/* Remarks */}
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Special Operating Instructions & Remarks:</label>
                  <textarea
                    rows="3"
                    value={ruleForm.remarks}
                    onChange={(e) => setRuleForm({ ...ruleForm, remarks: e.target.value })}
                    placeholder="Enter security notes, access restrictions, or gate procedure guidelines..."
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                  />
                </div>

                <div className="pt-2 flex justify-end">
                  <button
                    type="submit"
                    className="px-6 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-xl text-xs font-bold shadow-lg shadow-cyan-500/20"
                  >
                    Save Gate Rules Configuration
                  </button>
                </div>
              </form>
            )}
          </div>
        )}
      </main>

      {/* MODAL: ADD GATE */}
      <Modal isOpen={isAddGateOpen} onClose={() => setIsAddGateOpen(false)} title="Add New Factory Gate">
        <form onSubmit={handleCreateGate} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Gate Code *</label>
            <input
              type="text"
              required
              placeholder="e.g. GATE-NORTH-01"
              value={gateForm.gate_code}
              onChange={(e) => setGateForm({ ...gateForm, gate_code: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white font-mono uppercase focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Gate Name *</label>
            <input
              type="text"
              required
              placeholder="e.g. Main Factory North Gate"
              value={gateForm.gate_name}
              onChange={(e) => setGateForm({ ...gateForm, gate_name: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Gate Type *</label>
            <select
              value={gateForm.gate_type}
              onChange={(e) => setGateForm({ ...gateForm, gate_type: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
            >
              <option value="Entry & Exit">Entry & Exit</option>
              <option value="Entry">Entry Only</option>
              <option value="Exit">Exit Only</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Location Description</label>
            <input
              type="text"
              placeholder="e.g. North Perimeter - Highway Access"
              value={gateForm.location}
              onChange={(e) => setGateForm({ ...gateForm, location: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Description / Notes</label>
            <textarea
              rows="2"
              placeholder="Primary heavy vehicle entry/exit gate..."
              value={gateForm.description}
              onChange={(e) => setGateForm({ ...gateForm, description: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="flex items-center gap-3 pt-2">
            <button
              type="button"
              onClick={() => setIsAddGateOpen(false)}
              className="flex-1 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-2 bg-cyan-500 hover:bg-cyan-400 text-white text-xs font-bold rounded-xl shadow-lg shadow-cyan-500/20"
            >
              Create Gate
            </button>
          </div>
        </form>
      </Modal>

      {/* MODAL: EDIT GATE */}
      <Modal isOpen={isEditGateOpen} onClose={() => setIsEditGateOpen(false)} title="Edit Factory Gate">
        <form onSubmit={handleUpdateGate} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Gate Code</label>
            <input
              type="text"
              required
              value={gateForm.gate_code}
              onChange={(e) => setGateForm({ ...gateForm, gate_code: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white font-mono uppercase focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Gate Name</label>
            <input
              type="text"
              required
              value={gateForm.gate_name}
              onChange={(e) => setGateForm({ ...gateForm, gate_name: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Gate Type</label>
            <select
              value={gateForm.gate_type}
              onChange={(e) => setGateForm({ ...gateForm, gate_type: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
            >
              <option value="Entry & Exit">Entry & Exit</option>
              <option value="Entry">Entry Only</option>
              <option value="Exit">Exit Only</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Status</label>
            <select
              value={gateForm.status}
              onChange={(e) => setGateForm({ ...gateForm, status: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
            >
              <option value="ACTIVE">ACTIVE</option>
              <option value="INACTIVE">INACTIVE</option>
            </select>
          </div>

          <div className="flex items-center gap-3 pt-2">
            <button
              type="button"
              onClick={() => setIsEditGateOpen(false)}
              className="flex-1 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-2 bg-cyan-500 hover:bg-cyan-400 text-white text-xs font-bold rounded-xl shadow-lg shadow-cyan-500/20"
            >
              Save Changes
            </button>
          </div>
        </form>
      </Modal>

      {/* MODAL: DELETE GATE */}
      <Modal isOpen={isDeleteGateOpen} onClose={() => setIsDeleteGateOpen(false)} title="Delete Factory Gate">
        <div className="space-y-4">
          <p className="text-xs text-slate-300">
            Are you sure you want to delete gate <span className="font-mono font-bold text-rose-400">{selectedGate?.gate_code}</span> ({selectedGate?.gate_name})?
          </p>
          <p className="text-[11px] text-slate-400 italic bg-rose-500/10 border border-rose-500/20 p-2.5 rounded-lg">
            Warning: This action will also delete all assigned cameras and operational rules associated with this gate.
          </p>
          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={() => setIsDeleteGateOpen(false)}
              className="flex-1 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl"
            >
              Cancel
            </button>
            <button
              onClick={handleDeleteGate}
              className="flex-1 py-2 bg-rose-500 hover:bg-rose-600 text-white text-xs font-bold rounded-xl shadow-lg shadow-rose-500/20"
            >
              Confirm Delete
            </button>
          </div>
        </div>
      </Modal>

      {/* MODAL: ASSIGN CAMERA */}
      <Modal isOpen={isAddCameraOpen} onClose={() => setIsAddCameraOpen(false)} title="Assign New ANPR Camera">
        <form onSubmit={handleCreateCamera} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Assign to Gate *</label>
            <select
              required
              value={cameraForm.gate_id}
              onChange={(e) => setCameraForm({ ...cameraForm, gate_id: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-500"
            >
              <option value="">-- Select Gate --</option>
              {gates.map(g => (
                <option key={g.id} value={g.id}>{g.gate_code} - {g.gate_name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Camera Name *</label>
            <input
              type="text"
              required
              placeholder="e.g. ANPR Cam North Front"
              value={cameraForm.camera_name}
              onChange={(e) => setCameraForm({ ...cameraForm, camera_name: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-500"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Camera Position *</label>
            <select
              value={cameraForm.camera_position}
              onChange={(e) => setCameraForm({ ...cameraForm, camera_position: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-500"
            >
              <option value="Entry Camera">Entry Camera</option>
              <option value="Exit Camera">Exit Camera</option>
              <option value="Top View">Top View</option>
              <option value="Side View">Side View</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">RTSP Stream URL *</label>
            <input
              type="text"
              required
              placeholder="rtsp://192.168.1.101:554/stream1"
              value={cameraForm.rtsp_url}
              onChange={(e) => setCameraForm({ ...cameraForm, rtsp_url: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-purple-500"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">IP Address</label>
            <input
              type="text"
              placeholder="192.168.1.101"
              value={cameraForm.ip_address}
              onChange={(e) => setCameraForm({ ...cameraForm, ip_address: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-purple-500"
            />
          </div>

          <div className="flex items-center gap-3 pt-2">
            <button
              type="button"
              onClick={() => setIsAddCameraOpen(false)}
              className="flex-1 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-2 bg-purple-500 hover:bg-purple-400 text-white text-xs font-bold rounded-xl shadow-lg shadow-purple-500/20"
            >
              Assign Camera
            </button>
          </div>
        </form>
      </Modal>

      {/* MODAL: EDIT CAMERA */}
      <Modal isOpen={isEditCameraOpen} onClose={() => setIsEditCameraOpen(false)} title="Edit Camera Settings">
        <form onSubmit={handleUpdateCamera} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Camera Name</label>
            <input
              type="text"
              required
              value={cameraForm.camera_name}
              onChange={(e) => setCameraForm({ ...cameraForm, camera_name: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-500"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">RTSP Stream URL</label>
            <input
              type="text"
              required
              value={cameraForm.rtsp_url}
              onChange={(e) => setCameraForm({ ...cameraForm, rtsp_url: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-purple-500"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Camera Status</label>
            <select
              value={cameraForm.camera_status}
              onChange={(e) => setCameraForm({ ...cameraForm, camera_status: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-500"
            >
              <option value="Online">Online</option>
              <option value="Offline">Offline</option>
              <option value="Maintenance">Maintenance</option>
            </select>
          </div>

          <div className="flex items-center gap-3 pt-2">
            <button
              type="button"
              onClick={() => setIsEditCameraOpen(false)}
              className="flex-1 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-2 bg-purple-500 hover:bg-purple-400 text-white text-xs font-bold rounded-xl shadow-lg shadow-purple-500/20"
            >
              Save Changes
            </button>
          </div>
        </form>
      </Modal>

      {/* MODAL: DELETE CAMERA */}
      <Modal isOpen={isDeleteCameraOpen} onClose={() => setIsDeleteCameraOpen(false)} title="Remove Assigned Camera">
        <div className="space-y-4">
          <p className="text-xs text-slate-300">
            Are you sure you want to remove camera <span className="font-semibold text-purple-400">{selectedCamera?.camera_name}</span>?
          </p>
          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={() => setIsDeleteCameraOpen(false)}
              className="flex-1 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl"
            >
              Cancel
            </button>
            <button
              onClick={handleDeleteCamera}
              className="flex-1 py-2 bg-rose-500 hover:bg-rose-600 text-white text-xs font-bold rounded-xl shadow-lg shadow-rose-500/20"
            >
              Confirm Remove
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
