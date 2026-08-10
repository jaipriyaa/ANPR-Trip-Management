import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import TransportersPage from './pages/TransportersPage';
import VehiclesPage from './pages/VehiclesPage';
import DriversPage from './pages/DriversPage';
import VehiclePlatesPage from './pages/VehiclePlatesPage';
import VehicleRecognitionPage from './pages/VehicleRecognitionPage';
import GateManagementPage from './pages/GateManagementPage';
import EntryExitLogPage from './pages/EntryExitLogPage';
import LiveGateMonitorPage from './pages/LiveGateMonitorPage';
import TripsPage from './pages/TripsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import ReportsPage from './pages/ReportsPage';
import UsersPage from './pages/UsersPage';
import AuditLogsPage from './pages/AuditLogsPage';
import SystemHealthPage from './pages/SystemHealthPage';
import WhitelistPage from './pages/WhitelistPage';
import WatchlistPage from './pages/WatchlistPage';
import GateDecisionsPage from './pages/GateDecisionsPage';
import AuthorizationDashboardPage from './pages/AuthorizationDashboardPage';
import ManualReviewPage from './pages/ManualReviewPage';
import ManualReviewDetailPage from './pages/ManualReviewDetailPage';
import PipelineDashboardPage from './pages/PipelineDashboardPage';
import DailySummaryPage from './pages/DailySummaryPage';
import GateSummaryPage from './pages/GateSummaryPage';
import LateArrivalsPage from './pages/LateArrivalsPage';
import OverstayPage from './pages/OverstayPage';
import ArchiveManagerPage from './pages/ArchiveManagerPage';
import OcrFeedbackDatasetPage from './pages/OcrFeedbackDatasetPage';
import PerformanceDashboardPage from './pages/PerformanceDashboardPage';

export default function App() {
  return (
    <div className="flex min-h-screen bg-[#f2f2f2] text-[#1a3b45] selection:bg-[#52ab98] selection:text-white font-sans antialiased">
      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 bg-[#f2f2f2]">
        <Routes>
          <Route path="/" element={<Navigate to="/transporters" replace />} />
          <Route path="/transporters" element={<TransportersPage />} />
          <Route path="/vehicles" element={<VehiclesPage />} />
          <Route path="/vehicle-plates" element={<VehiclePlatesPage />} />
          <Route path="/drivers" element={<DriversPage />} />
          <Route path="/vehicle-recognition" element={<VehicleRecognitionPage />} />
          <Route path="/gates" element={<GateManagementPage />} />
          <Route path="/entry-exit" element={<EntryExitLogPage />} />
          <Route path="/live-gate" element={<LiveGateMonitorPage />} />
          <Route path="/trips" element={<TripsPage />} />
          
          {/* Phase 8 Administration Routes */}
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/dashboard" element={<Navigate to="/analytics" replace />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/users" element={<UsersPage />} />
          <Route path="/audit-logs" element={<AuditLogsPage />} />
          <Route path="/system-health" element={<SystemHealthPage />} />
          <Route path="/performance-dashboard" element={<PerformanceDashboardPage />} />

          {/* Phase 9 Authorization Engine Routes */}
          <Route path="/whitelist" element={<WhitelistPage />} />
          <Route path="/watchlist" element={<WatchlistPage />} />
          <Route path="/gate-decisions" element={<GateDecisionsPage />} />
          <Route path="/authorization-dashboard" element={<AuthorizationDashboardPage />} />

          {/* Phase 10 Manual Review & OCR Correction Routes */}
          <Route path="/manual-review" element={<ManualReviewPage />} />
          <Route path="/manual-review/:id" element={<ManualReviewDetailPage />} />

          {/* Phase 11 Data Engineering Pipeline Routes */}
          <Route path="/pipeline-dashboard" element={<PipelineDashboardPage />} />
          <Route path="/daily-summary" element={<DailySummaryPage />} />
          <Route path="/gate-summary" element={<GateSummaryPage />} />
          <Route path="/late-arrivals" element={<LateArrivalsPage />} />
          <Route path="/overstay" element={<OverstayPage />} />
          <Route path="/archive-manager" element={<ArchiveManagerPage />} />
          <Route path="/ocr-feedback" element={<OcrFeedbackDatasetPage />} />

          {/* Fallback Route */}
          <Route path="*" element={<Navigate to="/transporters" replace />} />
        </Routes>
      </div>
    </div>
  );
}
