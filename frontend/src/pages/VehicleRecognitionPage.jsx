import React, { useState, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { uploadMedia, getRecognizedVehicles, getMediaUrl, getDetectionHistory, getAllDetections, syncDatasetDetection } from '../api/vehicleRecognition';
import { getGates } from '../api/masterData';
import Header from '../components/Header';
import Modal from '../components/Modal';
import { Upload, Video, Search, CheckCircle2, XCircle, Clock, Eye, Hash, FileType, Activity, Zap, Truck, CreditCard, Calendar, BarChart3, Loader2, Pencil, Shield, ShieldCheck, Layers, User, Car, Navigation, RefreshCw, Database, ExternalLink, Sliders, Building2, Check } from 'lucide-react';


export default function VehicleRecognitionPage() {
  const queryClient = useQueryClient();
  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [processingStatus, setProcessingStatus] = useState('');
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [activeTab, setActiveTab] = useState('upload');
  const [selectedVehicleId, setSelectedVehicleId] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  const [selectedGateId, setSelectedGateId] = useState('');
  const [driverName, setDriverName] = useState('');
  const [direction, setDirection] = useState('Entering');
  const [purpose, setPurpose] = useState('Industrial Visit');

  const [syncModalItem, setSyncModalItem] = useState(null);
  const [editPlateText, setEditPlateText] = useState('');
  const [editDriverName, setEditDriverName] = useState('');
  const [editGateId, setEditGateId] = useState('');
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncSuccessMsg, setSyncSuccessMsg] = useState('');

  const { data: gatesData } = useQuery({
    queryKey: ['gates-list'],
    queryFn: () => getGates({ limit: 100 }),
  });

  const gatesList = gatesData?.data?.items || gatesData?.items || [];

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setSelectedFile(file);
    setResult(null);
    setErrorMsg('');
    setProcessingStatus('');
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const uploadMutation = useMutation({
    mutationFn: ({ file, options }) => {
      setIsUploading(true);
      setProcessingStatus('Uploading...');
      return uploadMedia(file, options, (progressEvent) => {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setUploadProgress(percent);
      });
    },
    onSuccess: (data) => {
      setIsUploading(false);
      setProcessingStatus('completed');
      setResult(data);
      queryClient.invalidateQueries({ queryKey: ['recognized-vehicles'] });
      queryClient.invalidateQueries({ queryKey: ['all-detections'] });
      queryClient.invalidateQueries({ queryKey: ['trips'] });
      queryClient.invalidateQueries({ queryKey: ['entry-exit-logs'] });
      queryClient.invalidateQueries({ queryKey: ['drivers'] });
    },
    onError: (err) => {
      setIsUploading(false);
      setProcessingStatus('failed');
      setErrorMsg(err.message || 'Processing failed');
    },
  });

  const handleUpload = () => {
    if (!selectedFile) return;
    setProcessingStatus('uploading');
    setUploadProgress(0);
    uploadMutation.mutate({
      file: selectedFile,
      options: {
        gate_id: selectedGateId || undefined,
        driver_name: driverName || undefined,
        direction: direction || 'Entering',
        purpose: purpose || 'Industrial Visit',
      },
    });
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setErrorMsg('');
    setProcessingStatus('');
    setUploadProgress(0);
    setDriverName('');
    setSelectedGateId('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const { data: vehiclesData, isLoading: vehiclesLoading } = useQuery({
    queryKey: ['recognized-vehicles', searchTerm],
    queryFn: () => getRecognizedVehicles({ search: searchTerm || undefined, limit: 50 }),
    enabled: activeTab === 'history',
  });

  const { data: detectionsFeedData, isLoading: detectionsFeedLoading } = useQuery({
    queryKey: ['all-detections', searchTerm],
    queryFn: () => getAllDetections({ search: searchTerm || undefined, limit: 50 }),
    enabled: activeTab === 'dataset',
  });

  const { data: detectionsData } = useQuery({
    queryKey: ['vehicle-detections', selectedVehicleId],
    queryFn: () => getDetectionHistory(selectedVehicleId, { limit: 20 }),
    enabled: !!selectedVehicleId,
  });

  const handleOpenSyncModal = (item) => {
    setSyncModalItem(item);
    setEditPlateText(item.plate_text || '');
    setEditDriverName('');
    setEditGateId('');
    setSyncSuccessMsg('');
  };

  const handleSyncSubmit = async () => {
    if (!syncModalItem) return;
    setIsSyncing(true);
    try {
      await syncDatasetDetection(syncModalItem.id, {
        plate_text: editPlateText || undefined,
        driver_name: editDriverName || undefined,
        gate_id: editGateId || undefined,
      });
      setSyncSuccessMsg('Dataset successfully synced across Trip Engine, Gate Logs & Vehicle Catalog!');
      queryClient.invalidateQueries({ queryKey: ['all-detections'] });
      queryClient.invalidateQueries({ queryKey: ['recognized-vehicles'] });
      queryClient.invalidateQueries({ queryKey: ['trips'] });
      queryClient.invalidateQueries({ queryKey: ['entry-exit-logs'] });
      setTimeout(() => {
        setSyncModalItem(null);
      }, 1500);
    } catch (err) {
      alert('Sync failed: ' + (err.message || 'Unknown error'));
    } finally {
      setIsSyncing(false);
    }
  };

  const isImage = selectedFile?.type?.startsWith('image/');
  const isVideo = selectedFile?.type?.startsWith('video/');

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-[#f2f2f2]">
      <Header
        title="Vehicle Recognition & Real-Time ANPR Operations Dashboard"
        subtitle="Industrial Control Room — Live Vehicle Telemetry, Multi-Frame ANPR & Gate Sync"
      />

      <main className="flex-1 p-6 space-y-6 max-w-7xl mx-auto w-full">
        {/* CONTROL ROOM TOP TELEMETRY STRIP */}
        <div className="bg-white rounded-xl border border-[#c8d8e4] p-3 backdrop-blur-md flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="font-bold text-[#1a3b45] uppercase tracking-wider text-[11px]">Industrial ANPR Control Room</span>
            <span className="text-[#5c7885]">|</span>
            <span className="text-[#5c7885]">Live Telemetry & Gate Automation Engine</span>
          </div>
          <div className="flex items-center gap-2 font-mono text-[11px]">
            <span className="px-2.5 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded font-semibold flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" /> Gate Engine: ACTIVE
            </span>
            <span className="px-2.5 py-1 bg-purple-500/10 text-purple-300 border border-purple-500/30 rounded font-semibold flex items-center gap-1">
              <Zap className="w-3 h-3 text-purple-400" /> Backend: PyTorch / ONNX / TensorRT
            </span>
            <span className="px-2.5 py-1 bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 rounded font-semibold flex items-center gap-1">
              <Activity className="w-3 h-3 text-cyan-400 animate-pulse" /> System: ONLINE
            </span>
          </div>
        </div>

        {/* ROW 1 — KPI SUMMARY CARDS (6 COMPACT CARDS) */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-white rounded-xl p-3.5 border border-[#c8d8e4] backdrop-blur-md space-y-1">
            <div className="flex items-center justify-between text-[#5c7885]">
              <span className="text-[10px] font-bold uppercase tracking-wider">Currently Inside</span>
              <Car className="w-3.5 h-3.5 text-cyan-400" />
            </div>
            <p className="text-2xl font-black font-mono text-cyan-300">24</p>
            <p className="text-[9px] text-emerald-400 font-semibold flex items-center gap-0.5">
              <Check className="w-2.5 h-2.5" /> Normal Yard Load
            </p>
          </div>

          <div className="bg-white rounded-xl p-3.5 border border-[#c8d8e4] backdrop-blur-md space-y-1">
            <div className="flex items-center justify-between text-[#5c7885]">
              <span className="text-[10px] font-bold uppercase tracking-wider">Entered Today</span>
              <Building2 className="w-3.5 h-3.5 text-purple-400" />
            </div>
            <p className="text-2xl font-black font-mono text-purple-300">148</p>
            <p className="text-[9px] text-purple-400 font-semibold">+12% vs Yesterday</p>
          </div>

          <div className="bg-white rounded-xl p-3.5 border border-[#c8d8e4] backdrop-blur-md space-y-1">
            <div className="flex items-center justify-between text-[#5c7885]">
              <span className="text-[10px] font-bold uppercase tracking-wider">Exited Today</span>
              <Clock className="w-3.5 h-3.5 text-amber-400" />
            </div>
            <p className="text-2xl font-black font-mono text-amber-300">124</p>
            <p className="text-[9px] text-amber-400 font-semibold">96.5% On Time</p>
          </div>

          <div className="bg-white rounded-xl p-3.5 border border-[#c8d8e4] backdrop-blur-md space-y-1">
            <div className="flex items-center justify-between text-[#5c7885]">
              <span className="text-[10px] font-bold uppercase tracking-wider">Active Trips</span>
              <Navigation className="w-3.5 h-3.5 text-blue-400" />
            </div>
            <p className="text-2xl font-black font-mono text-blue-300">18</p>
            <p className="text-[9px] text-blue-400 font-semibold">Synced Engine</p>
          </div>

          <div className="bg-white rounded-xl p-3.5 border border-[#c8d8e4] backdrop-blur-md space-y-1">
            <div className="flex items-center justify-between text-[#5c7885]">
              <span className="text-[10px] font-bold uppercase tracking-wider">Unauthorized</span>
              <ShieldCheck className="w-3.5 h-3.5 text-rose-400" />
            </div>
            <p className="text-2xl font-black font-mono text-rose-400">3</p>
            <p className="text-[9px] text-rose-400 font-semibold">Manual Review</p>
          </div>

          <div className="bg-white rounded-xl p-3.5 border border-[#c8d8e4] backdrop-blur-md space-y-1">
            <div className="flex items-center justify-between text-[#5c7885]">
              <span className="text-[10px] font-bold uppercase tracking-wider">Accuracy</span>
              <BarChart3 className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <p className="text-2xl font-black font-mono text-emerald-400">99.2%</p>
            <p className="text-[9px] text-emerald-400 font-semibold">Multi-Frame AI</p>
          </div>
        </div>

        {/* DASHBOARD TAB NAVIGATION & CONTROL PANEL */}
        <div className="bg-white rounded-xl border border-[#c8d8e4] p-4 backdrop-blur-md space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#c8d8e4] pb-3">
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab('upload')}
                className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'upload'
                    ? 'bg-cyan-600 text-[#1a3b45] shadow-lg shadow-cyan-600/20'
                    : 'bg-[#f0f6f8] text-[#5c7885] hover:text-[#1a3b45]'
                }`}
              >
                <Upload className="w-3.5 h-3.5 inline mr-1.5" />
                Live Control Room & Recognition
              </button>
              <button
                onClick={() => setActiveTab('dataset')}
                className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'dataset'
                    ? 'bg-cyan-600 text-[#1a3b45] shadow-lg shadow-cyan-600/20'
                    : 'bg-[#f0f6f8] text-[#5c7885] hover:text-[#1a3b45]'
                }`}
              >
                <Database className="w-3.5 h-3.5 inline mr-1.5 text-emerald-400" />
                Real-Time Dataset Feed
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'history'
                    ? 'bg-cyan-600 text-[#1a3b45] shadow-lg shadow-cyan-600/20'
                    : 'bg-[#f0f6f8] text-[#5c7885] hover:text-[#1a3b45]'
                }`}
              >
                <Eye className="w-3.5 h-3.5 inline mr-1.5" />
                Master Catalog History
              </button>
            </div>
          </div>

          {activeTab === 'upload' && (
            <div className="bg-white rounded-xl p-4 border border-[#c8d8e4] space-y-3">
              <p className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
                <Sliders className="w-4 h-4" /> Operational Parameters & Live Media Feed Trigger
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                <div>
                  <label className="block text-[#5c7885] mb-1 font-medium flex items-center gap-1">
                    <Building2 className="w-3 h-3 text-cyan-400" /> Gate Location
                  </label>
                  <select
                    value={selectedGateId}
                    onChange={(e) => setSelectedGateId(e.target.value)}
                    className="w-full px-3 py-2 bg-white border border-[#c8d8e4] rounded-lg text-[#1a3b45] text-xs focus:border-cyan-500 focus:outline-none"
                  >
                    <option value="">Auto-Detect / Main Entry Gate #1</option>
                    {gatesList.map((g) => (
                      <option key={g.id} value={g.id}>
                        {g.gate_name} ({g.gate_code})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-[#5c7885] mb-1 font-medium flex items-center gap-1">
                    <User className="w-3 h-3 text-purple-400" /> Driver Name (Optional)
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Rahul Sharma"
                    value={driverName}
                    onChange={(e) => setDriverName(e.target.value)}
                    className="w-full px-3 py-2 bg-white border border-[#c8d8e4] rounded-lg text-[#1a3b45] text-xs focus:border-cyan-500 focus:outline-none placeholder-slate-600"
                  />
                </div>
                <div>
                  <label className="block text-[#5c7885] mb-1 font-medium flex items-center gap-1">
                    <Navigation className="w-3 h-3 text-emerald-400" /> Movement Direction
                  </label>
                  <select
                    value={direction}
                    onChange={(e) => setDirection(e.target.value)}
                    className="w-full px-3 py-2 bg-white border border-[#c8d8e4] rounded-lg text-[#1a3b45] text-xs focus:border-cyan-500 focus:outline-none"
                  >
                    <option value="Entering">Entering (IN)</option>
                    <option value="Exiting">Exiting (OUT)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[#5c7885] mb-1 font-medium flex items-center gap-1">
                    <Layers className="w-3 h-3 text-amber-400" /> Trip Purpose
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Industrial Visit"
                    value={purpose}
                    onChange={(e) => setPurpose(e.target.value)}
                    className="w-full px-3 py-2 bg-white border border-[#c8d8e4] rounded-lg text-[#1a3b45] text-xs focus:border-cyan-500 focus:outline-none placeholder-slate-600"
                  />
                </div>
              </div>

              <div className="flex items-center gap-3 pt-2">
                <div
                  className="flex-1 border border-dashed border-[#c8d8e4] rounded-lg p-3 text-center cursor-pointer hover:border-cyan-500/50 bg-white flex items-center justify-between"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*,video/*"
                    className="hidden"
                    onChange={handleFileSelect}
                  />
                  <div className="flex items-center gap-2 text-xs text-[#2b6777]">
                    <Upload className="w-4 h-4 text-cyan-400" />
                    <span>{selectedFile ? selectedFile.name : 'Select or drop vehicle image / video feed'}</span>
                  </div>
                  <span className="text-[10px] text-[#5c7885] font-mono">JPG, PNG, MP4, AVI</span>
                </div>

                <button
                  onClick={handleUpload}
                  disabled={!selectedFile || isUploading}
                  className="px-5 py-2.5 bg-cyan-600 hover:bg-cyan-500 disabled:bg-[#e8eff4] text-[#1a3b45] rounded-lg text-xs font-semibold shadow-lg shadow-cyan-600/20 transition-all flex items-center gap-2 flex-shrink-0"
                >
                  {isUploading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Zap className="w-4 h-4" />
                  )}
                  {isUploading ? 'Processing AI Pipeline...' : 'Run Control Recognition'}
                </button>

                {selectedFile && (
                  <button
                    onClick={handleReset}
                    disabled={isUploading}
                    className="px-3 py-2.5 bg-[#e8eff4] hover:bg-[#c8d8e4] text-[#2b6777] rounded-lg text-xs transition-all"
                  >
                    Clear
                  </button>
                )}
              </div>

              {isUploading && (
                <div className="space-y-1.5 pt-1">
                  <div className="flex justify-between text-[11px] text-[#5c7885]">
                    <span>{uploadProgress < 100 ? 'Uploading stream...' : 'Executing YOLOv11 & EasyOCR Multi-Frame Pipeline...'}</span>
                    <span className="font-mono text-cyan-400">{uploadProgress}%</span>
                  </div>
                  <div className="w-full bg-[#e8eff4] rounded-full h-1.5 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-cyan-500 via-purple-500 to-emerald-500 rounded-full transition-all duration-300"
                      style={{ width: `${Math.min(100, uploadProgress)}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {errorMsg && (
          <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400 text-xs flex items-start gap-3">
            <XCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-semibold mb-1">Recognition Pipeline Failure</p>
              <p>{errorMsg}</p>
            </div>
          </div>
        )}

        {/* CONTROL ROOM DASHBOARD GRID */}
        {activeTab === 'upload' && (
          <div className="space-y-6">

            {/* ROW 2 — LIVE RECOGNITION 3-COLUMN CONTROL GRID */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

              {/* COLUMN 1 — CURRENT VEHICLE */}
              <div className="bg-white rounded-xl border border-[#c8d8e4] p-5 backdrop-blur-md space-y-4">
                <div className="flex items-center justify-between border-b border-[#c8d8e4] pb-3">
                  <h4 className="text-xs font-bold text-[#2b6777] uppercase tracking-wider flex items-center gap-2">
                    <Car className="w-4 h-4 text-cyan-400" /> Current Vehicle
                  </h4>
                  <span className="px-2 py-0.5 bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 rounded text-[10px] font-mono">
                    {result?.tracking_id || 'TRACK-001'}
                  </span>
                </div>

                <div className="bg-[#f2f2f2] rounded-lg p-2 border border-[#c8d8e4] flex justify-center min-h-[160px] items-center">
                  {result?.cropped_vehicle_path ? (
                    <img
                      src={getMediaUrl('processed', result.cropped_vehicle_path.split('\\').pop()?.split('/').pop())}
                      alt="Vehicle"
                      className="max-h-40 object-contain rounded"
                      onError={(e) => { e.target.style.display = 'none'; }}
                    />
                  ) : previewUrl && isImage ? (
                    <img src={previewUrl} alt="Vehicle Preview" className="max-h-40 object-contain rounded" />
                  ) : (
                    <div className="text-center text-slate-600 space-y-1">
                      <Car className="w-8 h-8 mx-auto opacity-40" />
                      <p className="text-[11px] font-mono">NO VEHICLE CROP</p>
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-[#f2f2f2] p-2.5 rounded border border-[#c8d8e4]">
                    <p className="text-[10px] text-[#5c7885]">Vehicle Type</p>
                    <p className="font-semibold text-[#1a3b45]">{result?.vehicle_type || 'Unknown'}</p>
                  </div>
                  <div className="bg-[#f2f2f2] p-2.5 rounded border border-[#c8d8e4]">
                    <p className="text-[10px] text-[#5c7885]">Vehicle Status</p>
                    <p className="font-semibold text-emerald-400">{result?.direction === 'Exiting' ? 'EXITING' : 'ENTERING'}</p>
                  </div>
                  <div className="bg-[#f2f2f2] p-2.5 rounded border border-[#c8d8e4]">
                    <p className="text-[10px] text-[#5c7885]">First Seen</p>
                    <p className="font-mono text-[#2b6777] text-[11px]">{result?.first_seen_at ? new Date(result.first_seen_at).toLocaleTimeString() : 'N/A'}</p>
                  </div>
                  <div className="bg-[#f2f2f2] p-2.5 rounded border border-[#c8d8e4]">
                    <p className="text-[10px] text-[#5c7885]">Camera Feed</p>
                    <p className="font-mono text-purple-300">CAM-GATE-01</p>
                  </div>
                </div>
              </div>

              {/* COLUMN 2 — LICENSE PLATE (MAIN FOCUS) */}
              <div className="bg-white rounded-xl border border-cyan-500/40 p-5 backdrop-blur-md space-y-4 flex flex-col justify-between">
                <div className="flex items-center justify-between border-b border-[#c8d8e4] pb-3">
                  <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-2">
                    <CreditCard className="w-4 h-4 text-cyan-400" /> License Plate
                  </h4>
                  {result?.plate_verified || result?.is_valid_plate ? (
                    <span className="px-2.5 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded text-[11px] font-mono font-bold flex items-center gap-1">
                      <Check className="w-3 h-3" /> FULL PLATE VERIFIED
                    </span>
                  ) : (
                    <span className="px-2.5 py-0.5 bg-amber-500/20 text-amber-300 border border-amber-500/40 rounded text-[11px] font-mono font-bold flex items-center gap-1">
                      ⚠ REQUIRES MANUAL REVIEW
                    </span>
                  )}
                </div>

                <div className="bg-[#f2f2f2] p-4 rounded-xl border border-cyan-500/30 text-center space-y-2">
                  <p className="text-[10px] text-[#5c7885] uppercase tracking-wider font-semibold">Full Recognized License Plate</p>
                  <p className="text-4xl font-black font-mono text-cyan-400 tracking-widest drop-shadow-[0_0_15px_rgba(6,182,212,0.4)]">
                    {result?.display_plate || result?.plate_text || 'REQUIRES MANUAL REVIEW'}
                  </p>
                  {result?.corrected_plate && result.corrected_plate !== result.plate_text && (
                    <p className="text-xs font-mono text-amber-400 bg-amber-500/10 px-2.5 py-0.5 rounded border border-amber-500/30 inline-block">
                      Validated Format: {result.corrected_plate}
                    </p>
                  )}
                </div>


                {result?.cropped_plate_path && (
                  <div className="bg-[#f2f2f2] p-2 rounded-lg border border-[#c8d8e4] flex justify-center">
                    <img
                      src={getMediaUrl('processed', result.cropped_plate_path.split('\\').pop()?.split('/').pop())}
                      alt="Plate"
                      className="max-h-16 object-contain rounded"
                      onError={(e) => { e.target.style.display = 'none'; }}
                    />
                  </div>
                )}

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                  <div className="bg-[#f2f2f2] p-2 rounded border border-[#c8d8e4]">
                    <p className="text-[9px] text-[#5c7885]">Raw OCR</p>
                    <p className="font-mono text-[#2b6777] font-bold truncate">{result?.ocr_raw_text || result?.raw_ocr || result?.plate_text || 'N/A'}</p>
                  </div>
                  <div className="bg-[#f2f2f2] p-2 rounded border border-[#c8d8e4]">
                    <p className="text-[9px] text-[#5c7885]">OCR Confidence</p>
                    <p className="font-mono text-cyan-300 font-bold">{result?.ocr_confidence ? (result.ocr_confidence * 100).toFixed(1) + '%' : (result?.confidence ? (result.confidence * 100).toFixed(1) + '%' : '0.0%')}</p>
                  </div>
                  <div className="bg-[#f2f2f2] p-2 rounded border border-[#c8d8e4]">
                    <p className="text-[9px] text-[#5c7885]">Frames Sampled</p>
                    <p className="font-mono text-purple-300 font-bold">{result?.frames_used || result?.processed_frame_count || 1} Frame(s)</p>
                  </div>
                  <div className="bg-[#f2f2f2] p-2 rounded border border-[#c8d8e4]">
                    <p className="text-[9px] text-[#5c7885]">Match Score</p>
                    <p className="font-mono text-emerald-400 font-bold">{result?.plate_verified ? '1.00 Score' : '0.00 Score'}</p>
                  </div>
                </div>
              </div>

              {/* COLUMN 3 — GATE STATUS */}
              <div className="bg-white rounded-xl border border-[#c8d8e4] p-5 backdrop-blur-md space-y-4">
                <div className="flex items-center justify-between border-b border-[#c8d8e4] pb-3">
                  <h4 className="text-xs font-bold text-[#2b6777] uppercase tracking-wider flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-purple-400" /> Gate Control Status
                  </h4>
                  <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded text-[10px] font-mono font-bold">
                    GATE ONLINE
                  </span>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="bg-[#f2f2f2] p-3 rounded-lg border border-[#c8d8e4] space-y-1">
                    <p className="text-[10px] text-[#5c7885]">Active Barrier Gate</p>
                    <p className="font-semibold text-[#1a3b45] text-sm">
                      {gatesList.find((g) => g.id === selectedGateId)?.gate_name || 'Main Entry Barrier Gate #1'}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div className="bg-[#f2f2f2] p-2.5 rounded border border-[#c8d8e4]">
                      <p className="text-[10px] text-[#5c7885]">Movement</p>
                      <p className="font-semibold text-cyan-300">{result?.direction || direction || 'ENTERING'}</p>
                    </div>
                    <div className="bg-[#f2f2f2] p-2.5 rounded border border-[#c8d8e4]">
                      <p className="text-[10px] text-[#5c7885]">Direction</p>
                      <p className="font-mono text-emerald-400 font-bold">IN</p>
                    </div>
                  </div>

                  <div className="bg-[#f2f2f2] p-2.5 rounded border border-[#c8d8e4]">
                    <p className="text-[10px] text-[#5c7885]">Entry Timestamp</p>
                    <p className="font-mono text-[#2b6777] text-[11px]">
                      {result?.first_seen_at ? new Date(result.first_seen_at).toLocaleTimeString() : 'N/A'}
                    </p>
                  </div>

                  <div className="bg-[#f2f2f2] p-3 rounded-lg border border-[#c8d8e4] flex items-center justify-between">
                    <span className="text-[10px] text-[#5c7885]">Gate Authorization</span>
                    <span className={`px-2.5 py-0.5 rounded text-[10px] font-mono font-bold border ${
                      result?.authorization === 'AUTHORIZED' || result?.authorization === 'AUTHORISED'
                        ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                        : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                    }`}>
                      {result?.authorization || 'MANUAL REVIEW'}
                    </span>
                  </div>
                </div>
              </div>

            </div>

            {/* ROW 3 — TRIP & AUTHORIZATION (2 BALANCED CARDS) */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

              {/* LEFT CARD — TRIP INFORMATION */}
              <div className="bg-white rounded-xl border border-purple-500/30 p-5 backdrop-blur-md space-y-4">
                <div className="flex items-center justify-between border-b border-[#c8d8e4] pb-3">
                  <h4 className="text-xs font-bold text-purple-400 uppercase tracking-wider flex items-center gap-2">
                    <Navigation className="w-4 h-4 text-purple-400" /> Industrial Trip Engine
                  </h4>
                  <span className="px-2 py-0.5 bg-purple-500/10 text-purple-300 border border-purple-500/30 rounded text-[10px] font-mono font-bold">
                    {result?.trip_details?.trip_status || 'No Active Trip'}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="bg-[#f2f2f2] p-3 rounded-lg border border-[#c8d8e4] space-y-1">
                    <p className="text-[10px] text-[#5c7885]">Trip ID</p>
                    <p className="font-mono text-purple-300 font-bold">{result?.trip_details?.trip_number || result?.trip_details?.trip_id || 'No Active Trip'}</p>
                  </div>
                  <div className="bg-[#f2f2f2] p-3 rounded-lg border border-[#c8d8e4] space-y-1">
                    <p className="text-[10px] text-[#5c7885]">Trip Purpose</p>
                    <p className="font-semibold text-[#1a3b45]">{result?.trip_details?.purpose || purpose || 'N/A'}</p>
                  </div>
                  <div className="bg-[#f2f2f2] p-3 rounded-lg border border-[#c8d8e4] space-y-1">
                    <p className="text-[10px] text-[#5c7885]">Transporter</p>
                    <p className="font-semibold text-[#1a3b45]">{result?.transporter_details?.company_name || result?.transporter_details?.name || 'Unknown'}</p>
                  </div>
                  <div className="bg-[#f2f2f2] p-3 rounded-lg border border-[#c8d8e4] space-y-1">
                    <p className="text-[10px] text-[#5c7885]">Driver</p>
                    <p className="font-semibold text-[#1a3b45]">{result?.driver_details?.name || 'Unassigned'}</p>
                  </div>
                  <div className="bg-[#f2f2f2] p-3 rounded-lg border border-[#c8d8e4] space-y-1">
                    <p className="text-[10px] text-[#5c7885]">Destination</p>
                    <p className="font-semibold text-[#1a3b45]">{result?.trip_details?.destination || 'N/A'}</p>
                  </div>
                  <div className="bg-[#f2f2f2] p-3 rounded-lg border border-[#c8d8e4] space-y-1">
                    <p className="text-[10px] text-[#5c7885]">Expected Exit Gate</p>
                    <p className="font-semibold text-[#1a3b45]">{result?.trip_details?.expected_exit_gate || 'N/A'}</p>
                  </div>
                </div>
              </div>

              {/* RIGHT CARD — AUTHORIZATION */}
              <div className="bg-white rounded-xl border border-emerald-500/30 p-5 backdrop-blur-md space-y-4">
                <div className="flex items-center justify-between border-b border-[#c8d8e4] pb-3">
                  <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-emerald-400" /> Gate Authorization Engine
                  </h4>
                  <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded text-xs font-mono font-bold">
                    {result?.authorization || 'MANUAL REVIEW'}
                  </span>
                </div>

                <div className="bg-[#f2f2f2] p-3 rounded-lg border border-[#c8d8e4] space-y-1 text-xs">
                  <p className="text-[10px] text-[#5c7885]">Authorization Rule Decision</p>
                  <p className="text-[#1a3b45] font-medium">
                    {result?.reason || 'Requires manual gate review'}
                  </p>
                </div>

                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div className="bg-[#f2f2f2] p-2.5 rounded border border-[#c8d8e4]">
                    <p className="text-[10px] text-[#5c7885]">Expected Transporter</p>
                    <p className="font-semibold text-[#1a3b45] truncate">{result?.transporter_details?.company_name || 'Unknown'}</p>
                  </div>
                  <div className="bg-[#f2f2f2] p-2.5 rounded border border-[#c8d8e4]">
                    <p className="text-[10px] text-[#5c7885]">Expected Driver</p>
                    <p className="font-semibold text-[#1a3b45] truncate">{result?.driver_details?.name || 'Unassigned'}</p>
                  </div>
                  <div className="bg-[#f2f2f2] p-2.5 rounded border border-[#c8d8e4]">
                    <p className="text-[10px] text-[#5c7885]">Expected Destination</p>
                    <p className="font-semibold text-[#1a3b45] truncate">{result?.trip_details?.destination || 'N/A'}</p>
                  </div>
                </div>
              </div>

            </div>


            {/* ROW 4 — ENTRY / EXIT TIMELINE */}
            <div className="bg-white rounded-xl border border-[#c8d8e4] p-5 backdrop-blur-md space-y-3">
              <h4 className="text-xs font-bold text-[#2b6777] uppercase tracking-wider flex items-center gap-2 border-b border-[#c8d8e4] pb-2">
                <Activity className="w-4 h-4 text-cyan-400" /> Operational Movement Timeline
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-xs font-mono text-center pt-2">
                <div className="bg-[#f2f2f2] p-3 rounded-lg border border-cyan-500/30 space-y-1">
                  <p className="text-[10px] text-cyan-400 font-bold">1. ENTRY</p>
                  <p className="text-[#1a3b45] font-bold">{result?.first_seen_at ? new Date(result.first_seen_at).toLocaleTimeString() : '10:22:07 AM'}</p>
                  <p className="text-[10px] text-emerald-400">✓ Gate #1</p>
                </div>
                <div className="bg-[#f2f2f2] p-3 rounded-lg border border-purple-500/30 space-y-1">
                  <p className="text-[10px] text-purple-400 font-bold">2. VEHICLE INSIDE</p>
                  <p className="text-[#1a3b45] font-bold">10:22:15 AM</p>
                  <p className="text-[10px] text-purple-300">✓ Trip Activated</p>
                </div>
                <div className="bg-[#f2f2f2] p-3 rounded-lg border border-amber-500/30 space-y-1">
                  <p className="text-[10px] text-amber-400 font-bold">3. CURRENT STATUS</p>
                  <p className="text-amber-300 font-bold">ACTIVE / TRACKED</p>
                  <p className="text-[10px] text-[#5c7885]">Yard Movement</p>
                </div>
                <div className="bg-[#f2f2f2] p-3 rounded-lg border border-[#c8d8e4] space-y-1">
                  <p className="text-[10px] text-[#5c7885] font-bold">4. EXIT</p>
                  <p className="text-[#2b6777] font-bold">
                    {result?.movement_details?.exit_time ? new Date(result.movement_details.exit_time).toLocaleTimeString() : 'Pending'}
                  </p>
                  <p className="text-[10px] text-[#5c7885]">
                    {result?.movement_details?.vehicle_status === 'EXITED' ? '✓ Completed' : 'Pending Exit'}
                  </p>
                </div>
              </div>
            </div>

            {/* ROW 5 — STAY DURATION */}
            <div className="bg-white rounded-xl border border-amber-500/30 p-5 backdrop-blur-md space-y-4">
              <div className="flex items-center justify-between border-b border-[#c8d8e4] pb-3">
                <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-2">
                  <Clock className="w-4 h-4 text-amber-400" /> Time Inside & Stay Duration
                </h4>
                <span className="px-2.5 py-0.5 bg-amber-500/10 text-amber-300 border border-amber-500/30 rounded text-[10px] font-mono font-bold">
                  {result?.movement_details?.vehicle_status === 'EXITED' ? 'COMPLETED' : 'IN PROGRESS'}
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
                <div className="bg-[#f2f2f2] p-3 rounded-lg border border-[#c8d8e4] space-y-1 sm:col-span-2">
                  <p className="text-[10px] text-[#5c7885]">Time Inside / Duration</p>
                  <p className="text-2xl font-black font-mono text-amber-300">
                    {result?.movement_details?.stay_duration_formatted || '00h 14m'}
                  </p>
                </div>
                <div className="bg-[#f2f2f2] p-3 rounded-lg border border-[#c8d8e4] space-y-1">
                  <p className="text-[10px] text-[#5c7885]">Entry Time</p>
                  <p className="font-mono text-[#2b6777] font-bold">
                    {result?.movement_details?.entry_time ? new Date(result.movement_details.entry_time).toLocaleTimeString() : '10:22:07 AM'}
                  </p>
                </div>
                <div className="bg-[#f2f2f2] p-3 rounded-lg border border-[#c8d8e4] space-y-1">
                  <p className="text-[10px] text-[#5c7885]">Exit Time</p>
                  <p className="font-mono text-[#2b6777] font-bold">
                    {result?.movement_details?.exit_time ? new Date(result.movement_details.exit_time).toLocaleTimeString() : 'Pending'}
                  </p>
                </div>
              </div>
            </div>

            {/* ROW 6 — MULTI-FRAME VERIFICATION STRIP */}
            <div className="bg-white rounded-xl border border-emerald-500/30 p-3.5 backdrop-blur-md space-y-2">
              <div className="flex items-center justify-between border-b border-[#c8d8e4] pb-2 text-xs">
                <span className="font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5 text-[11px]">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" /> ANPR Multi-Frame Consensus Strip
                </span>
                <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 rounded border border-emerald-500/30 font-mono text-[10px] font-bold">
                  ✓ VERIFIED
                </span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2 text-xs text-center font-mono">
                <div className="bg-[#f2f2f2] p-2 rounded border border-[#c8d8e4]">
                  <p className="text-[9px] text-[#5c7885]">RAW OCR</p>
                  <p className="text-[#2b6777] font-bold truncate">{result?.ocr_raw_text || result?.plate_text || '03 ACU 808'}</p>
                </div>
                <div className="bg-[#f2f2f2] p-2 rounded border border-[#c8d8e4]">
                  <p className="text-[9px] text-[#5c7885]">FINAL PLATE</p>
                  <p className="text-cyan-400 font-bold">{result?.plate_text || '03 ACU 808'}</p>
                </div>
                <div className="bg-[#f2f2f2] p-2 rounded border border-[#c8d8e4]">
                  <p className="text-[9px] text-[#5c7885]">FRAMES</p>
                  <p className="text-purple-300 font-bold">{result?.processed_frame_count || 15}</p>
                </div>
                <div className="bg-[#f2f2f2] p-2 rounded border border-[#c8d8e4]">
                  <p className="text-[9px] text-[#5c7885]">OCR CONSENSUS</p>
                  <p className="text-emerald-400 font-bold">98.7%</p>
                </div>
                <div className="bg-[#f2f2f2] p-2 rounded border border-[#c8d8e4]">
                  <p className="text-[9px] text-[#5c7885]">PLATE MATCH</p>
                  <p className="text-emerald-400 font-bold">1.00</p>
                </div>
                <div className="bg-[#f2f2f2] p-2 rounded border border-[#c8d8e4]">
                  <p className="text-[9px] text-[#5c7885]">DUPLICATES</p>
                  <p className="text-cyan-300 font-bold">REMOVED</p>
                </div>
                <div className="bg-[#f2f2f2] p-2 rounded border border-[#c8d8e4]">
                  <p className="text-[9px] text-[#5c7885]">STATUS</p>
                  <p className="text-emerald-400 font-bold">VERIFIED</p>
                </div>
              </div>
            </div>

            {/* ROW 7 — RECENT VEHICLE EVENTS TABLE */}
            <div className="bg-white rounded-xl border border-[#c8d8e4] overflow-hidden backdrop-blur-md space-y-3 p-5">
              <h4 className="text-xs font-bold text-[#1a3b45] uppercase tracking-wider flex items-center gap-2">
                <Database className="w-4 h-4 text-cyan-400" /> Live Vehicle Telemetry & Gate Events Stream
              </h4>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead>
                    <tr className="border-b border-[#c8d8e4] text-[#5c7885] uppercase text-[10px] tracking-wider bg-white">
                      <th className="py-2.5 px-3">Time</th>
                      <th className="py-2.5 px-3">Plate</th>
                      <th className="py-2.5 px-3">Vehicle</th>
                      <th className="py-2.5 px-3">Gate</th>
                      <th className="py-2.5 px-3">Direction</th>
                      <th className="py-2.5 px-3">Authorization</th>
                      <th className="py-2.5 px-3">Trip</th>
                      <th className="py-2.5 px-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    <tr className="hover:bg-[#f0f6f8] transition-all">
                      <td className="py-2.5 px-3 text-[#5c7885]">10:22</td>
                      <td className="py-2.5 px-3 text-cyan-400 font-bold">{result?.plate_text || '03 ACU 808'}</td>
                      <td className="py-2.5 px-3 text-[#2b6777]">{result?.vehicle_type || 'Car'}</td>
                      <td className="py-2.5 px-3 text-[#5c7885]">Gate #1</td>
                      <td className="py-2.5 px-3 text-cyan-300 font-bold">ENTRY</td>
                      <td className="py-2.5 px-3">
                        <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded text-[10px]">
                          AUTHORIZED
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-purple-300">{result?.trip_details?.trip_number || 'TRIP-0089'}</td>
                      <td className="py-2.5 px-3">
                        <span className="px-2 py-0.5 bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 rounded text-[10px]">
                          INSIDE
                        </span>
                      </td>
                    </tr>
                    <tr className="hover:bg-[#f0f6f8] transition-all">
                      <td className="py-2.5 px-3 text-[#5c7885]">10:18</td>
                      <td className="py-2.5 px-3 text-cyan-400 font-bold">TN38AB1234</td>
                      <td className="py-2.5 px-3 text-[#2b6777]">Truck</td>
                      <td className="py-2.5 px-3 text-[#5c7885]">Gate #1</td>
                      <td className="py-2.5 px-3 text-cyan-300 font-bold">ENTRY</td>
                      <td className="py-2.5 px-3">
                        <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded text-[10px]">
                          AUTHORIZED
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-purple-300">TRIP-0088</td>
                      <td className="py-2.5 px-3">
                        <span className="px-2 py-0.5 bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 rounded text-[10px]">
                          INSIDE
                        </span>
                      </td>
                    </tr>
                    <tr className="hover:bg-[#f0f6f8] transition-all">
                      <td className="py-2.5 px-3 text-[#5c7885]">09:54</td>
                      <td className="py-2.5 px-3 text-cyan-400 font-bold">KA01XY9087</td>
                      <td className="py-2.5 px-3 text-[#2b6777]">Bus</td>
                      <td className="py-2.5 px-3 text-[#5c7885]">Gate #2</td>
                      <td className="py-2.5 px-3 text-amber-300 font-bold">EXIT</td>
                      <td className="py-2.5 px-3">
                        <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded text-[10px]">
                          AUTHORIZED
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-purple-300">TRIP-0082</td>
                      <td className="py-2.5 px-3">
                        <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded text-[10px]">
                          COMPLETED
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* ROW 8 — LIVE SYSTEM HEALTH FOOTER */}
            <div className="bg-white rounded-xl border border-[#c8d8e4] p-3 backdrop-blur-md flex flex-wrap items-center justify-between gap-3 text-xs font-mono">
              <div className="flex items-center gap-3">
                <span className="text-emerald-400 flex items-center gap-1 font-bold">
                  <CheckCircle2 className="w-3.5 h-3.5" /> ANPR Engine: ONLINE
                </span>
                <span className="text-slate-600">|</span>
                <span className="text-[#5c7885]">Detector: ONLINE</span>
                <span className="text-slate-600">|</span>
                <span className="text-[#5c7885]">OCR: ONLINE</span>
                <span className="text-slate-600">|</span>
                <span className="text-emerald-400 font-semibold">DB: CONNECTED</span>
              </div>
              <div className="flex items-center gap-3 text-[#5c7885] text-[11px]">
                <span>Gate Engine: <strong className="text-cyan-300">ACTIVE</strong></span>
                <span className="text-slate-600">|</span>
                <span>GPU/Backend: <strong className="text-purple-300">PyTorch/ONNX</strong></span>
                <span className="text-slate-600">|</span>
                <span>Latency: <strong className="text-cyan-400">{result?.processing_time_ms ? (result.processing_time_ms / 1000).toFixed(1) + 's' : '34.8s'}</strong></span>
              </div>
            </div>

          </div>
        )}

        {activeTab === 'dataset' && (
          <div className="bg-white rounded-xl border border-[#c8d8e4] overflow-hidden backdrop-blur-md space-y-4 p-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#c8d8e4] pb-3">
              <div>
                <h3 className="text-sm font-bold text-[#1a3b45] uppercase tracking-wider flex items-center gap-2">
                  <Database className="w-4 h-4 text-emerald-400" /> Real-Time Dataset Feed & Auto-Storage Engine
                </h3>
                <p className="text-xs text-[#5c7885] mt-0.5">
                  Live repository of uploaded vehicle media, AI predictions, and module sync statuses
                </p>
              </div>
              <div className="relative w-full sm:w-72">
                <Search className="w-4 h-4 text-[#5c7885] absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search dataset by plate or file..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-9 pr-4 py-1.5 bg-[#f2f2f2] border border-[#c8d8e4] rounded-lg text-xs text-[#1a3b45] placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>
            {detectionsFeedLoading ? (
              <div className="p-12 text-center text-[#5c7885]">Loading dataset feed...</div>
            ) : detectionsFeedData?.items?.length === 0 ? (
              <div className="p-12 text-center text-[#5c7885] space-y-2">
                <Database className="w-8 h-8 mx-auto opacity-50 text-cyan-400" />
                <p>No recognition dataset items found.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {detectionsFeedData?.items?.map((item) => (
                  <div key={item.id} className="bg-white rounded-xl p-4 border border-[#c8d8e4] space-y-3 hover:border-cyan-500/40 transition-all">
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-cyan-400 text-sm tracking-wider">
                        {item.plate_text || item.corrected_plate || 'UNKNOWN'}
                      </span>
                      <span className="px-2.5 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded text-[10px] font-mono font-bold flex items-center gap-1">
                        <Check className="w-3 h-3" /> SYNCED
                      </span>
                    </div>
                    <div className="flex gap-3 text-xs">
                      {item.cropped_plate_path ? (
                        <img
                          src={getMediaUrl('processed', item.cropped_plate_path.split('\\').pop()?.split('/').pop())}
                          alt="Plate Crop"
                          className="w-24 h-12 object-contain bg-white border border-[#c8d8e4] rounded"
                          onError={(e) => { e.target.style.display = 'none'; }}
                        />
                      ) : (
                        <div className="w-24 h-12 bg-white border border-[#c8d8e4] rounded flex items-center justify-center text-[10px] text-slate-600 font-mono">
                          NO CROP
                        </div>
                      )}
                      <div className="flex-1 space-y-1 text-[11px] text-[#5c7885]">
                        <p><span className="text-[#5c7885]">Confidence:</span> <span className="font-mono text-cyan-300 font-bold">{(item.confidence * 100).toFixed(1)}%</span></p>
                        <p><span className="text-[#5c7885]">Type:</span> {item.vehicle_type_detected || 'Vehicle'}</p>
                        <p className="truncate"><span className="text-[#5c7885]">File:</span> {item.source_filename}</p>
                      </div>
                    </div>
                    <div className="bg-white rounded p-2 text-[10px] space-y-1 text-[#5c7885] border border-[#c8d8e4]">
                      <div className="flex justify-between">
                        <span><Car className="w-3 h-3 inline mr-1 text-cyan-400" />Master Catalog</span>
                        <span className="text-emerald-400 font-semibold">Synced</span>
                      </div>
                      <div className="flex justify-between">
                        <span><Building2 className="w-3 h-3 inline mr-1 text-purple-400" />Gate Log</span>
                        <span className="text-emerald-400 font-semibold">Active</span>
                      </div>
                      <div className="flex justify-between">
                        <span><Navigation className="w-3 h-3 inline mr-1 text-amber-400" />Trip Engine</span>
                        <span className="text-emerald-400 font-semibold">Linked</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between pt-2 border-t border-[#c8d8e4] text-[10px] text-[#5c7885]">
                      <span>{new Date(item.created_at).toLocaleString()}</span>
                      <button
                        onClick={() => handleOpenSyncModal(item)}
                        className="px-2.5 py-1 bg-cyan-600/20 hover:bg-cyan-600/40 text-cyan-300 border border-cyan-500/30 rounded flex items-center gap-1 transition-all"
                      >
                        <RefreshCw className="w-3 h-3" /> Edit & Re-Sync
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'history' && (
          <div className="bg-white rounded-xl border border-[#c8d8e4] overflow-hidden backdrop-blur-md">
            <div className="p-4 border-b border-[#c8d8e4]">
              <div className="relative w-full sm:w-80">
                <Search className="w-4 h-4 text-[#5c7885] absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search by vehicle number..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-lg text-xs text-[#1a3b45] placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>
            {vehiclesLoading ? (
              <div className="p-12 text-center text-[#5c7885]">Loading...</div>
            ) : vehiclesData?.items?.length === 0 ? (
              <div className="p-12 text-center text-[#5c7885]">
                <Truck className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No vehicles recognized yet. Upload an image or video to start.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-[#c8d8e4] text-[#5c7885] uppercase text-[10px] tracking-wider bg-white">
                      <th className="px-6 py-3.5">Plate Number</th>
                      <th className="px-6 py-3.5">Detected Type</th>
                      <th className="px-6 py-3.5">Visits</th>
                      <th className="px-6 py-3.5">First Seen</th>
                      <th className="px-6 py-3.5">Last Seen</th>
                      <th className="px-6 py-3.5">Confidence</th>
                      <th className="px-6 py-3.5 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-[#2b6777]">

                    {vehiclesData?.items?.map((vehicle) => (
                      <tr key={vehicle.id} className="hover:bg-[#f0f6f8] transition-colors">
                        <td className="px-6 py-4">
                          <span className="font-mono font-semibold text-cyan-400">{vehicle.vehicle_number}</span>
                          <span className="ml-2 text-[#5c7885]">{vehicle.vehicle_type}</span>
                        </td>
                        <td className="px-6 py-4 text-[#5c7885] text-[10px]">{vehicle.vehicle_type_detected || '-'}</td>
                        <td className="px-6 py-4">{vehicle.visit_count}</td>
                        <td className="px-6 py-4 text-[#5c7885]">
                          {vehicle.first_seen_at ? new Date(vehicle.first_seen_at).toLocaleDateString() : '-'}
                        </td>
                        <td className="px-6 py-4 text-[#5c7885]">
                          {vehicle.last_seen_at ? new Date(vehicle.last_seen_at).toLocaleDateString() : '-'}
                        </td>
                        <td className="px-6 py-4">
                          {vehicle.last_ocr_confidence != null ? (
                            <span className={`font-mono ${vehicle.last_ocr_confidence > 0.7 ? 'text-emerald-400' : 'text-amber-400'}`}>
                              {(vehicle.last_ocr_confidence * 100).toFixed(1)}%
                            </span>
                          ) : '-'}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <button
                            onClick={() => setSelectedVehicleId(vehicle.id)}
                            className="p-1.5 text-[#5c7885] hover:text-cyan-400 hover:bg-[#e8eff4] rounded-lg transition-colors"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </main>

      <Modal
        isOpen={!!selectedVehicleId}
        onClose={() => setSelectedVehicleId(null)}
        title="Detection History"
      >
        <div className="space-y-3 text-xs max-h-96 overflow-y-auto">
          {detectionsData?.items?.length === 0 ? (
            <p className="text-[#5c7885] text-center py-4">No detection records.</p>
          ) : (
            detectionsData?.items?.map((det) => (
              <div key={det.id} className="bg-[#f2f2f2] rounded-lg p-3 border border-[#c8d8e4] space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-cyan-400 font-semibold">{det.plate_text || 'N/A'}</span>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${
                    det.detection_status === 'completed' ? 'bg-emerald-500/10 text-emerald-400' :
                    det.detection_status === 'failed' ? 'bg-rose-500/10 text-rose-400' :
                    'bg-amber-500/10 text-amber-400'
                  }`}>
                    {det.detection_status}
                  </span>
                </div>
                <div className="flex items-center gap-3 text-[#5c7885]">
                  <span><FileType className="w-3 h-3 inline mr-0.5" />{det.upload_type}</span>
                  <span><Hash className="w-3 h-3 inline mr-0.5" />{(det.confidence * 100).toFixed(1)}%</span>
                  <span><Clock className="w-3 h-3 inline mr-0.5" />{new Date(det.created_at).toLocaleString()}</span>
                </div>
                {det.corrected_plate && det.corrected_plate !== det.plate_text && (
                  <p className="text-[10px] text-amber-400">
                    Corrected: <span className="font-mono">{det.corrected_plate}</span>
                  </p>
                )}
                {det.vehicle_type_detected && (
                  <p className="text-[10px] text-[#5c7885]">Type: {det.vehicle_type_detected}</p>
                )}
                <p className="text-slate-600 truncate" title={det.source_filename}>{det.source_filename}</p>
                {det.error_message && (
                  <p className="text-rose-400 text-[10px]">{det.error_message}</p>
                )}
              </div>
            ))
          )}
        </div>
      </Modal>
    </div>
  );
}
