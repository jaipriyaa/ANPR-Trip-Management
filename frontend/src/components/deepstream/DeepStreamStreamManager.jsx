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
    <div className="bg-white border border-[#c8d8e4] rounded-xl p-5 shadow-2xl text-[#1a3b45] mb-6">
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-[#c8d8e4]">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-br from-emerald-500 to-teal-700 rounded-lg text-[#1a3b45] shadow-lg shadow-emerald-500/20">
            <Zap className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-50 flex items-center gap-2">
              NVIDIA DeepStream 7.x Hardware Accelerator
              <span className="px-2.5 py-0.5 text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-full">
                ACTIVE
              </span>
            </h3>
            <p className="text-xs text-[#5c7885]">
              NVMM Hardware Muxing • NvDCF 3D Tracking • NVDSAnalytics ROI Rules
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchDeepStreamData}
            className="p-2 bg-[#e8eff4] hover:bg-[#c8d8e4] text-[#2b6777] rounded-lg transition-colors"
            title="Refresh metrics"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-[#1a3b45] text-xs font-semibold rounded-lg shadow-md transition-all"
          >
            <Plus className="w-4 h-4" />
            Add RTSP Stream
          </button>
        </div>
      </div>

      {/* Hardware Performance Metrics Grid */}
      {metrics && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 my-4">
          <div className="bg-white border border-[#c8d8e4] rounded-lg p-3">
            <div className="flex items-center justify-between text-xs text-[#5c7885] mb-1">
              <span>Pipeline Throughput</span>
              <Activity className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <div className="text-xl font-bold text-emerald-400">{metrics.total_throughput_fps} <span className="text-xs font-normal text-[#5c7885]">FPS</span></div>
          </div>

          <div className="bg-white border border-[#c8d8e4] rounded-lg p-3">
            <div className="flex items-center justify-between text-xs text-[#5c7885] mb-1">
              <span>GPU VRAM Memory</span>
              <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            </div>
            <div className="text-xl font-bold text-cyan-400">{metrics.gpu_memory_used_mb} <span className="text-xs font-normal text-[#5c7885]">MB</span></div>
          </div>

          <div className="bg-white border border-[#c8d8e4] rounded-lg p-3">
            <div className="flex items-center justify-between text-xs text-[#5c7885] mb-1">
              <span>Inference Latency</span>
              <Zap className="w-3.5 h-3.5 text-amber-400" />
            </div>
            <div className="text-xl font-bold text-amber-400">{metrics.latency_ms} <span className="text-xs font-normal text-[#5c7885]">ms</span></div>
          </div>

          <div className="bg-white border border-[#c8d8e4] rounded-lg p-3">
            <div className="flex items-center justify-between text-xs text-[#5c7885] mb-1">
              <span>Active Streams</span>
              <Layers className="w-3.5 h-3.5 text-indigo-400" />
            </div>
            <div className="text-xl font-bold text-indigo-400">{metrics.active_streams} <span className="text-xs font-normal text-[#5c7885]">Feeds</span></div>
          </div>
        </div>
      )}

      {/* Active RTSP Feeds List */}
      <div className="mt-4">
        <h4 className="text-xs font-semibold text-[#5c7885] uppercase tracking-wider mb-2">
          Active Dynamic Camera Streams ({streams.length})
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {streams.map((stream) => (
            <div
              key={stream.id}
              className="bg-white border border-[#c8d8e4] rounded-lg p-3.5 flex items-center justify-between hover:border-[#c8d8e4] transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="p-2 bg-[#e8eff4] text-emerald-400 rounded-md">
                  <Video className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-[#1a3b45] flex items-center gap-2">
                    {stream.name}
                    <span className="px-2 py-0.5 text-[10px] bg-[#e8eff4] text-[#2b6777] rounded font-mono">
                      {stream.id}
                    </span>
                  </div>
                  <div className="text-xs text-[#5c7885] font-mono truncate max-w-xs mt-0.5">
                    {stream.rtsp_url}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="text-right hidden sm:block">
                  <div className="text-xs font-semibold text-emerald-400">{stream.fps} FPS</div>
                  <div className="text-[10px] text-[#5c7885]">{stream.camera_type}</div>
                </div>
                <button
                  onClick={() => handleRemoveStream(stream.id)}
                  className="p-1.5 hover:bg-rose-500/20 text-[#5c7885] hover:text-rose-400 rounded-md transition-colors"
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
          <div className="bg-white border border-[#c8d8e4] rounded-xl p-6 w-full max-w-md shadow-2xl">
            <h3 className="text-base font-bold text-[#1a3b45] mb-4 flex items-center gap-2">
              <Plus className="w-5 h-5 text-emerald-400" />
              Add Dynamic RTSP Source (DeepStream 7.x)
            </h3>
            <form onSubmit={handleAddStream} className="space-y-4 text-xs">
              <div>
                <label className="block text-[#2b6777] font-medium mb-1">Camera Stream Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. South Gate Secondary Cam"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full bg-[#f2f2f2] border border-[#c8d8e4] rounded-lg p-2.5 text-[#1a3b45] focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-[#2b6777] font-medium mb-1">RTSP Stream URL</label>
                <input
                  type="text"
                  required
                  placeholder="rtsp://admin:pass@192.168.1.120:554/live"
                  value={formData.rtsp_url}
                  onChange={(e) => setFormData({ ...formData, rtsp_url: e.target.value })}
                  className="w-full bg-[#f2f2f2] border border-[#c8d8e4] rounded-lg p-2.5 text-[#1a3b45] font-mono focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[#2b6777] font-medium mb-1">Gate Designation</label>
                  <input
                    type="text"
                    value={formData.gate_id}
                    onChange={(e) => setFormData({ ...formData, gate_id: e.target.value })}
                    className="w-full bg-[#f2f2f2] border border-[#c8d8e4] rounded-lg p-2.5 text-[#1a3b45] focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-[#2b6777] font-medium mb-1">Stream Type</label>
                  <select
                    value={formData.camera_type}
                    onChange={(e) => setFormData({ ...formData, camera_type: e.target.value })}
                    className="w-full bg-[#f2f2f2] border border-[#c8d8e4] rounded-lg p-2.5 text-[#1a3b45] focus:outline-none focus:border-emerald-500"
                  >
                    <option value="GATE_IN">GATE_IN (Entry)</option>
                    <option value="GATE_OUT">GATE_OUT (Exit)</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-[#c8d8e4]">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 bg-[#e8eff4] text-[#2b6777] rounded-lg hover:bg-[#c8d8e4] transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-600 text-[#1a3b45] font-semibold rounded-lg hover:bg-emerald-500 transition-colors"
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
