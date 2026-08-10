import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getVehiclePlates, getVehicles, createVehiclePlate, deleteVehiclePlate } from '../api/masterData';
import Header from '../components/Header';
import Modal from '../components/Modal';
import { Plus, Search, CreditCard, Tag, CheckCircle2, Trash2, Shield } from 'lucide-react';

export default function VehiclePlatesPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    vehicle_id: '',
    plate_number: '',
    plate_type: 'Standard',
    is_primary: false,
    is_active: true,
  });
  const [errorMsg, setErrorMsg] = useState('');

  // Fetch Plates & Vehicles
  const { data, isLoading } = useQuery({
    queryKey: ['vehicle-plates', search],
    queryFn: () => getVehiclePlates({ search, limit: 50 }),
  });

  const { data: vehiclesData } = useQuery({
    queryKey: ['vehicles-options'],
    queryFn: () => getVehicles({ limit: 100 }),
  });

  // Save Mutation
  const saveMutation = useMutation({
    mutationFn: (payload) => createVehiclePlate(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicle-plates'] });
      queryClient.invalidateQueries({ queryKey: ['vehicles'] });
      closeModal();
    },
    onError: (err) => {
      console.error('[VehiclePlatesPage] Save error:', err);
      setErrorMsg(err.message);
    },
  });

  // Delete Mutation
  const deleteMutation = useMutation({
    mutationFn: (id) => deleteVehiclePlate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicle-plates'] });
    },
  });

  const openCreateModal = () => {
    setFormData({
      vehicle_id: '',
      plate_number: '',
      plate_type: 'Standard',
      is_primary: false,
      is_active: true,
    });
    setErrorMsg('');
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setErrorMsg('');
  };

  const cleanPayload = (data) => Object.fromEntries(
    Object.entries(data).map(([k, v]) => [k, v === '' ? null : v])
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    setErrorMsg('');
    saveMutation.mutate(cleanPayload(formData));
  };

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-slate-950">
      <Header 
        title="Vehicle Plates Master" 
        subtitle="Manage ANPR optical recognition plate records & trailer mapping" 
      />

      <main className="flex-1 p-6 space-y-6 max-w-7xl mx-auto w-full">
        {/* Control Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900/60 p-4 rounded-xl border border-slate-800 backdrop-blur-md">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search plate registration string..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-all"
            />
          </div>

          <button
            onClick={openCreateModal}
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-cyan-600/20 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Map Secondary Plate</span>
          </button>
        </div>

        {/* Plates Table */}
        <div className="bg-slate-900/60 rounded-xl border border-slate-800 overflow-hidden shadow-xl backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/80 text-slate-400 font-mono text-[11px] uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="px-6 py-3.5">Plate Number</th>
                  <th className="px-6 py-3.5">Type</th>
                  <th className="px-6 py-3.5">Primary / Secondary</th>
                  <th className="px-6 py-3.5">Status</th>
                  <th className="px-6 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {isLoading ? (
                  <tr>
                    <td colSpan="5" className="px-6 py-12 text-center text-slate-500">
                      Loading ANPR plate index...
                    </td>
                  </tr>
                ) : data?.items?.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="px-6 py-12 text-center text-slate-500">
                      No plate records found.
                    </td>
                  </tr>
                ) : (
                  data?.items?.map((item) => (
                    <tr key={item.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="px-6 py-4 font-mono font-bold text-amber-400">
                        <div className="inline-flex items-center gap-2 px-3 py-1 bg-slate-950 border border-slate-700 rounded-md">
                          <Tag className="w-3.5 h-3.5 text-amber-400" />
                          <span>{item.plate_number}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 font-medium text-slate-200">
                        {item.plate_type}
                      </td>
                      <td className="px-6 py-4">
                        {item.is_primary ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                            Primary Vehicle Plate
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-slate-800 text-slate-400">
                            Secondary / Trailer
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        {item.is_active ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            Active
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-slate-800 text-slate-400">
                            Inactive
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => {
                            if (confirm(`Remove plate registration ${item.plate_number}?`)) {
                              deleteMutation.mutate(item.id);
                            }
                          }}
                          className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition-colors"
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
        title="Map Vehicle Plate"
      >
        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {errorMsg && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-400">
              {errorMsg}
            </div>
          )}

          <div>
            <label className="block text-slate-400 mb-1 font-medium">Target Vehicle *</label>
            <select
              required
              value={formData.vehicle_id}
              onChange={(e) => setFormData({ ...formData, vehicle_id: e.target.value })}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-cyan-500"
            >
              <option value="">Select Fleet Vehicle</option>
              {vehiclesData?.items?.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.vehicle_number} - {v.vehicle_type} ({v.make_model || 'Spec'})
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-400 mb-1 font-medium">Plate Number *</label>
              <input
                type="text"
                required
                placeholder="e.g. KA01TR9999"
                value={formData.plate_number}
                onChange={(e) => setFormData({ ...formData, plate_number: e.target.value.toUpperCase() })}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-white font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-slate-400 mb-1 font-medium">Plate Category</label>
              <select
                value={formData.plate_type}
                onChange={(e) => setFormData({ ...formData, plate_type: e.target.value })}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-cyan-500"
              >
                <option value="Standard">Standard</option>
                <option value="Commercial">Commercial</option>
                <option value="High Security">High Security (HSRP)</option>
                <option value="Foreign">Foreign / Special</option>
              </select>
            </div>
          </div>

          <div className="flex items-center gap-6 pt-2">
            <label className="flex items-center gap-2 text-slate-300">
              <input
                type="checkbox"
                checked={formData.is_primary}
                onChange={(e) => setFormData({ ...formData, is_primary: e.target.checked })}
                className="rounded bg-slate-950 border-slate-800 text-cyan-600 focus:ring-cyan-500"
              />
              Mark Primary Plate
            </label>
            <label className="flex items-center gap-2 text-slate-300">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="rounded bg-slate-950 border-slate-800 text-cyan-600 focus:ring-cyan-500"
              />
              Active
            </label>
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={closeModal}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saveMutation.isPending}
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-semibold rounded-lg shadow-lg shadow-cyan-600/20 transition-all"
            >
              {saveMutation.isPending ? 'Mapping...' : 'Map Plate'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
