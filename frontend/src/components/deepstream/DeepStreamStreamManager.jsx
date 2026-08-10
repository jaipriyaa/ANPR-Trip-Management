import React, { useState, useEffect } from 'react';
import { Cpu, Video, Plus, Trash2, Activity, Zap, Layers, RefreshCw } from 'lucide-react';

export default function DeepStreamStreamManager() {
  const [streams, setStreams] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    rtsp_url: '',
    gate_id: 'GATE-ENTRY-01',
    camera_type: 'GATE_IN'
  });

  const fetchDeepStreamData = async () => {
    try {
      const [streamsRes, metricsRes] = await Promise.all([
        fetch('/api/v1/deepstream/streams'),
        fetch('/api/v1/deepstream/metrics')
      ]);
      if (streamsRes.ok && metricsRes.ok) {
        const streamsData = await streamsRes.json();
        const metricsData = await metricsRes.json();
        setStreams(streamsData);
        setMetrics(metricsData);
      }
    } catch (err) {
      console.error('Failed to load DeepStream metrics', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDeepStreamData();
    const interval = setInterval(fetchDeepStreamData, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleAddStream = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/v1/deepstream/streams', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (res.ok) {
        setShowAddModal(false);
        setFormData({ name: '', rtsp_url: '', gate_id: 'GATE-ENTRY-01', camera_type: 'GATE_IN' });
        fetchDeepStreamData();
      }
    } catch (err) {
      console.error('Failed to add RTSP stream', err);
    }
  };

  const handleRemoveStream = async (streamId) => {
    try {
      const res = await fetch(`/api/v1/deepstream/streams/${streamId}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        fetchDeepStreamData();
      }
    } catch (err) {
      console.error('Failed to remove stream', err);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-2xl text-slate-100 mb-6">
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-br from-emerald-500 to-teal-700 rounded-lg text-white shadow-lg shadow-emerald-500/20">
            <Zap className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-50 flex items-center gap-2">
              NVIDIA DeepStream 7.x Hardware Accelerator
              <span className="px-2.5 py-0.5 text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-full">
                ACTIVE
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              NVMM Hardware Muxing • NvDCF 3D Tracking • NVDSAnalytics ROI Rules
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchDeepStreamData}
            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors"
            title="Refresh metrics"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg shadow-md transition-all"
          >
            <Plus className="w-4 h-4" />
            Add RTSP Stream
          </button>
        </div>
      </div>

      {/* Hardware Performance Metrics Grid */}
      {metrics && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 my-4">
          <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-3">
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span>Pipeline Throughput</span>
              <Activity className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <div className="text-xl font-bold text-emerald-400">{metrics.total_throughput_fps} <span className="text-xs font-normal text-slate-400">FPS</span></div>
          </div>

          <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-3">
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span>GPU VRAM Memory</span>
              <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            </div>
            <div className="text-xl font-bold text-cyan-400">{metrics.gpu_memory_used_mb} <span className="text-xs font-normal text-slate-400">MB</span></div>
          </div>

          <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-3">
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span>Inference Latency</span>
              <Zap className="w-3.5 h-3.5 text-amber-400" />
            </div>
            <div className="text-xl font-bold text-amber-400">{metrics.latency_ms} <span className="text-xs font-normal text-slate-400">ms</span></div>
          </div>

          <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-3">
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span>Active Streams</span>
              <Layers className="w-3.5 h-3.5 text-indigo-400" />
            </div>
            <div className="text-xl font-bold text-indigo-400">{metrics.active_streams} <span className="text-xs font-normal text-slate-400">Feeds</span></div>
          </div>
        </div>
      )}

      {/* Active RTSP Feeds List */}
      <div className="mt-4">
        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
          Active Dynamic Camera Streams ({streams.length})
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {streams.map((stream) => (
            <div
              key={stream.id}
              className="bg-slate-950/80 border border-slate-800 rounded-lg p-3.5 flex items-center justify-between hover:border-slate-700 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="p-2 bg-slate-800 text-emerald-400 rounded-md">
                  <Video className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-slate-100 flex items-center gap-2">
                    {stream.name}
                    <span className="px-2 py-0.5 text-[10px] bg-slate-800 text-slate-300 rounded font-mono">
                      {stream.id}
                    </span>
                  </div>
                  <div className="text-xs text-slate-400 font-mono truncate max-w-xs mt-0.5">
                    {stream.rtsp_url}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="text-right hidden sm:block">
                  <div className="text-xs font-semibold text-emerald-400">{stream.fps} FPS</div>
                  <div className="text-[10px] text-slate-400">{stream.camera_type}</div>
                </div>
                <button
                  onClick={() => handleRemoveStream(stream.id)}
                  className="p-1.5 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 rounded-md transition-colors"
                  title="Remove stream"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Add Stream Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 w-full max-w-md shadow-2xl">
            <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
              <Plus className="w-5 h-5 text-emerald-400" />
              Add Dynamic RTSP Source (DeepStream 7.x)
            </h3>
            <form onSubmit={handleAddStream} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">Camera Stream Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. South Gate Secondary Cam"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-100 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">RTSP Stream URL</label>
                <input
                  type="text"
                  required
                  placeholder="rtsp://admin:pass@192.168.1.120:554/live"
                  value={formData.rtsp_url}
                  onChange={(e) => setFormData({ ...formData, rtsp_url: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-100 font-mono focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Gate Designation</label>
                  <input
                    type="text"
                    value={formData.gate_id}
                    onChange={(e) => setFormData({ ...formData, gate_id: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-100 focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Stream Type</label>
                  <select
                    value={formData.camera_type}
                    onChange={(e) => setFormData({ ...formData, camera_type: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-100 focus:outline-none focus:border-emerald-500"
                  >
                    <option value="GATE_IN">GATE_IN (Entry)</option>
                    <option value="GATE_OUT">GATE_OUT (Exit)</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-lg hover:bg-slate-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-500 transition-colors"
                >
                  Add Stream to Muxer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
