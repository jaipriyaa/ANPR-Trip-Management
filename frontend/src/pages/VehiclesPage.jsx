import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getVehicles, getTransporters, createVehicle, updateVehicle, deleteVehicle } from '../api/masterData';
import Header from '../components/Header';
import Modal from '../components/Modal';
import { Plus, Search, Truck, ShieldAlert, CheckCircle2, XCircle, Trash2, Edit, Tag, Weight } from 'lucide-react';

export default function VehiclesPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [transporterFilter, setTransporterFilter] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    vehicle_number: '',
    vehicle_type: 'Truck',
    make_model: '',
    color: '',
    capacity_tons: '',
    transporter_id: '',
    is_active: true,
    is_blacklisted: false,
  });
  const [errorMsg, setErrorMsg] = useState('');

  // Fetch Vehicles & Transporters
  const { data, isLoading } = useQuery({
    queryKey: ['vehicles', search, transporterFilter],
    queryFn: () => getVehicles({ 
      search, 
      transporter_id: transporterFilter || undefined,
      limit: 50 
    }),
  });

  const { data: transportersData } = useQuery({
    queryKey: ['transporters-options'],
    queryFn: () => getTransporters({ limit: 100 }),
  });

  // Save Mutation
  const saveMutation = useMutation({
    mutationFn: (payload) => {
      const formatted = {
        ...payload,
        capacity_tons: payload.capacity_tons ? parseFloat(payload.capacity_tons) : null,
        transporter_id: payload.transporter_id || null,
      };
      if (editingId) {
        return updateVehicle(editingId, formatted);
      }
      return createVehicle(formatted);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicles'] });
      closeModal();
    },
    onError: (err) => {
      console.error('[VehiclesPage] Save error:', err);
      setErrorMsg(err.message);
    },
  });

  // Delete Mutation
  const deleteMutation = useMutation({
    mutationFn: (id) => deleteVehicle(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicles'] });
    },
  });

  const openCreateModal = () => {
    setEditingId(null);
    setFormData({
      vehicle_number: '',
      vehicle_type: 'Truck',
      make_model: '',
      color: '',
      capacity_tons: '',
      transporter_id: '',
      is_active: true,
      is_blacklisted: false,
    });
    setErrorMsg('');
    setIsModalOpen(true);
  };

  const openEditModal = (item) => {
    setEditingId(item.id);
    setFormData({
      vehicle_number: item.vehicle_number,
      vehicle_type: item.vehicle_type || 'Truck',
      make_model: item.make_model || '',
      color: item.color || '',
      capacity_tons: item.capacity_tons || '',
      transporter_id: item.transporter_id || '',
      is_active: item.is_active,
      is_blacklisted: item.is_blacklisted,
    });
    setErrorMsg('');
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingId(null);
    setErrorMsg('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setErrorMsg('');
    saveMutation.mutate(formData);
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-[#f2f2f2]">
      <Header 
        title="Vehicle Master" 
        subtitle="Fleet vehicle registration, ANPR plate mapping, and blacklists" 
      />

      <main className="flex-1 p-6 space-y-6 max-w-7xl mx-auto w-full">
        {/* Top Controls */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white p-4 rounded-xl border border-[#c8d8e4] backdrop-blur-md">
          <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
            {/* Search */}
            <div className="relative w-full sm:w-64">
              <Search className="w-4 h-4 text-[#5c7885] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search vehicle number..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-9 pr-4 py-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-lg text-xs text-[#1a3b45] placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-all"
              />
            </div>

            {/* Transporter Filter */}
            <select
              value={transporterFilter}
              onChange={(e) => setTransporterFilter(e.target.value)}
              className="px-3 py-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-lg text-xs text-[#2b6777] focus:outline-none focus:border-cyan-500"
            >
              <option value="">All Transporters</option>
              {transportersData?.items?.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.company_name} ({t.code})
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={openCreateModal}
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-[#1a3b45] rounded-lg text-xs font-semibold shadow-lg shadow-cyan-600/20 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Add Vehicle</span>
          </button>
        </div>

        {/* Vehicles Table */}
        <div className="bg-white rounded-xl border border-[#c8d8e4] overflow-hidden shadow-xl backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-white text-[#5c7885] font-mono text-[11px] uppercase tracking-wider border-b border-[#c8d8e4]">
                <tr>
                  <th className="px-6 py-3.5">Vehicle Plate</th>
                  <th className="px-6 py-3.5">Type & Model</th>
                  <th className="px-6 py-3.5">Transporter</th>
                  <th className="px-6 py-3.5">Capacity</th>
                  <th className="px-6 py-3.5">Security & Status</th>
                  <th className="px-6 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-[#2b6777]">
                {isLoading ? (
                  <tr>
                    <td colSpan="6" className="px-6 py-12 text-center text-[#5c7885]">
                      Loading vehicle fleet...
                    </td>
                  </tr>
                ) : data?.items?.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="px-6 py-12 text-center text-[#5c7885]">
                      No vehicles found. Click "Add Vehicle" to register one.
                    </td>
                  </tr>
                ) : (
                  data?.items?.map((item) => (
                    <tr key={item.id} className="hover:bg-[#f0f6f8] transition-colors">
                      <td className="px-6 py-4 font-mono font-bold text-amber-400">
                        <div className="inline-flex items-center gap-2 px-2.5 py-1 bg-[#f2f2f2] border border-[#c8d8e4] rounded-md shadow-inner">
                          <Tag className="w-3.5 h-3.5 text-amber-400" />
                          <span>{item.vehicle_number}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="font-medium text-[#1a3b45]">{item.vehicle_type}</div>
                        <div className="text-[11px] text-[#5c7885]">{item.make_model || 'Standard Spec'}</div>
                      </td>
                      <td className="px-6 py-4 text-[#2b6777] font-medium">
                        {item.transporter ? item.transporter.company_name : <span className="text-[#5c7885] italic">Unassigned</span>}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-1 text-[#5c7885]">
                          <Weight className="w-3.5 h-3.5 text-[#5c7885]" />
                          <span>{item.capacity_tons ? `${item.capacity_tons} Tons` : 'N/A'}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 space-x-2">
                        {item.is_blacklisted && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/40 animate-pulse">
                            <ShieldAlert className="w-3 h-3" /> Blacklisted
                          </span>
                        )}
                        {item.is_active ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            Active
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-[#e8eff4] text-[#5c7885]">
                            Inactive
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-right space-x-2">
                        <button
                          onClick={() => openEditModal(item)}
                          className="p-1.5 text-[#5c7885] hover:text-cyan-400 hover:bg-[#e8eff4] rounded-lg transition-colors"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => {
                            if (confirm(`Delete vehicle ${item.vehicle_number}?`)) {
                              deleteMutation.mutate(item.id);
                            }
                          }}
                          className="p-1.5 text-[#5c7885] hover:text-rose-400 hover:bg-[#e8eff4] rounded-lg transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={closeModal}
        title={editingId ? 'Edit Vehicle' : 'Register Vehicle'}
      >
        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {errorMsg && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-400">
              {errorMsg}
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-[#5c7885] mb-1 font-medium">Vehicle Number *</label>
              <input
                type="text"
                required
                placeholder="e.g. KA01AB1234"
                value={formData.vehicle_number}
                onChange={(e) => setFormData({ ...formData, vehicle_number: e.target.value.toUpperCase() })}
                className="w-full px-3 py-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-lg text-[#1a3b45] font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-[#5c7885] mb-1 font-medium">Vehicle Category</label>
              <select
                value={formData.vehicle_type}
                onChange={(e) => setFormData({ ...formData, vehicle_type: e.target.value })}
                className="w-full px-3 py-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-lg text-[#1a3b45] focus:outline-none focus:border-cyan-500"
              >
                <option value="Truck">Truck</option>
                <option value="Tanker">Tanker</option>
                <option value="Trailer">Trailer</option>
                <option value="LCV">LCV</option>
                <option value="Car">Car</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-[#5c7885] mb-1 font-medium">Make / Model</label>
              <input
                type="text"
                placeholder="Volvo FH16"
                value={formData.make_model}
                onChange={(e) => setFormData({ ...formData, make_model: e.target.value })}
                className="w-full px-3 py-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-lg text-[#1a3b45] focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-[#5c7885] mb-1 font-medium">Capacity (Tons)</label>
              <input
                type="number"
                step="0.1"
                placeholder="25.5"
                value={formData.capacity_tons}
                onChange={(e) => setFormData({ ...formData, capacity_tons: e.target.value })}
                className="w-full px-3 py-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-lg text-[#1a3b45] focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-[#5c7885] mb-1 font-medium">Assign Transporter</label>
            <select
              value={formData.transporter_id}
              onChange={(e) => setFormData({ ...formData, transporter_id: e.target.value })}
              className="w-full px-3 py-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-lg text-[#1a3b45] focus:outline-none focus:border-cyan-500"
            >
              <option value="">None (Independent Fleet)</option>
              {transportersData?.items?.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.company_name} ({t.code})
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-6 pt-2">
            <label className="flex items-center gap-2 text-[#2b6777]">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="rounded bg-[#f2f2f2] border-[#c8d8e4] text-cyan-600 focus:ring-cyan-500"
              />
              Active
            </label>
            <label className="flex items-center gap-2 text-rose-400 font-semibold">
              <input
                type="checkbox"
                checked={formData.is_blacklisted}
                onChange={(e) => setFormData({ ...formData, is_blacklisted: e.target.checked })}
                className="rounded bg-[#f2f2f2] border-[#c8d8e4] text-rose-600 focus:ring-rose-500"
              />
              Flag Blacklisted
            </label>
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-[#c8d8e4]">
            <button
              type="button"
              onClick={closeModal}
              className="px-4 py-2 bg-[#e8eff4] hover:bg-[#c8d8e4] text-[#2b6777] rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saveMutation.isPending}
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-[#1a3b45] font-semibold rounded-lg shadow-lg shadow-cyan-600/20 transition-all"
            >
              {saveMutation.isPending ? 'Saving...' : 'Save Vehicle'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
