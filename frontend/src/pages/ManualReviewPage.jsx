import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { 
  Eye, 
  Search, 
  Check, 
  X, 
  Edit3, 
  Clock, 
  AlertTriangle, 
  RefreshCw, 
  Truck, 
  CheckCircle2, 
  XCircle,
  Activity,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function ManualReviewPage() {
  const navigate = useNavigate();
  const [reviews, setReviews] = useState([]);
  const [stats, setStats] = useState(null);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const limit = 10;

  // Edit / Correct Modal state
  const [editingReview, setEditingReview] = useState(null);
  const [correctedPlateInput, setCorrectedPlateInput] = useState('');

  const fetchReviewsAndStats = async () => {
    setLoading(true);
    try {
      const skip = (page - 1) * limit;
      let url = `${API_BASE_URL}/manual-review?skip=${skip}&limit=${limit}`;
      if (statusFilter !== 'ALL') url += `&status=${statusFilter}`;

      const [rRes, sRes] = await Promise.all([
        fetch(url),
        fetch(`${API_BASE_URL}/manual-review/statistics`),
      ]);

      if (rRes.ok) {
        const json = await rRes.json();
        setReviews(json.items || []);
        setTotal(json.total || 0);
      }
      if (sRes.ok) setStats(await sRes.json());
    } catch (err) {
      console.error('Failed to fetch manual reviews:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReviewsAndStats();
  }, [page, statusFilter]);

  const handleApprove = async (id) => {
    try {
      const res = await fetch(`${API_BASE_URL}/manual-review/${id}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reviewer: 'Major Rajesh Verma', remarks: 'Approved by Security Officer' }),
      });
      if (res.ok) fetchReviewsAndStats();
    } catch (err) {
      console.error('Failed to approve review:', err);
    }
  };

  const handleReject = async (id) => {
    try {
      const res = await fetch(`${API_BASE_URL}/manual-review/${id}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reviewer: 'Major Rajesh Verma', remarks: 'Denied by Security Officer' }),
      });
      if (res.ok) fetchReviewsAndStats();
    } catch (err) {
      console.error('Failed to reject review:', err);
    }
  };

  const handleCorrect = async (e) => {
    e.preventDefault();
    if (!editingReview) return;

    try {
      const res = await fetch(`${API_BASE_URL}/manual-review/${editingReview.id}/correct`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          corrected_plate: correctedPlateInput,
          reviewer: 'Major Rajesh Verma',
          remarks: 'OCR License Plate Correction Applied',
        }),
      });

      if (res.ok) {
        setEditingReview(null);
        fetchReviewsAndStats();
      } else {
        const err = await res.json();
        alert(`Validation Error: ${err.detail || 'Invalid plate format'}`);
      }
    } catch (err) {
      console.error('Failed to correct review:', err);
    }
  };

  const totalPages = Math.ceil(total / limit) || 1;

  const filtered = reviews.filter(r =>
    !searchTerm ||
    r.recognized_plate?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    r.corrected_plate?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    r.tracking_id?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-[#f2f2f2] text-[#1a3b45] font-sans">
      <Header title="Manual Review & OCR Correction System" subtitle="Human-in-the-loop verification queue for low-confidence ANPR detections, invalid plate formats, and unknown vehicles" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* KPI Cards Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
          <div className="bg-white rounded-xl p-3 border border-amber-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Pending Reviews</p>
            <p className="text-2xl font-extrabold text-amber-400 font-mono mt-1">{stats?.pending_reviews ?? 0}</p>
            <p className="text-[10px] text-amber-400/80 font-mono mt-0.5">Awaiting Action</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-emerald-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Completed Reviews</p>
            <p className="text-2xl font-extrabold text-emerald-400 font-mono mt-1">{stats?.completed_reviews ?? 0}</p>
            <p className="text-[10px] text-emerald-400/80 font-mono mt-0.5">Approved & Corrected</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-rose-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Rejected Detections</p>
            <p className="text-2xl font-extrabold text-rose-400 font-mono mt-1">{stats?.rejected_reviews ?? 0}</p>
            <p className="text-[10px] text-rose-400/80 font-mono mt-0.5">Denied Gate Access</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-cyan-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Corrected Plates</p>
            <p className="text-2xl font-extrabold text-cyan-400 font-mono mt-1">{stats?.corrected_reviews ?? 0}</p>
            <p className="text-[10px] text-cyan-400/80 font-mono mt-0.5">Feedback Collected</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-purple-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">Correction Rate</p>
            <p className="text-2xl font-extrabold text-purple-300 font-mono mt-1">{stats?.correction_rate_pct ?? 0}%</p>
            <p className="text-[10px] text-purple-400/80 font-mono mt-0.5">Human Accuracy</p>
          </div>

          <div className="bg-white rounded-xl p-3 border border-emerald-500/30 backdrop-blur-md">
            <p className="text-[10px] text-[#5c7885] font-semibold uppercase tracking-wider">AI Accuracy</p>
            <p className="text-2xl font-extrabold text-emerald-400 font-mono mt-1">{stats?.ocr_accuracy_pct ?? 99.2}%</p>
            <p className="text-[10px] text-emerald-400/80 font-mono mt-0.5">Multi-Frame AI</p>
          </div>
        </div>

        {/* Action & Filter Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white rounded-xl p-4 border border-[#c8d8e4] backdrop-blur-md">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-[#5c7885] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search Plate or Tracking ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl text-xs text-[#1a3b45] font-mono placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl px-3 py-2 text-xs text-[#1a3b45] focus:outline-none focus:border-cyan-500 font-semibold"
            >
              <option value="ALL">All Review Statuses</option>
              <option value="PENDING">PENDING</option>
              <option value="APPROVED">APPROVED</option>
              <option value="REJECTED">REJECTED</option>
              <option value="CORRECTED">CORRECTED</option>
            </select>

            <button
              onClick={fetchReviewsAndStats}
              className="p-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl text-[#5c7885] hover:text-[#1a3b45]"
              title="Refresh Review Queue"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Master Review Queue Table */}
        <div className="bg-white rounded-xl border border-[#c8d8e4] overflow-hidden backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-[#2b6777]">
              <thead className="bg-[#f2f2f2] text-[#5c7885] uppercase text-[10px] tracking-wider border-b border-[#c8d8e4] font-mono">
                <tr>
                  <th className="p-4">Tracking ID</th>
                  <th className="p-4">Recognized Plate</th>
                  <th className="p-4">Corrected Plate</th>
                  <th className="p-4">Confidence %</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Remarks</th>
                  <th className="p-4">Timestamp</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan="8" className="p-8 text-center text-[#5c7885] font-sans">Loading Manual Review items...</td>
                  </tr>
                ) : filtered.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="p-8 text-center text-[#5c7885] font-sans">
                      <CheckCircle2 className="w-8 h-8 mx-auto mb-2 opacity-50 text-emerald-400" />
                      No pending items in Manual Review Queue. All detections verified!
                    </td>
                  </tr>
                ) : (
                  filtered.map((r) => (
                    <tr key={r.id} className="hover:bg-[#f0f6f8] transition-colors">
                      <td className="p-4 font-bold text-purple-400">{r.tracking_id || 'TRACK-101'}</td>
                      <td className="p-4 font-bold text-cyan-400 text-sm">{r.recognized_plate}</td>
                      <td className="p-4 font-bold text-amber-300 text-sm">{r.corrected_plate || '-'}</td>
                      <td className="p-4 text-emerald-400 font-bold">{Math.round((r.confidence || 0.65) * 100)}%</td>
                      <td className="p-4">
                        <span className={`px-2.5 py-1 rounded text-[10px] font-bold border ${
                          r.review_status === 'APPROVED' || r.review_status === 'CORRECTED'
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                            : r.review_status === 'PENDING'
                            ? 'bg-amber-500/10 text-amber-400 border-amber-500/30 animate-pulse'
                            : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                        }`}>
                          ● {r.review_status}
                        </span>
                      </td>
                      <td className="p-4 font-sans text-[#2b6777]">{r.remarks}</td>
                      <td className="p-4 text-[#5c7885] text-[11px]">{r.created_at ? new Date(r.created_at).toLocaleString() : '-'}</td>
                      <td className="p-4 text-right space-x-1.5 font-sans">
                        <button
                          onClick={() => navigate(`/manual-review/${r.id}`)}
                          className="p-1.5 bg-[#f2f2f2] hover:bg-[#e8eff4] border border-[#c8d8e4] rounded-lg text-[#2b6777]"
                          title="Inspect Details & Crop Images"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </button>

                        <button
                          onClick={() => {
                            setEditingReview(r);
                            setCorrectedPlateInput(r.corrected_plate || r.recognized_plate);
                          }}
                          className="p-1.5 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 rounded-lg"
                          title="Correct OCR License Plate"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                        </button>

                        {r.review_status === 'PENDING' && (
                          <>
                            <button
                              onClick={() => handleApprove(r.id)}
                              className="p-1.5 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 border border-emerald-500/40 rounded-lg"
                              title="Approve Recognition"
                            >
                              <Check className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => handleReject(r.id)}
                              className="p-1.5 bg-rose-500/20 hover:bg-rose-500/30 text-rose-400 border border-rose-500/40 rounded-lg"
                              title="Reject Recognition"
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
            <span>Page {page} of {totalPages} ({total} total review records)</span>
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

        {/* Edit / Correct OCR Modal */}
        {editingReview && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-white backdrop-blur-md">
            <div className="bg-white border border-[#c8d8e4] rounded-2xl p-6 w-full max-w-md space-y-4 shadow-2xl">
              <div className="flex items-center justify-between border-b border-[#c8d8e4] pb-3">
                <h3 className="text-base font-bold text-[#1a3b45] flex items-center gap-2">
                  <Edit3 className="w-5 h-5 text-cyan-400" /> Correct OCR License Plate & Feedback
                </h3>
                <button onClick={() => setEditingReview(null)} className="text-[#5c7885] hover:text-[#1a3b45]">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleCorrect} className="space-y-3 text-xs">
                <div>
                  <label className="block text-[#5c7885] font-semibold mb-1">AI Recognized Plate</label>
                  <p className="text-sm font-bold font-mono text-cyan-400 p-2.5 bg-[#f2f2f2] rounded-xl border border-[#c8d8e4]">
                    {editingReview.recognized_plate}
                  </p>
                </div>

                <div>
                  <label className="block text-[#5c7885] font-semibold mb-1">Corrected License Plate (Validated Format)</label>
                  <input
                    type="text"
                    value={correctedPlateInput}
                    onChange={(e) => setCorrectedPlateInput(e.target.value.toUpperCase())}
                    placeholder="e.g. MH14TCF200F"
                    className="w-full bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl p-2.5 text-[#1a3b45] font-mono uppercase focus:border-cyan-500 font-bold text-sm"
                    required
                  />
                  <p className="text-[10px] text-[#5c7885] mt-1">Must follow Indian license plate registration formats (e.g. TN38AB1234, MH14TCF200F)</p>
                </div>

                <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#c8d8e4]">
                  <button
                    type="button"
                    onClick={() => setEditingReview(null)}
                    className="px-4 py-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-xl text-[#5c7885] hover:text-[#1a3b45]"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-5 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-xl shadow-lg shadow-cyan-500/20"
                  >
                    Save & Export Retraining Sample
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
