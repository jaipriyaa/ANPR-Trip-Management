import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import { 
  Camera, 
  Cpu, 
  Settings, 
  AlertTriangle, 
  Activity, 
  CheckCircle2, 
  XCircle, 
  RefreshCw, 
  Wifi, 
  Sliders, 
  ShieldAlert,
  Save
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function SystemHealthPage() {
  const [activeTab, setActiveTab] = useState('camera'); // 'camera', 'model', 'settings', 'alerts'
  const [cameraHealth, setCameraHealth] = useState([]);
  const [modelHealth, setModelHealth] = useState(null);
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(false);

  const fetchHealthData = async () => {
    setLoading(true);
    try {
      const [cRes, mRes, sRes] = await Promise.all([
        fetch(`${API_BASE_URL}/admin/camera-health`),
        fetch(`${API_BASE_URL}/admin/model-health`),
        fetch(`${API_BASE_URL}/admin/settings`),
      ]);
      if (cRes.ok) setCameraHealth(await cRes.json());
      if (mRes.ok) setModelHealth(await mRes.json());
      if (sRes.ok) setSettings(await sRes.json());
    } catch (err) {
      console.error('Failed to fetch system health data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealthData();
    const interval = setInterval(fetchHealthData, 5000); // 5s auto refresh
    return () => clearInterval(interval);
  }, []);

  const handleSaveSettings = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE_URL}/admin/settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      });
      if (res.ok) {
        alert('System settings updated successfully.');
        fetchHealthData();
      }
    } catch (err) {
      console.error('Failed to save settings:', err);
    }
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-slate-950 text-slate-100 font-sans">
      <Header title="System & Health Management" subtitle="Live RTSP camera monitoring, AI deep learning model performance, system configuration thresholds, and alert center" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Tab Navigation */}
        <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
          <button
            onClick={() => setActiveTab('camera')}
            className={`px-4 py-2 rounded-xl font-bold text-xs flex items-center gap-2 transition-all ${
              activeTab === 'camera'
                ? 'bg-cyan-500 text-slate-950 shadow-lg shadow-cyan-500/20'
                : 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-white'
            }`}
          >
            <Camera className="w-4 h-4" /> Camera Health
          </button>

          <button
            onClick={() => setActiveTab('model')}
            className={`px-4 py-2 rounded-xl font-bold text-xs flex items-center gap-2 transition-all ${
              activeTab === 'model'
                ? 'bg-cyan-500 text-slate-950 shadow-lg shadow-cyan-500/20'
                : 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-white'
            }`}
          >
            <Cpu className="w-4 h-4" /> AI Model Health
          </button>

          <button
            onClick={() => setActiveTab('settings')}
            className={`px-4 py-2 rounded-xl font-bold text-xs flex items-center gap-2 transition-all ${
              activeTab === 'settings'
                ? 'bg-cyan-500 text-slate-950 shadow-lg shadow-cyan-500/20'
                : 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-white'
            }`}
          >
            <Settings className="w-4 h-4" /> System Settings
          </button>

          <button
            onClick={() => setActiveTab('alerts')}
            className={`px-4 py-2 rounded-xl font-bold text-xs flex items-center gap-2 transition-all ${
              activeTab === 'alerts'
                ? 'bg-cyan-500 text-slate-950 shadow-lg shadow-cyan-500/20'
                : 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-white'
            }`}
          >
            <AlertTriangle className="w-4 h-4" /> Alert Center
          </button>
        </div>

        {/* Tab 1: Camera Health Monitoring */}
        {activeTab === 'camera' && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {cameraHealth.map((cam) => (
                <div key={cam.camera_id} className="bg-slate-900/80 rounded-xl border border-slate-800 p-5 space-y-3 backdrop-blur-md">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                    <div>
                      <h4 className="font-bold text-sm text-white">{cam.camera_name}</h4>
                      <p className="text-xs text-purple-400 font-mono">{cam.gate_code}</p>
                    </div>
                    <span className={`px-2.5 py-1 rounded text-[10px] font-bold font-mono border ${
                      cam.status === 'Online'
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                        : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                    }`}>
                      ● {cam.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                    <div className="bg-slate-950 p-2 rounded-lg border border-slate-800">
                      <span className="text-slate-500 text-[10px] block">Frame Rate</span>
                      <span className="font-bold text-cyan-400">{cam.fps} FPS</span>
                    </div>
                    <div className="bg-slate-950 p-2 rounded-lg border border-slate-800">
                      <span className="text-slate-500 text-[10px] block">Stream Latency</span>
                      <span className="font-bold text-emerald-400">{cam.latency_ms} ms</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs text-slate-400 pt-1">
                    <span>Resolution: {cam.resolution}</span>
                    <span className="text-slate-500 font-mono">Frame: {cam.last_frame_time}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 2: AI Model Health */}
        {activeTab === 'model' && modelHealth && (
          <div className="bg-slate-900/80 rounded-xl border border-slate-800 p-6 space-y-6 backdrop-blur-md">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Cpu className="w-5 h-5 text-cyan-400" /> Deep Learning AI Engine Metrics
                </h3>
                <p className="text-xs text-slate-400 pt-0.5">Model Version: <span className="font-mono text-cyan-400">{modelHealth.model_version}</span></p>
              </div>
              <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-3 py-1.5 rounded-xl font-bold font-mono text-xs">
                ● {modelHealth.model_status}
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                <p className="text-slate-500 text-xs mb-1">Avg Inference Time</p>
                <p className="text-2xl font-extrabold text-cyan-400 font-mono">{modelHealth.average_inference_ms} ms</p>
              </div>
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                <p className="text-slate-500 text-xs mb-1">GPU Usage</p>
                <p className="text-2xl font-extrabold text-emerald-400 font-mono">{modelHealth.gpu_usage_pct}%</p>
              </div>
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                <p className="text-slate-500 text-xs mb-1">CPU Load</p>
                <p className="text-2xl font-extrabold text-purple-300 font-mono">{modelHealth.cpu_usage_pct}%</p>
              </div>
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                <p className="text-slate-500 text-xs mb-1">Recognition Accuracy</p>
                <p className="text-2xl font-extrabold text-emerald-400 font-mono">{modelHealth.recognition_accuracy_pct}%</p>
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: System Settings */}
        {activeTab === 'settings' && (
          <form onSubmit={handleSaveSettings} className="bg-slate-900/80 rounded-xl border border-slate-800 p-6 space-y-6 backdrop-blur-md max-w-2xl">
            <h3 className="text-base font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
              <Settings className="w-5 h-5 text-cyan-400" /> Platform Configuration Thresholds
            </h3>

            <div className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Recognition Confidence Threshold (0.50 - 1.00)</label>
                <input
                  type="text"
                  value={settings.recognition_confidence_threshold || '0.75'}
                  onChange={(e) => setSettings({ ...settings, recognition_confidence_threshold: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Duplicate Suppression Window (Seconds)</label>
                <input
                  type="text"
                  value={settings.duplicate_suppression_window_seconds || '120'}
                  onChange={(e) => setSettings({ ...settings, duplicate_suppression_window_seconds: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Maximum File Upload Limit (MB)</label>
                <input
                  type="text"
                  value={settings.max_upload_size_mb || '50'}
                  onChange={(e) => setSettings({ ...settings, max_upload_size_mb: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Data Retention Period (Days)</label>
                <input
                  type="text"
                  value={settings.data_retention_days || '180'}
                  onChange={(e) => setSettings({ ...settings, data_retention_days: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white font-mono"
                />
              </div>
            </div>

            <div className="pt-4 border-t border-slate-800">
              <button
                type="submit"
                className="px-5 py-2.5 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-cyan-500/20"
              >
                <Save className="w-4 h-4" /> Save Configuration Settings
              </button>
            </div>
          </form>
        )}

        {/* Tab 4: Alert Center */}
        {activeTab === 'alerts' && (
          <div className="bg-slate-900/80 rounded-xl border border-slate-800 p-5 space-y-4 backdrop-blur-md">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" /> Operational & Security Alert Center
            </h3>

            <div className="space-y-3 font-mono text-xs">
              <div className="bg-slate-950 p-4 rounded-xl border border-rose-500/30 flex items-center justify-between">
                <div className="space-y-1">
                  <span className="px-2 py-0.5 bg-rose-500/10 text-rose-400 font-bold rounded">UNAUTHORIZED ENTRY ATTEMPT</span>
                  <p className="text-white font-sans text-xs">Unregistered truck plate <span className="font-mono text-cyan-400">MH12AB9999</span> attempted entry at Gate North 01</p>
                  <span className="text-[10px] text-slate-500">10 minutes ago</span>
                </div>
                <button className="px-3 py-1.5 bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 rounded-lg text-xs font-bold font-sans hover:bg-emerald-500/30">
                  Resolve Alert
                </button>
              </div>

              <div className="bg-slate-950 p-4 rounded-xl border border-amber-500/30 flex items-center justify-between">
                <div className="space-y-1">
                  <span className="px-2 py-0.5 bg-amber-500/10 text-amber-400 font-bold rounded">LOW CONFIDENCE WARNING</span>
                  <p className="text-white font-sans text-xs">OCR confidence 64% on vehicle at East Gate 03</p>
                  <span className="text-[10px] text-slate-500">25 minutes ago</span>
                </div>
                <button className="px-3 py-1.5 bg-slate-800 text-slate-300 border border-slate-700 rounded-lg text-xs font-bold font-sans hover:bg-slate-700">
                  Acknowledge
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
