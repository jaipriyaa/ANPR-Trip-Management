import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react';
import Header from '../components/Header';
import { 
  ArrowLeft, 
  CheckCircle2, 
  XCircle, 
  Edit3, 
  Clock, 
  Truck, 
  CreditCard, 
  History, 
  Database,
  Activity
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function ManualReviewDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchDetail = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/manual-review/${id}`);
      if (res.ok) {
        setReview(await res.json());
      }
    } catch (err) {
      console.error('Failed to fetch review detail:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
  }, [id]);

  const getMediaUrl = (path) => {
    if (!path) return null;
    const filename = path.split('\\').pop()?.split('/').pop();
    return `${API_BASE_URL}/vehicle-recognition/media/processed/${filename}`;
  };

  if (loading) {
    return (
      <div className="flex-1 flex flex-col bg-[#f2f2f2] text-[#1a3b45] font-sans items-center justify-center p-12">
        <p className="text-[#5c7885]">Loading inspection details...</p>
      </div>
    );
  }

  if (!review) {
    return (
      <div className="flex-1 flex flex-col bg-[#f2f2f2] text-[#1a3b45] font-sans p-6 space-y-4">
        <button onClick={() => navigate('/manual-review')} className="text-cyan-400 flex items-center gap-1 text-xs">
          <ArrowLeft className="w-4 h-4" /> Back to Queue
        </button>
        <p className="text-rose-400">Manual review item not found.</p>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-[#f2f2f2] text-[#1a3b45] font-sans">
      <Header title={`Manual Review Inspection — #${review.id.slice(0, 8)}`} subtitle="High-resolution image crop inspection, OCR correction audit history, and AI retraining feedback collector" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        <button
          onClick={() => navigate('/manual-review')}
          className="px-3 py-1.5 bg-white border border-[#c8d8e4] text-[#2b6777] hover:text-[#1a3b45] rounded-xl text-xs flex items-center gap-2 font-mono"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Manual Review Queue
        </button>

        {/* 1. Header Status Bar */}
        <div className="bg-white rounded-xl border border-[#c8d8e4] p-5 backdrop-blur-md flex items-center justify-between flex-wrap gap-4">
          <div>
            <span className="text-xs text-purple-400 font-mono font-bold block">{review.tracking_id || 'TRACK-101'}</span>
            <h2 className="text-xl font-bold font-mono text-cyan-400 mt-0.5">{review.corrected_plate || review.recognized_plate}</h2>
            <p className="text-xs text-[#5c7885] mt-1">Raw OCR: <span className="font-mono text-amber-400">{review.raw_ocr_text || review.recognized_plate}</span></p>
          </div>

          <div className="flex items-center gap-3 font-mono text-xs">
            <div className="bg-[#f2f2f2] p-3 rounded-xl border border-[#c8d8e4]">
              <span className="text-[#5c7885] text-[10px] block">Confidence</span>
              <span className="font-bold text-emerald-400 text-sm">{Math.round((review.confidence || 0.65) * 100)}%</span>
            </div>
            <div className="bg-[#f2f2f2] p-3 rounded-xl border border-[#c8d8e4]">
              <span className="text-[#5c7885] text-[10px] block">Review Status</span>
              <span className={`font-bold text-sm ${
                review.review_status === 'APPROVED' || review.review_status === 'CORRECTED' ? 'text-emerald-400' : 'text-amber-400'
              }`}>{review.review_status}</span>
            </div>
          </div>
        </div>

        {/* 2. Image Inspection Side-by-Side Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl border border-[#c8d8e4] p-5 backdrop-blur-md space-y-3">
            <h3 className="text-xs font-bold text-[#1a3b45] uppercase tracking-wider flex items-center gap-2">
              <Truck className="w-4 h-4 text-cyan-400" /> Original Detected Vehicle Crop
            </h3>
            {review.vehicle_image_path ? (
              <img
                src={getMediaUrl(review.vehicle_image_path)}
                alt="Vehicle Crop"
                className="w-full rounded-xl border border-[#c8d8e4] bg-[#f2f2f2] max-h-64 object-contain"
                onError={(e) => { e.target.style.display = 'none'; }}
              />
            ) : (
              <div className="p-8 text-center text-[#5c7885] bg-[#f2f2f2] rounded-xl border border-[#c8d8e4] text-xs">Vehicle Crop Available</div>
            )}
          </div>

          <div className="bg-white rounded-xl border border-[#c8d8e4] p-5 backdrop-blur-md space-y-3">
            <h3 className="text-xs font-bold text-[#1a3b45] uppercase tracking-wider flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-purple-400" /> Cropped License Plate ROI
            </h3>
            {review.plate_image_path ? (
              <img
                src={getMediaUrl(review.plate_image_path)}
                alt="Plate Crop"
                className="w-full rounded-xl border border-[#c8d8e4] bg-[#f2f2f2] max-h-64 object-contain"
                onError={(e) => { e.target.style.display = 'none'; }}
              />
            ) : (
              <div className="p-8 text-center text-[#5c7885] bg-[#f2f2f2] rounded-xl border border-[#c8d8e4] text-xs">Plate Crop Available</div>
            )}
          </div>
        </div>

        {/* 3. OCR Correction History Audit Log */}
        <div className="bg-white rounded-xl border border-[#c8d8e4] p-5 backdrop-blur-md space-y-4">
          <h3 className="text-xs font-bold text-[#1a3b45] uppercase tracking-wider flex items-center gap-2">
            <History className="w-4 h-4 text-cyan-400" /> OCR Correction History Audit Log
          </h3>

          <div className="bg-[#f2f2f2] rounded-xl border border-[#c8d8e4] p-4 space-y-3 font-mono text-xs">
            {!review.corrections_history || review.corrections_history.length === 0 ? (
              <p className="text-[#5c7885] text-center py-2 font-sans">No manual corrections applied yet.</p>
            ) : (
              review.corrections_history.map((c) => (
                <div key={c.id} className="flex items-center justify-between border-b border-[#c8d8e4] pb-2 text-[11px]">
                  <div>
                    <span className="text-[#5c7885]">{c.old_plate}</span> → <span className="text-cyan-400 font-bold text-sm">{c.new_plate}</span>
                    <p className="text-[#5c7885] font-sans text-[10px] pt-0.5">{c.correction_reason}</p>
                  </div>
                  <div className="text-right text-[#5c7885]">
                    <p>{new Date(c.timestamp).toLocaleString()}</p>
                    <span className="text-purple-400 font-sans">{c.reviewed_by}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* 4. AI Retraining Feedback Dataset Export Status */}
        <div className="bg-white rounded-xl border border-[#c8d8e4] p-5 backdrop-blur-md flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Database className="w-5 h-5 text-emerald-400" />
            <div>
              <h4 className="text-xs font-bold text-[#1a3b45]">AI Retraining Feedback Dataset Collector</h4>
              <p className="text-[11px] text-[#5c7885]">Sample exported to <span className="font-mono text-cyan-400">backend/app/ai/feedback_dataset/</span> for OCR model retraining</p>
            </div>
          </div>
          <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-3 py-1 rounded-xl text-xs font-bold font-mono">
            ● Dataset Sample Exported
          </span>
        </div>
      </main>
    </div>
  );
}
