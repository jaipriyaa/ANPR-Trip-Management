import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getDrivers, getTransporters, createDriver, updateDriver, deleteDriver } from '../api/masterData';
import Header from '../components/Header';
import Modal from '../components/Modal';
import { Plus, Search, UserCheck, Phone, CreditCard, Building2, CheckCircle2, XCircle, Trash2, Edit } from 'lucide-react';

export default function DriversPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    full_name: '',
    license_number: '',
    phone_number: '',
    identity_card_no: '',
    transporter_id: '',
    is_active: true,
  });
  const [errorMsg, setErrorMsg] = useState('');

  // Fetch Drivers & Transporters
  const { data, isLoading } = useQuery({
    queryKey: ['drivers', search],
    queryFn: () => getDrivers({ search, limit: 50 }),
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
        transporter_id: payload.transporter_id || null,
      };
      if (editingId) {
        return updateDriver(editingId, formatted);
      }
      return createDriver(formatted);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['drivers'] });
      closeModal();
    },
    onError: (err) => {
      console.error('[DriversPage] Save error:', err);
      setErrorMsg(err.message);
    },
  });

  // Delete Mutation
  const deleteMutation = useMutation({
    mutationFn: (id) => deleteDriver(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['drivers'] });
    },
  });

  const openCreateModal = () => {
    setEditingId(null);
    setFormData({
      full_name: '',
      license_number: '',
      phone_number: '',
      identity_card_no: '',
      transporter_id: '',
      is_active: true,
    });
    setErrorMsg('');
    setIsModalOpen(true);
  };

  const openEditModal = (item) => {
    setEditingId(item.id);
    setFormData({
      full_name: item.full_name,
      license_number: item.license_number,
      phone_number: item.phone_number,
      identity_card_no: item.identity_card_no || '',
      transporter_id: item.transporter_id || '',
      is_active: item.is_active,
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
        title="Driver Master" 
        subtitle="Manage authorized vehicle drivers, commercial license verification, and safety IDs" 
      />

      <main className="flex-1 p-6 space-y-6 max-w-7xl mx-auto w-full">
        {/* Control Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white p-4 rounded-xl border border-[#c8d8e4] backdrop-blur-md">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-[#5c7885] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by driver name, license, phone..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-lg text-xs text-[#1a3b45] placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-all"
            />
          </div>

          <button
            onClick={openCreateModal}
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-[#1a3b45] rounded-lg text-xs font-semibold shadow-lg shadow-cyan-600/20 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Add Driver</span>
          </button>
        </div>

        {/* Drivers Table */}
        <div className="bg-white rounded-xl border border-[#c8d8e4] overflow-hidden shadow-xl backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-white text-[#5c7885] font-mono text-[11px] uppercase tracking-wider border-b border-[#c8d8e4]">
                <tr>
                  <th className="px-6 py-3.5">Full Name</th>
                  <th className="px-6 py-3.5">License Number</th>
                  <th className="px-6 py-3.5">Phone / Govt ID</th>
                  <th className="px-6 py-3.5">Transporter Company</th>
                  <th className="px-6 py-3.5">Status</th>
                  <th className="px-6 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-[#2b6777]">
                {isLoading ? (
                  <tr>
                    <td colSpan="6" className="px-6 py-12 text-center text-[#5c7885]">
                      Loading drivers list...
                    </td>
                  </tr>
                ) : data?.items?.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="px-6 py-12 text-center text-[#5c7885]">
                      No drivers found. Click "Add Driver" to register one.
                    </td>
                  </tr>
                ) : (
                  data?.items?.map((item) => (
                    <tr key={item.id} className="hover:bg-[#f0f6f8] transition-colors">
                      <td className="px-6 py-4 font-medium text-[#1a3b45]">
                        <div className="flex items-center gap-2">
                          <UserCheck className="w-4 h-4 text-cyan-400" />
                          <span>{item.full_name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 font-mono text-cyan-300">
                        {item.license_number}
                      </td>
                      <td className="px-6 py-4 space-y-0.5">
                        <div className="flex items-center gap-1.5 text-[#2b6777]">
                          <Phone className="w-3 h-3 text-[#5c7885]" />
                          <span>{item.phone_number}</span>
                        </div>
                        {item.identity_card_no && (
                          <div className="flex items-center gap-1.5 text-[#5c7885] text-[11px]">
                            <CreditCard className="w-3 h-3 text-[#5c7885]" />
                            <span>{item.identity_card_no}</span>
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 font-medium text-[#2b6777]">
                        {item.transporter ? (
                          <div className="flex items-center gap-1.5">
                            <Building2 className="w-3.5 h-3.5 text-[#5c7885]" />
                            <span>{item.transporter.company_name}</span>
                          </div>
                        ) : (
                          <span className="text-[#5c7885] italic">Independent</span>
                        )}
                      </td>
                      <td className="px-6 py-4">
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
                            if (confirm(`Delete driver ${item.full_name}?`)) {
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
        title={editingId ? 'Edit Driver' : 'Register New Driver'}
      >
        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {errorMsg && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-400">
              {errorMsg}
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-[#5c7885] mb-1 font-medium">Full Name *</label>
              <input
                type="text"
                required
                placeholder="Robert Miller"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className="w-full px-3 py-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-lg text-[#1a3b45] focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-[#5c7885] mb-1 font-medium">License Number *</label>
              <input
                type="text"
                required
                placeholder="DL-987654321"
                value={formData.license_number}
                onChange={(e) => setFormData({ ...formData, license_number: e.target.value.toUpperCase() })}
                className="w-full px-3 py-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-lg text-[#1a3b45] font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-[#5c7885] mb-1 font-medium">Phone Number *</label>
              <input
                type="text"
                required
                placeholder="+91 9876543210"
                value={formData.phone_number}
                onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                className="w-full px-3 py-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-lg text-[#1a3b45] focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-[#5c7885] mb-1 font-medium">Identity Card No / Aadhaar</label>
              <input
                type="text"
                placeholder="AADHAAR-100200"
                value={formData.identity_card_no}
                onChange={(e) => setFormData({ ...formData, identity_card_no: e.target.value })}
                className="w-full px-3 py-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-lg text-[#1a3b45] focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-[#5c7885] mb-1 font-medium">Transporter Company</label>
            <select
              value={formData.transporter_id}
              onChange={(e) => setFormData({ ...formData, transporter_id: e.target.value })}
              className="w-full px-3 py-2 bg-[#f2f2f2] border border-[#c8d8e4] rounded-lg text-[#1a3b45] focus:outline-none focus:border-cyan-500"
            >
              <option value="">Independent / Self Employed</option>
              {transportersData?.items?.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.company_name} ({t.code})
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2 pt-2">
            <input
              type="checkbox"
              id="driver_is_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="rounded bg-[#f2f2f2] border-[#c8d8e4] text-cyan-600 focus:ring-cyan-500"
            />
            <label htmlFor="driver_is_active" className="text-[#2b6777]">Active License</label>
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
              {saveMutation.isPending ? 'Saving...' : 'Save Driver'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
