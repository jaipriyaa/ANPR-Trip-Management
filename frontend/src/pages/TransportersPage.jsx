import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getTransporters, createTransporter, updateTransporter, deleteTransporter } from '../api/masterData';
import Header from '../components/Header';
import Modal from '../components/Modal';
import { Plus, Search, Building2, Phone, Mail, User, Trash2, Edit, CheckCircle2, XCircle } from 'lucide-react';

export default function TransportersPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    code: '',
    company_name: '',
    contact_person: '',
    phone: '',
    email: '',
    is_active: true,
  });
  const [errorMsg, setErrorMsg] = useState('');

  // Fetch Transporters
  const { data, isLoading } = useQuery({
    queryKey: ['transporters', search],
    queryFn: () => getTransporters({ search, limit: 50 }),
  });

  // Create / Update Mutation
  const saveMutation = useMutation({
    mutationFn: (payload) => {
      if (editingId) {
        return updateTransporter(editingId, payload);
      }
      return createTransporter(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transporters'] });
      closeModal();
    },
    onError: (err) => {
      console.error('[TransportersPage] Save error:', err);
      setErrorMsg(err.message);
    },
  });

  // Delete Mutation
  const deleteMutation = useMutation({
    mutationFn: (id) => deleteTransporter(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transporters'] });
    },
  });

  const openCreateModal = () => {
    setEditingId(null);
    setFormData({ code: '', company_name: '', contact_person: '', phone: '', email: '', is_active: true });
    setErrorMsg('');
    setIsModalOpen(true);
  };

  const openEditModal = (item) => {
    setEditingId(item.id);
    setFormData({
      code: item.code,
      company_name: item.company_name,
      contact_person: item.contact_person || '',
      phone: item.phone || '',
      email: item.email || '',
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
        title="Transporter Master" 
        subtitle="Manage registered third-party logistics companies & fleet operators" 
      />

      <main className="flex-1 p-6 space-y-6 max-w-7xl mx-auto w-full">
        {/* Top Control Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900/60 p-4 rounded-xl border border-slate-800 backdrop-blur-md">
          {/* Search Box */}
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by company code, name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-all"
            />
          </div>

          {/* Action Button */}
          <button
            onClick={openCreateModal}
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-cyan-600/20 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Add Transporter</span>
          </button>
        </div>

        {/* Data Table */}
        <div className="bg-slate-900/60 rounded-xl border border-slate-800 overflow-hidden shadow-xl backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/80 text-slate-400 font-mono text-[11px] uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="px-6 py-3.5">Code</th>
                  <th className="px-6 py-3.5">Company Name</th>
                  <th className="px-6 py-3.5">Contact Person</th>
                  <th className="px-6 py-3.5">Phone / Email</th>
                  <th className="px-6 py-3.5">Status</th>
                  <th className="px-6 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {isLoading ? (
                  <tr>
                    <td colSpan="6" className="px-6 py-12 text-center text-slate-500">
                      Loading transporter database...
                    </td>
                  </tr>
                ) : data?.items?.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="px-6 py-12 text-center text-slate-500">
                      No transporters registered yet. Click "Add Transporter" to create one.
                    </td>
                  </tr>
                ) : (
                  data?.items?.map((item) => (
                    <tr key={item.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="px-6 py-4 font-mono font-semibold text-cyan-400">
                        {item.code}
                      </td>
                      <td className="px-6 py-4 font-medium text-white">
                        <div className="flex items-center gap-2">
                          <Building2 className="w-4 h-4 text-slate-500" />
                          <span>{item.company_name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-1.5 text-slate-400">
                          <User className="w-3.5 h-3.5" />
                          <span>{item.contact_person || 'N/A'}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 space-y-0.5">
                        <div className="flex items-center gap-1.5 text-slate-400">
                          <Phone className="w-3 h-3 text-slate-500" />
                          <span>{item.phone || 'N/A'}</span>
                        </div>
                        {item.email && (
                          <div className="flex items-center gap-1.5 text-slate-500 text-[11px]">
                            <Mail className="w-3 h-3 text-slate-500" />
                            <span>{item.email}</span>
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        {item.is_active ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            <CheckCircle2 className="w-3 h-3" /> Active
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
                            <XCircle className="w-3 h-3" /> Inactive
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-right space-x-2">
                        <button
                          onClick={() => openEditModal(item)}
                          className="p-1.5 text-slate-400 hover:text-cyan-400 hover:bg-slate-800 rounded-lg transition-colors"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => {
                            if (confirm(`Delete ${item.company_name}?`)) {
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

      {/* Create / Edit Transporter Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={closeModal}
        title={editingId ? 'Edit Transporter' : 'Add New Transporter'}
      >
        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {errorMsg && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-400">
              {errorMsg}
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-400 mb-1 font-medium">Company Code *</label>
              <input
                type="text"
                required
                placeholder="e.g. TR-LOG-01"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-white font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-slate-400 mb-1 font-medium">Company Name *</label>
              <input
                type="text"
                required
                placeholder="e.g. Apex Logistics"
                value={formData.company_name}
                onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-400 mb-1 font-medium">Contact Person</label>
              <input
                type="text"
                placeholder="John Doe"
                value={formData.contact_person}
                onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-slate-400 mb-1 font-medium">Phone Number</label>
              <input
                type="text"
                placeholder="+91 9876543210"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-slate-400 mb-1 font-medium">Email Address</label>
            <input
              type="email"
              placeholder="contact@company.com"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="flex items-center gap-2 pt-2">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="rounded bg-slate-950 border-slate-800 text-cyan-600 focus:ring-cyan-500"
            />
            <label htmlFor="is_active" className="text-slate-300">Active Status</label>
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
              {saveMutation.isPending ? 'Saving...' : 'Save Transporter'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
