import React from 'react';
import { Shield, Search, Bell } from 'lucide-react';

export default function Header({ title, subtitle }) {
  return (
    <header className="h-16 bg-white border-b border-[#c8d8e4] sticky top-0 z-20 px-6 flex items-center justify-between shadow-sm">
      <div>
        <h1 className="text-lg font-bold text-[#0f2931] tracking-tight font-sans">{title}</h1>
        {subtitle && <p className="text-xs text-[#2b6777] font-medium font-sans">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {/* Global Search Bar */}
        <div className="relative hidden md:block">
          <Search className="w-4 h-4 text-[#2b6777] absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search plates, vehicles..."
            className="pl-9 pr-4 py-2 bg-[#f8fafc] border border-[#c8d8e4] rounded-full text-xs font-medium text-[#0f2931] placeholder-[#4d6e78] focus:outline-none focus:border-[#52ab98] focus:ring-2 focus:ring-[#52ab98]/30 w-64 transition-all"
          />
        </div>

        {/* System Status Pill */}
        <div className="flex items-center gap-2 px-3.5 py-1.5 bg-[#f0f6f8] border border-[#c8d8e4] rounded-full text-xs font-bold text-[#2b6777]">
          <Shield className="w-3.5 h-3.5 text-[#52ab98]" />
          <span className="text-[11px] font-sans">Gate Engine Active</span>
        </div>

        {/* Notifications Icon */}
        <button className="w-9 h-9 rounded-full bg-[#f0f6f8] border border-[#c8d8e4] flex items-center justify-center text-[#2b6777] hover:bg-[#c8d8e4]/50 transition-colors">
          <Bell className="w-4 h-4" />
        </button>

        {/* Profile Avatar */}
        <div className="w-9 h-9 rounded-full bg-[#2b6777] text-white flex items-center justify-center font-bold text-xs shadow-sm shadow-[#2b6777]/30 ring-2 ring-[#c8d8e4]">
          SA
        </div>
      </div>
    </header>
  );
}
