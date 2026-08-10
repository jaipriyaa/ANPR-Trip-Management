import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import { 
  Users, 
  Shield, 
  Plus, 
  UserCheck, 
  Lock, 
  Mail, 
  X,
  CheckCircle2
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    role: 'Security Officer',
  });

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const [uRes, rRes] = await Promise.all([
        fetch(`${API_BASE_URL}/admin/users`),
        fetch(`${API_BASE_URL}/admin/roles`),
      ]);
      if (uRes.ok) setUsers(await uRes.json());
      if (rRes.ok) setRoles(await rRes.json());
    } catch (err) {
      console.error('Failed to fetch users or roles:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE_URL}/admin/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (res.ok) {
        setShowAddModal(false);
        setFormData({ username: '', email: '', full_name: '', role: 'Security Officer' });
        fetchUsers();
      } else {
        const err = await res.json();
        alert(`Error creating user: ${err.detail || 'Validation error'}`);
      }
    } catch (err) {
      console.error('Failed to create user:', err);
    }
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-slate-950 text-slate-100 font-sans">
      <Header title="User Management & Role-Based Access Control" subtitle="Configure system accounts, role permissions matrix (Administrator, Security Officer, Gate Operator, Supervisor, Viewer)" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Header Action Bar */}
        <div className="flex items-center justify-between bg-slate-900/80 rounded-xl p-4 border border-slate-800 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <Users className="w-5 h-5 text-cyan-400" />
            <div>
              <h2 className="text-sm font-bold text-white">Platform User Accounts</h2>
              <p className="text-xs text-slate-400">{users.length} Registered Personnel Accounts</p>
            </div>
          </div>

          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-cyan-500/20"
          >
            <Plus className="w-4 h-4" /> Create User Account
          </button>
        </div>

        {/* Users Master Table */}
        <div className="bg-slate-900/80 rounded-xl border border-slate-800 overflow-hidden backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-mono">
                <tr>
                  <th className="p-4">Username</th>
                  <th className="p-4">Full Name</th>
                  <th className="p-4">Email</th>
                  <th className="p-4">Role</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Created Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan="6" className="p-8 text-center text-slate-500 font-sans">Loading user accounts...</td>
                  </tr>
                ) : users.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="p-8 text-center text-slate-500 font-sans">No user accounts found.</td>
                  </tr>
                ) : (
                  users.map((u) => (
                    <tr key={u.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="p-4 font-bold text-cyan-400">{u.username}</td>
                      <td className="p-4 font-sans text-white">{u.full_name}</td>
                      <td className="p-4 text-purple-300">{u.email}</td>
                      <td className="p-4">
                        <span className={`px-2.5 py-1 rounded text-[10px] font-bold border ${
                          u.role === 'Administrator' ? 'bg-purple-500/10 text-purple-400 border-purple-500/30' :
                          u.role === 'Security Officer' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' :
                          u.role === 'Gate Operator' ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30' :
                          'bg-slate-800 text-slate-400 border-slate-700'
                        }`}>
                          {u.role}
                        </span>
                      </td>
                      <td className="p-4">
                        <span className="text-emerald-400 font-bold">● Active</span>
                      </td>
                      <td className="p-4 text-slate-400 text-[11px]">{u.created_at ? new Date(u.created_at).toLocaleDateString() : 'System'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Role Permissions Matrix Section */}
        <div className="bg-slate-900/80 rounded-xl border border-slate-800 p-5 backdrop-blur-md space-y-4">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Shield className="w-4 h-4 text-purple-400" /> Configurable Role Permissions Matrix (RBAC)
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {roles.map((r) => (
              <div key={r.role} className="bg-slate-950 rounded-xl border border-slate-800 p-4 space-y-3">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <h4 className="font-bold text-sm text-cyan-400">{r.role}</h4>
                  <Shield className="w-4 h-4 text-purple-400" />
                </div>
                <p className="text-xs text-slate-400">{r.description}</p>
                <div className="space-y-1 pt-1">
                  <p className="text-[10px] text-slate-500 uppercase font-semibold">Allowed Modules:</p>
                  <div className="flex flex-wrap gap-1">
                    {r.permissions.map((p) => (
                      <span key={p} className="text-[10px] bg-slate-900 text-slate-300 border border-slate-800 px-2 py-0.5 rounded font-mono">
                        ✓ {p}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Modal: Create User */}
        {showAddModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-md space-y-4 shadow-2xl">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <UserCheck className="w-5 h-5 text-cyan-400" /> Create Platform User Account
                </h3>
                <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-white">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleCreateUser} className="space-y-3 text-xs">
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Username</label>
                  <input
                    type="text"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    placeholder="e.g. officer_verma"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:border-cyan-500 font-mono"
                    required
                  />
                </div>

                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Full Name</label>
                  <input
                    type="text"
                    value={formData.full_name}
                    onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                    placeholder="e.g. Major Rajesh Verma"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:border-cyan-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Email Address</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="e.g. verma@factory.com"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:border-cyan-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Assign Role</label>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:border-cyan-500"
                  >
                    <option value="Administrator">Administrator</option>
                    <option value="Security Officer">Security Officer</option>
                    <option value="Gate Operator">Gate Operator</option>
                    <option value="Supervisor">Supervisor</option>
                    <option value="Viewer">Viewer</option>
                  </select>
                </div>

                <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="px-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-400 hover:text-white"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-5 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-xl shadow-lg shadow-cyan-500/20"
                  >
                    Create Account
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
