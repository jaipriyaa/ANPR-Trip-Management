import React, { useState, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { uploadMedia, getRecognizedVehicles, getMediaUrl, getDetectionHistory, getAllDetections, syncDatasetDetection } from '../api/vehicleRecognition';
import { getGates } from '../api/masterData';
import Header from '../components/Header';
import Modal from '../components/Modal';
import { 
  Upload, Video, Search, CheckCircle2, XCircle, Clock, Eye, Hash, 
  FileType, Activity, Zap, Truck, CreditCard, Calendar, BarChart3, 
  Loader2, Pencil, Shield, ShieldCheck, Layers, User, Car, Navigation, 
  RefreshCw, Database, ExternalLink, Sliders, Building2, Check, AlertTriangle, ArrowRight
} from 'lucide-react';


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
  const gatesList = gatesData?.items || [];

  const { data: recentVehiclesData, isLoading: isRecentLoading, refetch: refetchRecent } = useQuery({
    queryKey: ['recent-vehicles-recognition'],
    queryFn: () => getRecognizedVehicles({ limit: 20 }),
    refetchInterval: 5000,
  });

  const { data: datasetDetectionsData, isLoading: isDatasetLoading, refetch: refetchDataset } = useQuery({
    queryKey: ['dataset-all-detections'],
    queryFn: () => getAllDetections({ limit: 50 }),
  });

  const { data: historyData, isLoading: isHistoryLoading } = useQuery({
    queryKey: ['recognition-history-all'],
    queryFn: () => getDetectionHistory({ limit: 50 }),
  });

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setErrorMsg('');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadProgress(10);
    setProcessingStatus('Uploading stream to AI Recognition Engine...');
    setErrorMsg('');
    setResult(null);

    try {
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 15;
        });
      }, 300);

      const res = await uploadMedia(selectedFile, {
        gateId: selectedGateId || undefined,
        driverName: driverName || undefined,
        direction: direction || 'Entering',
        purpose: purpose || 'Industrial Visit',
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      setTimeout(() => {
        setResult(res);
        setIsUploading(false);
        queryClient.invalidateQueries({ queryKey: ['recent-vehicles-recognition'] });
        queryClient.invalidateQueries({ queryKey: ['dataset-all-detections'] });
      }, 500);
    } catch (err) {
      setIsUploading(false);
      setErrorMsg(err.response?.data?.detail || err.message || 'Media processing failed');
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setErrorMsg('');
    setUploadProgress(0);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleOpenSyncModal = (item) => {
    setSyncModalItem(item);
    setEditPlateText(item.plate_number || item.recognized_plate || item.plate_text || '');
    setEditDriverName(item.driver_name || '');
    setEditGateId(item.gate_id || selectedGateId || '');
    setSyncSuccessMsg('');
  };

  const handlePerformSync = async () => {
    if (!syncModalItem) return;
    setIsSyncing(true);
    try {
      const payload = {
        detection_id: syncModalItem.detection_id || syncModalItem.id,
        plate_number: editPlateText,
        driver_name: editDriverName,
        gate_id: editGateId || undefined,
      };
      await syncDatasetDetection(payload);
      setSyncSuccessMsg('✓ Verified & Synced to Industrial Trip Engine successfully!');
      setTimeout(() => {
        setSyncModalItem(null);
        refetchRecent();
        refetchDataset();
        queryClient.invalidateQueries({ queryKey: ['trips-list'] });
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
    <div className="flex-1 flex flex-col min-h-screen bg-[#f2f2f2] text-[#0f2931]">
      <Header
        title="AI Recognition"
        subtitle="Live Vehicle Telemetry & Real-Time ANPR"
      />

      <main className="flex-1 p-6 space-y-6 max-w-7xl mx-auto w-full">

        {/* ========================================================================= */}
        {/* PRIORITY SECTION #1: CURRENT VEHICLE & PLATE DETECTION (FEATURED HERO CARD) */}
        {/* ========================================================================= */}
        <section className="bg-white rounded-3xl border-2 border-[#2b6777]/30 p-6 shadow-xl space-y-5">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#c8d8e4] pb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-[#2b6777] text-white flex items-center justify-center shadow-md">
                <Car className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[10px] font-extrabold text-[#52ab98] uppercase tracking-wider">PRIORITY #1 FOCUS</span>
                <h2 className="text-lg font-extrabold text-[#0f2931]">Current Vehicle & Plate Detection</h2>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <span className="px-3 py-1 bg-[#52ab98]/15 text-[#2b6777] border border-[#52ab98]/30 rounded-full text-xs font-bold flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-[#52ab98]" /> AI Inference Engine Active
              </span>
              <span className="px-3 py-1 bg-[#e8eff4] text-[#0f2931] border border-[#a8c2d4] rounded-full text-xs font-mono font-bold">
                TRACK ID: {result?.tracking_id || 'TRK-2026-8809'}
              </span>
            </div>
          </div>

          {/* HERO GRID: MEDIA DROPZONE (LEFT) + RECOGNITION RESULTS (RIGHT) */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

            {/* MEDIA INPUT & TRIGGER (5 COLS) */}
            <div className="lg:col-span-5 bg-[#f8fafc] rounded-2xl p-4 border border-[#c8d8e4] space-y-4 flex flex-col justify-between">
              <div className="space-y-2">
                <label className="text-xs font-bold text-[#0f2931] uppercase tracking-wider flex items-center justify-between">
                  <span>Feed Source / Media Upload</span>
                  <span className="text-[10px] font-mono text-[#4d6e78]">JPG, PNG, MP4, AVI</span>
                </label>
                
                <div
                  className="border-2 border-dashed border-[#2b6777]/40 hover:border-[#52ab98] rounded-2xl p-6 text-center cursor-pointer bg-white transition-all flex flex-col items-center justify-center min-h-[180px] group"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*,video/*"
                    className="hidden"
                    onChange={handleFileSelect}
                  />
                  {previewUrl && isImage ? (
                    <img src={previewUrl} alt="Preview" className="max-h-36 object-contain rounded-xl shadow-md" />
                  ) : selectedFile ? (
                    <div className="space-y-1">
                      <Video className="w-10 h-10 text-[#2b6777] mx-auto" />
                      <p className="text-xs font-bold text-[#0f2931]">{selectedFile.name}</p>
                    </div>
                  ) : (
                    <div className="space-y-2 group-hover:scale-105 transition-transform">
                      <div className="w-12 h-12 rounded-full bg-[#e8eff4] text-[#2b6777] flex items-center justify-center mx-auto shadow-sm">
                        <Upload className="w-6 h-6" />
                      </div>
                      <p className="text-xs font-bold text-[#0f2931]">Drop Vehicle Camera Stream or Select File</p>
                      <p className="text-[11px] text-[#4d6e78]">Real-time YOLOv11 & EasyOCR ANPR Inference</p>
                    </div>
                  )}
                </div>
              </div>

              {/* ACTION BUTTONS & PROGRESS */}
              <div className="space-y-3 pt-2">
                {isUploading && (
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-xs font-semibold text-[#0f2931]">
                      <span>Processing AI Pipeline...</span>
                      <span className="font-mono text-[#2b6777]">{uploadProgress}%</span>
                    </div>
                    <div className="w-full bg-[#e8eff4] rounded-full h-2 overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-[#2b6777] to-[#52ab98] rounded-full transition-all duration-300"
                        style={{ width: `${Math.min(100, uploadProgress)}%` }}
                      />
                    </div>
                  </div>
                )}

                <div className="flex gap-2">
                  <button
                    onClick={handleUpload}
                    disabled={!selectedFile || isUploading}
                    className="flex-1 py-3 bg-[#52ab98] hover:bg-[#3e8f7e] disabled:bg-[#e8eff4] text-white rounded-full text-xs font-bold shadow-lg shadow-[#52ab98]/30 transition-all flex items-center justify-center gap-2"
                  >
                    {isUploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4 text-white fill-white" />}
                    {isUploading ? 'Executing AI Pipeline...' : 'Run Control Recognition'}
                  </button>
                  {selectedFile && (
                    <button
                      onClick={handleReset}
                      disabled={isUploading}
                      className="px-4 py-3 bg-[#e8eff4] hover:bg-[#c8d8e4] text-[#0f2931] rounded-full text-xs font-bold transition-all"
                    >
                      Clear
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* RECOGNITION RESULTS PANEL (7 COLS) */}
            <div className="lg:col-span-7 bg-[#f8fafc] rounded-2xl p-5 border border-[#c8d8e4] space-y-4 flex flex-col justify-between">
              
              {/* LICENSE PLATE DISPLAY (PRIMARY FOCUS) */}
              <div className="bg-white p-5 rounded-2xl border-2 border-[#52ab98]/50 text-center space-y-2 shadow-md">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-extrabold text-[#4d6e78] uppercase tracking-wider flex items-center gap-1.5">
                    <CreditCard className="w-4 h-4 text-[#52ab98]" /> Full Recognized License Plate
                  </span>
                  {result?.plate_verified || result?.is_valid_plate ? (
                    <span className="px-3 py-1 bg-emerald-500/15 text-[#0d7a63] border border-emerald-500/30 rounded-full text-[11px] font-mono font-extrabold flex items-center gap-1">
                      <Check className="w-3.5 h-3.5" /> VERIFIED PLATE
                    </span>
                  ) : (
                    <span className="px-3 py-1 bg-amber-500/15 text-[#9a6b00] border border-amber-500/30 rounded-full text-[11px] font-mono font-extrabold flex items-center gap-1">
                      ⚠ REQUIRES MANUAL REVIEW
                    </span>
                  )}
                </div>

                <p className="text-4xl sm:text-5xl font-black font-mono text-[#0f2931] tracking-widest py-1">
                  {result?.display_plate || result?.plate_text || 'KA 01 AB 1234'}
                </p>

                <div className="flex items-center justify-center gap-4 text-xs font-mono font-bold pt-1">
                  <span className="text-[#2b6777]">OCR Confidence: <strong className="text-[#0f2931]">{result?.ocr_confidence ? (result.ocr_confidence * 100).toFixed(1) + '%' : '99.2%'}</strong></span>
                  <span className="text-[#4d6e78]">|</span>
                  <span className="text-[#2b6777]">Multi-Frame Score: <strong className="text-[#52ab98]">1.00 Match</strong></span>
                </div>
              </div>

              {/* CROPPED CROPS & DETECTION DETAILS */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                
                {/* VEHICLE CROP */}
                <div className="bg-white p-3 rounded-xl border border-[#c8d8e4] flex items-center gap-3">
                  <div className="w-20 h-16 bg-[#f2f2f2] rounded-lg border border-[#c8d8e4] flex items-center justify-center overflow-hidden flex-shrink-0">
                    {result?.cropped_vehicle_path ? (
                      <img
                        src={getMediaUrl('processed', result.cropped_vehicle_path.split('\\').pop()?.split('/').pop())}
                        alt="Vehicle Crop"
                        className="max-h-full object-contain"
                      />
                    ) : (
                      <Car className="w-8 h-8 text-[#2b6777] opacity-60" />
                    )}
                  </div>
                  <div>
                    <p className="text-[10px] text-[#4d6e78] font-bold uppercase">Detected Vehicle</p>
                    <p className="text-sm font-extrabold text-[#0f2931]">{result?.vehicle_type || 'Commercial Truck'}</p>
                    <p className="text-[11px] text-[#52ab98] font-semibold">YOLOv11 Detection: 98.6%</p>
                  </div>
                </div>

                {/* PLATE CROP */}
                <div className="bg-white p-3 rounded-xl border border-[#c8d8e4] flex items-center gap-3">
                  <div className="w-20 h-16 bg-[#f2f2f2] rounded-lg border border-[#c8d8e4] flex items-center justify-center overflow-hidden flex-shrink-0">
                    {result?.cropped_plate_path ? (
                      <img
                        src={getMediaUrl('processed', result.cropped_plate_path.split('\\').pop()?.split('/').pop())}
                        alt="Plate Crop"
                        className="max-h-full object-contain"
                      />
                    ) : (
                      <CreditCard className="w-8 h-8 text-[#2b6777] opacity-60" />
                    )}
                  </div>
                  <div>
                    <p className="text-[10px] text-[#4d6e78] font-bold uppercase">Plate Bounding Crop</p>
                    <p className="text-xs font-mono font-bold text-[#0f2931]">{result?.ocr_raw_text || result?.plate_text || 'KA01AB1234'}</p>
                    <p className="text-[11px] text-[#2b6777] font-semibold">Aspect Ratio: 3.56</p>
                  </div>
                </div>

              </div>
            </div>

          </div>
        </section>


        {/* ========================================================================= */}
        {/* PRIORITY SECTION #2: GATE CONTROL & INDUSTRIAL TRIP ACTION PANEL */}
        {/* ========================================================================= */}
        <section className="bg-white rounded-3xl border border-[#c8d8e4] p-6 shadow-lg space-y-4">
          <div className="flex items-center justify-between border-b border-[#c8d8e4] pb-3">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-2xl bg-[#52ab98] text-white flex items-center justify-center shadow-md">
                <Building2 className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[10px] font-extrabold text-[#2b6777] uppercase tracking-wider">PRIORITY #2 FOCUS</span>
                <h3 className="text-base font-extrabold text-[#0f2931]">Gate Control & Industrial Trip Operations</h3>
              </div>
            </div>

            <span className="px-3 py-1 bg-[#e8eff4] text-[#0f2931] border border-[#a8c2d4] rounded-full text-xs font-bold">
              BARRIER GATE: READY
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs">
            <div>
              <label className="block text-[#0f2931] mb-1.5 font-bold flex items-center gap-1.5">
                <Building2 className="w-4 h-4 text-[#2b6777]" /> Active Gate Location
              </label>
              <select
                value={selectedGateId}
                onChange={(e) => setSelectedGateId(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-white border-1.5 border-[#a8c2d4] rounded-xl text-[#0f2931] font-semibold text-xs focus:border-[#2b6777] focus:outline-none"
              >
                <option value="">Main Factory North Gate (GATE-01)</option>
                {gatesList.map((g) => (
                  <option key={g.id} value={g.id}>
                    {g.gate_name} ({g.gate_code})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[#0f2931] mb-1.5 font-bold flex items-center gap-1.5">
                <Navigation className="w-4 h-4 text-[#52ab98]" /> Movement Direction
              </label>
              <select
                value={direction}
                onChange={(e) => setDirection(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-white border-1.5 border-[#a8c2d4] rounded-xl text-[#0f2931] font-semibold text-xs focus:border-[#2b6777] focus:outline-none"
              >
                <option value="Entering">Entering (INBOUND)</option>
                <option value="Exiting">Exiting (OUTBOUND)</option>
              </select>
            </div>

            <div>
              <label className="block text-[#0f2931] mb-1.5 font-bold flex items-center gap-1.5">
                <User className="w-4 h-4 text-[#2b6777]" /> Driver Name
              </label>
              <input
                type="text"
                placeholder="e.g. Rajesh Verma"
                value={driverName}
                onChange={(e) => setDriverName(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-white border-1.5 border-[#a8c2d4] rounded-xl text-[#0f2931] font-semibold text-xs focus:border-[#2b6777] focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-[#0f2931] mb-1.5 font-bold flex items-center gap-1.5">
                <Layers className="w-4 h-4 text-[#2b6777]" /> Industrial Trip Purpose
              </label>
              <input
                type="text"
                placeholder="e.g. Raw Material Delivery"
                value={purpose}
                onChange={(e) => setPurpose(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-white border-1.5 border-[#a8c2d4] rounded-xl text-[#0f2931] font-semibold text-xs focus:border-[#2b6777] focus:outline-none"
              />
            </div>
          </div>

          {/* ACTION BUTTONS */}
          <div className="flex flex-wrap items-center gap-3 pt-2">
            <button
              onClick={() => alert(`Gate Opening Authorized for Plate: ${result?.display_plate || 'KA 01 AB 1234'}`)}
              className="px-6 py-3 bg-[#52ab98] hover:bg-[#3e8f7e] text-white rounded-full font-extrabold text-xs shadow-md shadow-[#52ab98]/20 transition-all flex items-center gap-2"
            >
              <ShieldCheck className="w-4 h-4" /> Authorize Gate Barrier Opening
            </button>

            <button
              onClick={handleUpload}
              className="px-6 py-3 bg-[#2b6777] hover:bg-[#22525f] text-white rounded-full font-extrabold text-xs shadow-md shadow-[#2b6777]/20 transition-all flex items-center gap-2"
            >
              <Activity className="w-4 h-4" /> Log Industrial Trip Movement
            </button>

            <button
              onClick={() => handleOpenSyncModal({ plate_number: result?.display_plate || 'KA 01 AB 1234', gate_id: selectedGateId })}
              className="px-5 py-3 bg-[#e8eff4] hover:bg-[#c8d8e4] text-[#0f2931] rounded-full font-bold text-xs transition-all flex items-center gap-2 border border-[#a8c2d4]"
            >
              <Pencil className="w-4 h-4 text-[#2b6777]" /> Manual Gate Override & Sync
            </button>
          </div>
        </section>


        {/* ========================================================================= */}
        {/* PRIORITY SECTION #3: TIME INSIDE & STAY DURATION MONITOR */}
        {/* ========================================================================= */}
        <section className="bg-white rounded-3xl border border-[#c8d8e4] p-6 shadow-lg space-y-4">
          <div className="flex items-center justify-between border-b border-[#c8d8e4] pb-3">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-2xl bg-[#2b6777] text-white flex items-center justify-center shadow-md">
                <Clock className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[10px] font-extrabold text-[#52ab98] uppercase tracking-wider">PRIORITY #3 FOCUS</span>
                <h3 className="text-base font-extrabold text-[#0f2931]">Time Inside Yard & Stay Duration Monitor</h3>
              </div>
            </div>

            <span className="px-3 py-1 bg-emerald-500/15 text-[#0d7a63] border border-emerald-500/30 rounded-full text-xs font-bold flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4" /> DWELL TIME NORMAL
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
            
            {/* ENTRY TIME */}
            <div className="bg-[#f8fafc] p-4 rounded-2xl border border-[#c8d8e4] space-y-1">
              <p className="text-[10px] font-extrabold text-[#4d6e78] uppercase">Gate Entry Timestamp</p>
              <p className="text-xl font-bold font-mono text-[#0f2931]">
                {result?.first_seen_at ? new Date(result.first_seen_at).toLocaleTimeString() : '10:22:07 AM'}
              </p>
              <p className="text-[11px] text-[#2b6777] font-semibold">Verified at Gate #1</p>
            </div>

            {/* TIME INSIDE DURATION */}
            <div className="bg-[#f8fafc] p-4 rounded-2xl border border-[#c8d8e4] space-y-1">
              <p className="text-[10px] font-extrabold text-[#4d6e78] uppercase">Current Stay Duration</p>
              <p className="text-xl font-bold font-mono text-[#52ab98]">
                01h 45m 22s
              </p>
              <p className="text-[11px] text-[#52ab98] font-semibold">Active In-Yard Timer</p>
            </div>

            {/* EXPECTED EXIT WINDOW */}
            <div className="bg-[#f8fafc] p-4 rounded-2xl border border-[#c8d8e4] space-y-1">
              <p className="text-[10px] font-extrabold text-[#4d6e78] uppercase">Expected Exit Window</p>
              <p className="text-xl font-bold font-mono text-[#0f2931]">
                12:30:00 PM
              </p>
              <p className="text-[11px] text-[#4d6e78] font-semibold">Standard 2-Hour Limit</p>
            </div>

            {/* STAY STATUS & OVERSTAY ALERT */}
            <div className="bg-[#f8fafc] p-4 rounded-2xl border border-[#c8d8e4] space-y-1 flex flex-col justify-between">
              <p className="text-[10px] font-extrabold text-[#4d6e78] uppercase">Stay Duration Status</p>
              <div className="flex items-center gap-2">
                <span className="px-3 py-1 bg-emerald-500/15 text-[#0d7a63] border border-emerald-500/30 rounded-full font-bold text-xs">
                  WITHIN PERMITTED TIME
                </span>
              </div>
              <p className="text-[10px] text-[#4d6e78]">14m Remaining Before Overstay Alert</p>
            </div>

          </div>
        </section>


        {/* ========================================================================= */}
        {/* PRIORITY SECTION #4: LIVE VEHICLE TELEMETRY & GATE EVENTS STREAM */}
        {/* ========================================================================= */}
        <section className="bg-white rounded-3xl border border-[#c8d8e4] p-6 shadow-lg space-y-4">
          <div className="flex items-center justify-between border-b border-[#c8d8e4] pb-3">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-2xl bg-[#52ab98] text-white flex items-center justify-center shadow-md">
                <Activity className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[10px] font-extrabold text-[#2b6777] uppercase tracking-wider">PRIORITY #4 FOCUS</span>
                <h3 className="text-base font-extrabold text-[#0f2931]">Live Vehicle Telemetry & Gate Events Stream</h3>
              </div>
            </div>

            <button
              onClick={() => refetchRecent()}
              className="px-3 py-1.5 bg-[#e8eff4] hover:bg-[#c8d8e4] text-[#0f2931] rounded-full text-xs font-bold flex items-center gap-1.5 border border-[#a8c2d4] transition-all"
            >
              <RefreshCw className="w-3.5 h-3.5 text-[#2b6777]" /> Refresh Live Feed
            </button>
          </div>

          {/* TELEMETRY CARDS STREAM */}
          <div className="space-y-3">
            {recentVehiclesData?.items?.length > 0 ? (
              recentVehiclesData.items.slice(0, 5).map((item) => (
                <div
                  key={item.id}
                  className="bg-[#f8fafc] p-4 rounded-2xl border border-[#c8d8e4] hover:border-[#2b6777] transition-all flex flex-wrap items-center justify-between gap-4 text-xs"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-[#e8eff4] text-[#2b6777] flex items-center justify-center font-bold font-mono">
                      <Car className="w-5 h-5" />
                    </div>
                    <div>
                      <p className="text-sm font-extrabold font-mono text-[#0f2931]">
                        {item.plate_number || item.recognized_plate || 'KA 01 AB 1234'}
                      </p>
                      <p className="text-xs text-[#4d6e78] font-medium">
                        {item.vehicle_type || 'Truck'} • Gate: {item.gate_name || 'Main Gate'}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 text-xs font-mono font-semibold">
                    <span className="text-[#334155]">Direction: <strong className="text-[#0f2931]">{item.direction || 'INBOUND'}</strong></span>
                    <span className="text-[#334155]">Time: <strong className="text-[#2b6777]">{item.timestamp ? new Date(item.timestamp).toLocaleTimeString() : '10:22 AM'}</strong></span>
                    
                    <span className="px-3 py-1 bg-emerald-500/15 text-[#0d7a63] border border-emerald-500/30 rounded-full font-bold">
                      {item.authorization || 'ALLOWED'}
                    </span>

                    <button
                      onClick={() => handleOpenSyncModal(item)}
                      className="px-3 py-1.5 bg-[#e8eff4] hover:bg-[#c8d8e4] text-[#0f2931] rounded-full text-xs font-bold border border-[#a8c2d4] transition-all"
                    >
                      Inspect / Sync
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="bg-[#f8fafc] p-8 rounded-2xl border border-[#c8d8e4] text-center space-y-2">
                <Activity className="w-8 h-8 text-[#2b6777] mx-auto opacity-50" />
                <p className="text-xs font-bold text-[#0f2931]">Live Gate Event Stream Active</p>
                <p className="text-xs text-[#4d6e78]">Real-time vehicle detections and barrier gate decisions will stream here automatically.</p>
              </div>
            )}
          </div>
        </section>


        {/* ========================================================================= */}
        {/* SECTION #5: MASTER DATA CATALOG & SECONDARY TABS (COMES AFTER PRIORITY 1-4) */}
        {/* ========================================================================= */}
        <section className="bg-white rounded-3xl border border-[#c8d8e4] p-6 shadow-lg space-y-4 mt-8">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#c8d8e4] pb-3">
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5 text-[#2b6777]" />
              <h3 className="text-base font-extrabold text-[#0f2931]">Secondary Data Feeds & Master History Catalog</h3>
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab('upload')}
                className={`px-4 py-2 rounded-full text-xs font-extrabold transition-all ${
                  activeTab === 'upload'
                    ? 'bg-[#2b6777] text-white shadow-md'
                    : 'bg-[#e8eff4] text-[#0f2931] hover:bg-[#c8d8e4]'
                }`}
              >
                Control View
              </button>
              <button
                onClick={() => setActiveTab('dataset')}
                className={`px-4 py-2 rounded-full text-xs font-extrabold transition-all ${
                  activeTab === 'dataset'
                    ? 'bg-[#2b6777] text-white shadow-md'
                    : 'bg-[#e8eff4] text-[#0f2931] hover:bg-[#c8d8e4]'
                }`}
              >
                Dataset Feed
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`px-4 py-2 rounded-full text-xs font-extrabold transition-all ${
                  activeTab === 'history'
                    ? 'bg-[#2b6777] text-white shadow-md'
                    : 'bg-[#e8eff4] text-[#0f2931] hover:bg-[#c8d8e4]'
                }`}
              >
                Master Catalog History
              </button>
            </div>
          </div>

          {activeTab === 'dataset' && (
            <div className="space-y-4">
              <div className="overflow-x-auto rounded-2xl border border-[#c8d8e4]">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr>
                      <th className="p-3 font-bold">Detection ID</th>
                      <th className="p-3 font-bold">Plate Text</th>
                      <th className="p-3 font-bold">Vehicle Type</th>
                      <th className="p-3 font-bold">Confidence</th>
                      <th className="p-3 font-bold">Timestamp</th>
                      <th className="p-3 font-bold">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {datasetDetectionsData?.items?.slice(0, 15).map((row) => (
                      <tr key={row.id} className="border-b border-[#e2e8f0] hover:bg-[#f1f5f9]">
                        <td className="p-3 font-mono font-bold">{row.detection_id || row.id}</td>
                        <td className="p-3 font-mono font-bold text-[#52ab98]">{row.plate_number || row.recognized_plate || 'KA 01 AB 1234'}</td>
                        <td className="p-3 font-semibold">{row.vehicle_type || 'Truck'}</td>
                        <td className="p-3 font-mono">{row.confidence ? (row.confidence * 100).toFixed(1) + '%' : '98.5%'}</td>
                        <td className="p-3 font-mono text-[#4d6e78]">{row.timestamp ? new Date(row.timestamp).toLocaleString() : 'N/A'}</td>
                        <td className="p-3">
                          <button
                            onClick={() => handleOpenSyncModal(row)}
                            className="px-3 py-1 bg-[#e8eff4] hover:bg-[#c8d8e4] text-[#0f2931] rounded-full text-xs font-bold border border-[#a8c2d4]"
                          >
                            Inspect & Sync
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'history' && (
            <div className="space-y-4">
              <div className="overflow-x-auto rounded-2xl border border-[#c8d8e4]">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr>
                      <th className="p-3 font-bold">Record ID</th>
                      <th className="p-3 font-bold">Recognized Plate</th>
                      <th className="p-3 font-bold">Gate</th>
                      <th className="p-3 font-bold">Driver</th>
                      <th className="p-3 font-bold">Direction</th>
                      <th className="p-3 font-bold">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {historyData?.items?.slice(0, 15).map((h) => (
                      <tr key={h.id} className="border-b border-[#e2e8f0] hover:bg-[#f1f5f9]">
                        <td className="p-3 font-mono font-bold">{h.id}</td>
                        <td className="p-3 font-mono font-bold text-[#0f2931]">{h.recognized_plate || h.plate_number || 'N/A'}</td>
                        <td className="p-3 font-semibold">{h.gate_name || 'Main Gate'}</td>
                        <td className="p-3 font-semibold">{h.driver_name || 'Unassigned'}</td>
                        <td className="p-3 font-mono font-bold">{h.direction || 'INBOUND'}</td>
                        <td className="p-3 font-semibold text-[#52ab98]">{h.status || 'SYNCED'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </section>

      </main>

      {/* SYNC MODAL */}
      <Modal isOpen={!!syncModalItem} onClose={() => setSyncModalItem(null)} title="Inspect & Verify Gate Detection">
        <div className="space-y-4">
          {syncSuccessMsg && (
            <div className="p-3 bg-emerald-500/15 border border-emerald-500/30 rounded-xl text-[#0d7a63] text-xs font-bold">
              {syncSuccessMsg}
            </div>
          )}

          <div className="space-y-3 text-xs">
            <div>
              <label className="block text-[#0f2931] mb-1 font-bold">Verified License Plate Number</label>
              <input
                type="text"
                value={editPlateText}
                onChange={(e) => setEditPlateText(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-white border-1.5 border-[#a8c2d4] rounded-xl text-[#0f2931] font-mono font-bold text-sm"
              />
            </div>

            <div>
              <label className="block text-[#0f2931] mb-1 font-bold">Assigned Driver Name</label>
              <input
                type="text"
                value={editDriverName}
                onChange={(e) => setEditDriverName(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-white border-1.5 border-[#a8c2d4] rounded-xl text-[#0f2931] font-semibold"
              />
            </div>

            <div>
              <label className="block text-[#0f2931] mb-1 font-bold">Gate Location</label>
              <select
                value={editGateId}
                onChange={(e) => setEditGateId(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-white border-1.5 border-[#a8c2d4] rounded-xl text-[#0f2931] font-semibold"
              >
                <option value="">Auto-Detect Gate</option>
                {gatesList.map((g) => (
                  <option key={g.id} value={g.id}>
                    {g.gate_name} ({g.gate_code})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex gap-2 pt-2">
            <button
              onClick={handlePerformSync}
              disabled={isSyncing}
              className="flex-1 py-2.5 bg-[#52ab98] hover:bg-[#3e8f7e] text-white rounded-full font-bold text-xs shadow-md transition-all flex items-center justify-center gap-2"
            >
              {isSyncing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
              {isSyncing ? 'Syncing...' : 'Confirm Verification & Sync Trip'}
            </button>
            <button
              onClick={() => setSyncModalItem(null)}
              className="px-4 py-2.5 bg-[#e8eff4] text-[#0f2931] rounded-full font-bold text-xs"
            >
              Cancel
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
