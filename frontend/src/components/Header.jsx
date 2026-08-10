import React from 'react';
import { Bell, Shield, User, Search } from 'lucide-react';

export default function Header({ title, subtitle }) {
  return (
    <header className="h-16 bg-slate-900/80 border-b border-slate-800 backdrop-blur-md sticky top-0 z-20 px-6 flex items-center justify-between">
      <div>
        <h1 className="text-lg font-bold text-white tracking-wide">{title}</h1>
        {subtitle && <p className="text-xs text-slate-400">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {/* Global Search Bar */}
        <div className="relative hidden md:block">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search plates, vehicles..."
            className="pl-9 pr-4 py-1.5 bg-slate-800/80 border border-slate-700/60 rounded-lg text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 w-64 transition-all"
          />
        </div>

        {/* System Status Pill */}
        <div className="flex items-center gap-2 px-3 py-1 bg-slate-800/60 border border-slate-700/40 rounded-full text-xs text-slate-300">
          <Shield className="w-3.5 h-3.5 text-cyan-400" />
          <span className="font-mono text-[11px]">Gate Engine Active</span>
        </div>

        {/* Profile Avatar */}
        <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 font-bold text-xs">
          SA
        </div>
      </div>
    </header>
  );
}
