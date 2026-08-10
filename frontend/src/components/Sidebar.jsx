import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Building2, 
  Truck, 
  CreditCard, 
  UserCheck, 
  Video, 
  Activity, 
  ShieldAlert, 
  FileText, 
  LayoutDashboard,
  Users,
  Zap,
  Eye,
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
  Gauge,
  CalendarDays
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
      { name: 'Trip Engine', path: '/trips', icon: CalendarDays },
      { name: 'Live Control Room', path: '/live-gate', icon: Activity },
      { name: 'Entry/Exit Logs', path: '/entry-exit', icon: Eye },
    ]
  },
  {
    title: 'Data Engineering Pipeline',
    items: [
      { name: 'Pipeline Dashboard', path: '/pipeline-dashboard', icon: Sliders },
      { name: 'Daily Summaries', path: '/daily-summary', icon: CalendarDays },
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
      { name: 'Audit Trail Logs', path: '/audit-logs', icon: ShieldCheck },
      { name: 'System & Health', path: '/system-health', icon: Settings },
    ]
  }
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-[#2b6777] text-white flex flex-col h-screen sticky top-0 z-30 font-sans shadow-xl border-r border-[#3d8294]/30">
      {/* Brand Header */}
      <div className="p-5 border-b border-[#3d8294]/40 flex items-center gap-3">
        <div className="w-10 h-10 rounded-2xl bg-[#52ab98] flex items-center justify-center shadow-lg shadow-[#52ab98]/30 ring-2 ring-[#c8d8e4]/40">
          <Truck className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-extrabold text-white tracking-wide text-sm leading-tight">ENTERPRISE ANPR</h1>
          <p className="text-xs text-[#c8d8e4] font-medium">Trip Platform v3.5</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto p-4 space-y-6">
        {navigationGroups.map((group, idx) => (
          <div key={idx} className="space-y-1">
            <h2 className="px-3 text-[11px] font-bold text-[#c8d8e4]/90 uppercase tracking-wider">
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
                      `flex items-center justify-between px-3.5 py-2.5 rounded-2xl text-xs font-semibold transition-all ${
                        isActive
                          ? 'bg-[#52ab98] text-white shadow-md shadow-[#52ab98]/30 ring-1 ring-white/20'
                          : 'text-[#e2ebf2] hover:text-white hover:bg-white/10'
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
      <div className="p-4 border-t border-[#3d8294]/40 bg-[#22525f]/60 rounded-b-none">
        <div className="flex items-center gap-2 text-xs font-bold">
          <span className="w-2.5 h-2.5 rounded-full bg-[#52ab98] animate-pulse shadow-sm shadow-[#52ab98]"></span>
          <span className="text-white">Data Pipeline Active</span>
        </div>
        <p className="text-[11px] text-[#c8d8e4]/80 mt-1">Deduplication / Archival / OCR</p>
      </div>
    </aside>
  );
}
