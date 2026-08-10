import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import { 
  FileText, 
  Download, 
  Search, 
  Filter, 
  Calendar, 
  Building, 
  Truck, 
  CheckCircle2, 
  Clock, 
  ShieldAlert,
  FileType
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function ReportsPage() {
  const [reportType, setReportType] = useState('Daily Vehicle Report');
  const [exportFormat, setExportFormat] = useState('JSON');
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);

  const reportOptions = [
    'Daily Vehicle Report',
    'Weekly Report',
    'Monthly Report',
    'Trip Report',
    'Driver Report',
    'Transporter Report',
    'Gate Report',
    'Camera Report',
    'Recognition Accuracy Report',
    'Unauthorized Vehicle Report',
    'Vehicle Stay Duration Report',
    'Alerts Report',
  ];

  const fetchReport = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/admin/reports?report_type=${encodeURIComponent(reportType)}&export_format=${exportFormat}`);
      if (res.ok) {
        if (exportFormat === 'CSV') {
          const blob = await res.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `${reportType.replace(/\s+/g, '_')}.csv`;
          a.click();
        } else {
          const json = await res.json();
          setReportData(json);
        }
      }
    } catch (err) {
      console.error('Failed to generate report:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (exportFormat === 'JSON') {
      fetchReport();
    }
  }, [reportType]);

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-slate-950 text-slate-100 font-sans">
      <Header title="Industrial Reports & Data Export" subtitle="Configurable reporting engine for gate logs, trip compliance, accuracy audit, and Excel/CSV/PDF exports" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Action & Configuration Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900/80 rounded-xl p-4 border border-slate-800 backdrop-blur-md">
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <FileText className="w-5 h-5 text-cyan-400" />
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500 font-semibold"
            >
              {reportOptions.map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <button
              onClick={() => {
                setExportFormat('JSON');
                fetchReport();
              }}
              className="px-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-300 hover:text-white font-mono flex items-center gap-2"
            >
              <Search className="w-3.5 h-3.5" /> View Report Data
            </button>

            <button
              onClick={() => {
                setExportFormat('CSV');
                fetchReport();
              }}
              className="px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-cyan-500/20"
            >
              <Download className="w-4 h-4" /> Export CSV / Excel
            </button>
          </div>
        </div>

        {/* Report Preview Table */}
        <div className="bg-slate-900/80 rounded-xl border border-slate-800 overflow-hidden backdrop-blur-md space-y-4">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <FileType className="w-4 h-4 text-cyan-400" /> {reportType}
              </h3>
              <p className="text-xs text-slate-400">Generated on {reportData?.generated_at ? new Date(reportData.generated_at).toLocaleString() : 'Live'} | Total Records: {reportData?.total_records || 0}</p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-mono">
                <tr>
                  <th className="p-4">License Plate</th>
                  <th className="p-4">Vehicle Type</th>
                  <th className="p-4">Entry Gate</th>
                  <th className="p-4">Exit Gate</th>
                  <th className="p-4">Entry Time</th>
                  <th className="p-4">Stay Duration</th>
                  <th className="p-4">Transporter</th>
                  <th className="p-4">Driver</th>
                  <th className="p-4">Accuracy %</th>
                  <th className="p-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan="10" className="p-8 text-center text-slate-500 font-sans">Generating report data...</td>
                  </tr>
                ) : !reportData?.rows || reportData.rows.length === 0 ? (
                  <tr>
                    <td colSpan="10" className="p-8 text-center text-slate-500 font-sans">No report records found matching criteria.</td>
                  </tr>
                ) : (
                  reportData.rows.map((row, i) => (
                    <tr key={i} className="hover:bg-slate-800/40 transition-colors">
                      <td className="p-4 font-bold text-cyan-400">{row.plate_number}</td>
                      <td className="p-4 font-sans text-slate-300">{row.vehicle_type}</td>
                      <td className="p-4 font-mono text-purple-400">{row.entry_gate}</td>
                      <td className="p-4 font-mono text-slate-400">{row.exit_gate}</td>
                      <td className="p-4 text-[11px] text-slate-300">{row.entry_time ? new Date(row.entry_time).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' }) : '-'}</td>
                      <td className="p-4 text-amber-300 font-bold">{row.stay_duration}</td>
                      <td className="p-4 font-sans text-slate-300">{row.transporter}</td>
                      <td className="p-4 font-sans text-slate-300">{row.driver}</td>
                      <td className="p-4 font-mono text-emerald-400 font-bold">{row.confidence}</td>
                      <td className="p-4">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          row.status === 'INSIDE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-slate-800 text-slate-400'
                        }`}>
                          {row.status}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}
