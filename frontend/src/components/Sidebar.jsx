import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Building2, 
  Truck, 
  CreditCard, 
  UserCheck, 
  Video, 
  Camera, 
  Calendar, 
  Activity, 
  ShieldAlert, 
  FileText, 
  LayoutDashboard,
  Users,
  Zap,
  Eye,
  FileCheck,
  Settings,
  ShieldCheck,
  CheckCircle2,
  Lock,
  Edit3,
  Sliders,
  Clock,
  AlertTriangle,
  Archive,
  Database,
  Gauge
} from 'lucide-react';

const navigationGroups = [
  {
    title: 'Master Data & AI',
    items: [
      { name: 'Transporters', path: '/transporters', icon: Building2 },
      { name: 'Vehicle Master', path: '/vehicles', icon: Truck },
      { name: 'Vehicle Plates', path: '/vehicle-plates', icon: CreditCard },
      { name: 'Drivers', path: '/drivers', icon: UserCheck },
      { name: 'AI Recognition', path: '/vehicle-recognition', icon: Zap },
      { name: 'Manual Review Queue', path: '/manual-review', icon: Edit3 },
    ]
  },
  {
    title: 'Gate & Operations',
    items: [
      { name: 'Gate Management', path: '/gates', icon: Video },
      { name: 'Trip Engine', path: '/trips', icon: Calendar },
      { name: 'Live Control Room', path: '/live-gate', icon: Activity },
      { name: 'Entry/Exit Logs', path: '/entry-exit', icon: Eye },
    ]
  },
  {
    title: 'Data Engineering Pipeline',
    items: [
      { name: 'Pipeline Dashboard', path: '/pipeline-dashboard', icon: Sliders },
      { name: 'Daily Summaries', path: '/daily-summary', icon: Calendar },
      { name: 'Gate Summaries', path: '/gate-summary', icon: Video },
      { name: 'Late Arrival Scans', path: '/late-arrivals', icon: Clock },
      { name: 'Overstay Monitor', path: '/overstay', icon: AlertTriangle },
      { name: 'Archive Manager', path: '/archive-manager', icon: Archive },
      { name: 'OCR Feedback Dataset', path: '/ocr-feedback', icon: Database },
    ]
  },
  {
    title: 'Authorization & Security',
    items: [
      { name: 'Auth Engine Dashboard', path: '/authorization-dashboard', icon: ShieldCheck },
      { name: 'Vehicle Whitelist', path: '/whitelist', icon: CheckCircle2 },
      { name: 'Security Watchlist', path: '/watchlist', icon: ShieldAlert },
      { name: 'Gate Decisions Log', path: '/gate-decisions', icon: Lock },
    ]
  },
  {
    title: 'Enterprise Admin & Analytics',
    items: [
      { name: 'Analytics Dashboard', path: '/analytics', icon: LayoutDashboard },
      { name: 'Performance Benchmarks', path: '/performance-dashboard', icon: Gauge },
      { name: 'Industrial Reports', path: '/reports', icon: FileText },
      { name: 'Users & RBAC', path: '/users', icon: Users },
      { name: 'Audit Trail Logs', path: '/audit-logs', icon: FileCheck },
      { name: 'System & Health', path: '/system-health', icon: Settings },
    ]
  }
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col h-screen sticky top-0 z-30 font-sans">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center bg-opacity-20 justify-center shadow-lg shadow-cyan-500/20 ring-1 ring-cyan-400/30">
          <Truck className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-bold text-white tracking-wide text-sm leading-tight">ENTERPRISE ANPR</h1>
          <p className="text-xs text-cyan-400 font-mono">Trip Platform v3.5</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto p-4 space-y-6">
        {navigationGroups.map((group, idx) => (
          <div key={idx} className="space-y-1">
            <h2 className="px-3 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              {group.title}
            </h2>
            <div className="mt-2 space-y-1">
              {group.items.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) =>
                      `flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                        isActive
                          ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm'
                          : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                      }`
                    }
                  >
                    <div className="flex items-center gap-2.5">
                      <Icon className="w-4 h-4" />
                      <span>{item.name}</span>
                    </div>
                  </NavLink>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Footer System Info */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/50">
        <div className="flex items-center gap-2 text-xs text-emerald-400 font-mono">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Data Pipeline Active</span>
        </div>
        <p className="text-[10px] text-slate-500 mt-1">Deduplication / Archival / OCR</p>
      </div>
    </aside>
  );
}
