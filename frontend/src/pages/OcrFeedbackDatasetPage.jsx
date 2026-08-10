import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import { Database, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function OcrFeedbackDatasetPage() {
  const [dataset, setDataset] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const limit = 15;

  const fetchDataset = async () => {
    setLoading(true);
    try {
      const skip = (page - 1) * limit;
      const res = await fetch(`${API_BASE_URL}/ocr-feedback?skip=${skip}&limit=${limit}`);
      if (res.ok) {
        const json = await res.json();
        setDataset(json.items || []);
        setTotal(json.total || 0);
      }
    } catch (err) {
      console.error('Failed to fetch OCR feedback dataset:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDataset();
  }, [page]);

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-slate-950 text-slate-100 font-sans">
      <Header title="AI Retraining OCR Feedback Dataset" subtitle="Accumulated OCR ground truth sample pairs collected from human manual review corrections for deep learning retraining" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        <div className="flex items-center justify-between bg-slate-900/80 rounded-xl p-4 border border-slate-800 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <Database className="w-5 h-5 text-cyan-400" />
            <h2 className="text-sm font-bold text-white">OCR Ground Truth Dataset</h2>
          </div>

          <button
            onClick={fetchDataset}
            className="p-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-400 hover:text-white"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Master OCR Feedback Dataset Table */}
        <div className="bg-slate-900/80 rounded-xl border border-slate-800 overflow-hidden backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-mono">
                <tr>
                  <th className="p-4">Raw OCR Prediction</th>
                  <th className="p-4">Corrected Ground Truth</th>
                  <th className="p-4">Confidence %</th>
                  <th className="p-4">Source Queue</th>
                  <th className="p-4">Reviewer</th>
                  <th className="p-4">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan="6" className="p-8 text-center text-slate-500 font-sans">Loading OCR feedback dataset...</td>
                  </tr>
                ) : dataset.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="p-8 text-center text-slate-500 font-sans">No feedback dataset records accumulated yet.</td>
                  </tr>
                ) : (
                  dataset.map((item) => (
                    <tr key={item.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="p-4 text-amber-400 font-bold">{item.raw_ocr_text}</td>
                      <td className="p-4 text-cyan-400 font-bold text-sm">{item.corrected_ocr_text}</td>
                      <td className="p-4 text-emerald-400 font-bold">{Math.round((item.confidence || 0.65) * 100)}%</td>
                      <td className="p-4 text-purple-300">{item.correction_source}</td>
                      <td className="p-4 text-slate-300 font-sans">{item.reviewer}</td>
                      <td className="p-4 text-slate-400">{item.created_at ? new Date(item.created_at).toLocaleString() : '-'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="p-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400 font-sans">
            <span>Page {page} of {totalPages} ({total} total feedback records)</span>
            <div className="flex items-center gap-2 font-mono">
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
      </main>
    </div>
  );
}
