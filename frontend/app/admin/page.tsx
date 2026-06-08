"use client";

import React, { useState, useCallback } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Users, Building2, CreditCard, BarChart3, ShieldCheck,
  Search, RefreshCw, CheckCircle2, XCircle, ChevronLeft,
  ChevronRight, AlertTriangle, Pencil, X, Save,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

// ── Types ─────────────────────────────────────────────────────────────
interface Stats {
  tenants: { total: number; active: number; paying: number; new_30d: number; trial: number };
  users: { total: number };
  products: { total: number };
  plan_distribution: Record<string, number>;
}
interface Tenant {
  id: string; slug: string; name: string; plan: string;
  is_active: boolean; trial_ends_at: string | null;
  stripe_customer_id: string | null; stripe_subscription_id: string | null;
  member_count: number; product_count: number; created_at: string | null;
}
interface User {
  id: string; email: string; full_name: string | null; clerk_id: string | null;
  is_active: boolean; tenant: string | null; role: string | null;
  last_login: string | null; created_at: string | null;
}

// ── Admin API client ──────────────────────────────────────────────────
function makeAdminClient(key: string) {
  const base = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000") + "/api/v1/admin";
  const headers = { "Content-Type": "application/json", "X-Admin-Key": key };

  return {
    stats:   () => fetch(`${base}/stats`, { headers }).then(r => { if (!r.ok) throw r; return r.json(); }),
    tenants: (p: number, s: string) =>
      fetch(`${base}/tenants?page=${p}&per_page=20${s ? `&search=${encodeURIComponent(s)}` : ""}`, { headers })
        .then(r => { if (!r.ok) throw r; return r.json(); }),
    tenant:  (id: string) => fetch(`${base}/tenants/${id}`, { headers }).then(r => { if (!r.ok) throw r; return r.json(); }),
    patchTenant: (id: string, body: object) =>
      fetch(`${base}/tenants/${id}`, { method: "PATCH", headers, body: JSON.stringify(body) })
        .then(r => { if (!r.ok) throw r; return r.json(); }),
    users:   (p: number, s: string) =>
      fetch(`${base}/users?page=${p}&per_page=20${s ? `&search=${encodeURIComponent(s)}` : ""}`, { headers })
        .then(r => { if (!r.ok) throw r; return r.json(); }),
    auditLogs: (p: number) =>
      fetch(`${base}/audit-logs?page=${p}&per_page=50`, { headers })
        .then(r => { if (!r.ok) throw r; return r.json(); }),
  };
}

// ── Stat card ─────────────────────────────────────────────────────────
function StatCard({ label, value, sub, icon: Icon, color }: {
  label: string; value: number | string; sub?: string;
  icon: React.ElementType; color: string;
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-5">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-gray-400">{label}</span>
        <div className={`w-8 h-8 rounded-lg ${color} flex items-center justify-center`}>
          <Icon className="w-4 h-4 text-white" />
        </div>
      </div>
      <div className="text-2xl font-bold text-white">{value}</div>
      {sub && <div className="text-xs text-gray-500 mt-1">{sub}</div>}
    </div>
  );
}

// ── Plan badge ────────────────────────────────────────────────────────
const planColors: Record<string, string> = {
  Agency: "bg-violet-500/20 text-violet-300 border-violet-500/30",
  Business: "bg-blue-500/20 text-blue-300 border-blue-500/30",
  Professional: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
  Starter: "bg-gray-500/20 text-gray-300 border-gray-500/30",
  Free: "bg-gray-500/10 text-gray-500 border-gray-500/20",
};

function PlanBadge({ plan }: { plan: string }) {
  return (
    <Badge className={`text-xs border ${planColors[plan] ?? planColors.Free}`}>
      {plan}
    </Badge>
  );
}

// ── Tenant edit modal ─────────────────────────────────────────────────
function TenantEditModal({ tenant, onClose, onSave }: {
  tenant: Tenant; onClose: () => void;
  onSave: (id: string, body: object) => void;
}) {
  const [isActive, setIsActive] = useState(tenant.is_active);
  const [plan, setPlan] = useState(tenant.plan);
  const [notes, setNotes] = useState("");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl border border-white/10 bg-[#0F1117] p-6 shadow-2xl">
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-lg font-semibold text-white">Edit Tenant</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-300">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="text-xs text-gray-400 mb-1 block">Tenant</label>
            <div className="text-sm text-white font-medium">{tenant.name}</div>
            <div className="text-xs text-gray-500">{tenant.slug}</div>
          </div>

          <div>
            <label className="text-xs text-gray-400 mb-1.5 block">Plan</label>
            <select
              value={plan}
              onChange={e => setPlan(e.target.value)}
              className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-violet-500"
            >
              {["Starter", "Professional", "Business", "Agency"].map(p => (
                <option key={p} value={p} className="bg-[#0F1117]">{p}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs text-gray-400 mb-1.5 block">Status</label>
            <div className="flex gap-2">
              <button
                onClick={() => setIsActive(true)}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all border ${isActive ? "border-emerald-500 bg-emerald-500/15 text-emerald-400" : "border-white/10 bg-white/5 text-gray-400"}`}
              >
                Active
              </button>
              <button
                onClick={() => setIsActive(false)}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all border ${!isActive ? "border-red-500 bg-red-500/15 text-red-400" : "border-white/10 bg-white/5 text-gray-400"}`}
              >
                Suspended
              </button>
            </div>
          </div>

          <div>
            <label className="text-xs text-gray-400 mb-1.5 block">Admin notes (internal)</label>
            <textarea
              value={notes}
              onChange={e => setNotes(e.target.value)}
              placeholder="Churn risk, support ticket ref, etc."
              rows={3}
              className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder-gray-600 outline-none focus:border-violet-500 resize-none"
            />
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <Button variant="ghost" onClick={onClose} className="flex-1 text-gray-400 hover:text-white">
            Cancel
          </Button>
          <Button
            onClick={() => {
              onSave(tenant.id, {
                is_active: isActive,
                plan_name: plan !== tenant.plan ? plan : undefined,
                notes: notes || undefined,
              });
              onClose();
            }}
            className="flex-1 bg-violet-600 hover:bg-violet-500 text-white"
          >
            <Save className="w-4 h-4 mr-1.5" />
            Save Changes
          </Button>
        </div>
      </div>
    </div>
  );
}

// ── Pagination ────────────────────────────────────────────────────────
function Pagination({ page, total, perPage, onPage }: {
  page: number; total: number; perPage: number; onPage: (p: number) => void;
}) {
  const totalPages = Math.ceil(total / perPage);
  if (totalPages <= 1) return null;
  return (
    <div className="flex items-center justify-between mt-4 text-sm text-gray-400">
      <span>{total} total</span>
      <div className="flex items-center gap-1">
        <button onClick={() => onPage(page - 1)} disabled={page === 1}
          className="p-1.5 rounded hover:bg-white/10 disabled:opacity-30 transition-all">
          <ChevronLeft className="w-4 h-4" />
        </button>
        <span className="px-3">Page {page} of {totalPages}</span>
        <button onClick={() => onPage(page + 1)} disabled={page >= totalPages}
          className="p-1.5 rounded hover:bg-white/10 disabled:opacity-30 transition-all">
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

// ── Login screen ──────────────────────────────────────────────────────
function AdminLogin({ onLogin }: { onLogin: (key: string) => void }) {
  const [key, setKey] = useState("");
  const [error, setError] = useState("");

  const attempt = async () => {
    setError("");
    try {
      const base = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000") + "/api/v1/admin";
      const r = await fetch(`${base}/stats`, { headers: { "X-Admin-Key": key } });
      if (r.ok) {
        sessionStorage.setItem("sv_admin_key", key);
        onLogin(key);
      } else {
        setError(r.status === 403 ? "Invalid admin key" : r.status === 503 ? "Admin panel is disabled on the server" : "Connection failed");
      }
    } catch {
      setError("Cannot reach API — is the backend running?");
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0E17] flex items-center justify-center p-4">
      <div className="w-full max-w-sm rounded-2xl border border-white/10 bg-white/[0.03] p-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-violet-600/20 flex items-center justify-center">
            <ShieldCheck className="w-5 h-5 text-violet-400" />
          </div>
          <div>
            <div className="text-lg font-bold text-white">Admin Panel</div>
            <div className="text-xs text-gray-500">SellerVision AI</div>
          </div>
        </div>

        <label className="text-xs text-gray-400 mb-1.5 block">Admin Key</label>
        <input
          type="password"
          value={key}
          onChange={e => setKey(e.target.value)}
          onKeyDown={e => e.key === "Enter" && attempt()}
          placeholder="ADMIN_SECRET_KEY value"
          className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2.5 text-sm text-white placeholder-gray-600 outline-none focus:border-violet-500 mb-4"
          autoFocus
        />
        {error && <p className="text-red-400 text-xs mb-3">{error}</p>}
        <Button onClick={attempt} disabled={!key}
          className="w-full bg-violet-600 hover:bg-violet-500 text-white">
          Unlock Admin Panel
        </Button>
        <p className="text-xs text-gray-600 mt-3 text-center">
          Set ADMIN_SECRET_KEY in your backend environment
        </p>
      </div>
    </div>
  );
}

// ── Main admin panel ──────────────────────────────────────────────────
export default function AdminPage() {
  const [adminKey, setAdminKey] = useState<string>(() =>
    typeof window !== "undefined" ? (sessionStorage.getItem("sv_admin_key") ?? "") : ""
  );
  const [tab, setTab] = useState<"overview" | "tenants" | "users" | "logs">("overview");
  const [tenantPage, setTenantPage] = useState(1);
  const [userPage, setUserPage] = useState(1);
  const [logPage, setLogPage] = useState(1);
  const [tenantSearch, setTenantSearch] = useState("");
  const [userSearch, setUserSearch] = useState("");;
  const [editTenant, setEditTenant] = useState<Tenant | null>(null);
  const qc = useQueryClient();

  const api = adminKey ? makeAdminClient(adminKey) : null;

  const { data: stats, isLoading: statsLoading } = useQuery<Stats>({
    queryKey: ["admin-stats"],
    queryFn: api!.stats,
    enabled: !!api,
    refetchInterval: 60_000,
  });

  const { data: tenants, isLoading: tenantsLoading } = useQuery({
    queryKey: ["admin-tenants", tenantPage, tenantSearch],
    queryFn: () => api!.tenants(tenantPage, tenantSearch),
    enabled: !!api && tab === "tenants",
  });

  const { data: users, isLoading: usersLoading } = useQuery({
    queryKey: ["admin-users", userPage, userSearch],
    queryFn: () => api!.users(userPage, userSearch),
    enabled: !!api && tab === "users",
  });

  const { data: logs } = useQuery({
    queryKey: ["admin-logs", logPage],
    queryFn: () => api!.auditLogs(logPage),
    enabled: !!api && tab === "logs",
  });

  const patchTenant = useMutation({
    mutationFn: ({ id, body }: { id: string; body: object }) => api!.patchTenant(id, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-tenants"] });
      qc.invalidateQueries({ queryKey: ["admin-stats"] });
    },
  });

  if (!adminKey) return <AdminLogin onLogin={setAdminKey} />;

  const tabs: Array<{ id: typeof tab; label: string; icon: React.ElementType }> = [
    { id: "overview", label: "Overview",  icon: BarChart3  },
    { id: "tenants",  label: "Tenants",   icon: Building2  },
    { id: "users",    label: "Users",     icon: Users      },
    { id: "logs",     label: "Audit Logs",icon: ShieldCheck },
  ];

  return (
    <div className="min-h-screen bg-[#0B0E17] text-white">
      {editTenant && (
        <TenantEditModal
          tenant={editTenant}
          onClose={() => setEditTenant(null)}
          onSave={(id, body) => patchTenant.mutate({ id, body })}
        />
      )}

      {/* Top bar */}
      <div className="border-b border-white/8 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-violet-600/20 flex items-center justify-center">
            <ShieldCheck className="w-4 h-4 text-violet-400" />
          </div>
          <div>
            <span className="font-bold text-white">Admin Panel</span>
            <span className="text-gray-500 text-sm ml-2">SellerVision AI</span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Button
            size="sm" variant="ghost"
            onClick={() => qc.invalidateQueries()}
            className="text-gray-400 hover:text-white h-8"
          >
            <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> Refresh
          </Button>
          <Button
            size="sm" variant="ghost"
            onClick={() => { sessionStorage.removeItem("sv_admin_key"); setAdminKey(""); }}
            className="text-gray-500 hover:text-red-400 h-8"
          >
            <X className="w-3.5 h-3.5 mr-1" /> Sign out
          </Button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* Tabs */}
        <div className="flex gap-1 mb-6 bg-white/5 rounded-xl p-1 w-fit">
          {tabs.map(t => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all
                ${tab === t.id ? "bg-violet-600 text-white" : "text-gray-400 hover:text-white hover:bg-white/5"}`}
            >
              <t.icon className="w-4 h-4" />
              {t.label}
            </button>
          ))}
        </div>

        {/* Overview */}
        {tab === "overview" && (
          <div className="space-y-6">
            {statsLoading ? (
              <div className="text-gray-500 text-sm">Loading stats…</div>
            ) : stats ? (
              <>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <StatCard label="Total Tenants"    value={stats.tenants.total}  sub={`${stats.tenants.new_30d} new this month`} icon={Building2}  color="bg-violet-600"  />
                  <StatCard label="Paying Customers" value={stats.tenants.paying} sub={`${stats.tenants.trial} on trial`}          icon={CreditCard} color="bg-emerald-600" />
                  <StatCard label="Active Users"     value={stats.users.total}    icon={Users}      color="bg-blue-600"   />
                  <StatCard label="Total Products"   value={stats.products.total} icon={BarChart3}  color="bg-amber-600"  />
                </div>

                <div className="rounded-xl border border-white/10 bg-white/[0.03] p-5">
                  <h3 className="text-sm font-semibold text-white mb-4">Plan Distribution</h3>
                  <div className="space-y-3">
                    {Object.entries(stats.plan_distribution)
                      .sort(([, a], [, b]) => b - a)
                      .map(([name, count]) => (
                        <div key={name} className="flex items-center gap-3">
                          <PlanBadge plan={name} />
                          <div className="flex-1 bg-white/5 rounded-full h-2 overflow-hidden">
                            <div
                              className="h-full bg-violet-500 rounded-full"
                              style={{ width: `${Math.max(4, (count / Math.max(stats.tenants.total, 1)) * 100)}%` }}
                            />
                          </div>
                          <span className="text-sm text-gray-400 w-6 text-right">{count}</span>
                        </div>
                      ))}
                  </div>
                </div>
              </>
            ) : null}
          </div>
        )}

        {/* Tenants */}
        {tab === "tenants" && (
          <div className="space-y-4">
            <div className="flex gap-3">
              <div className="relative flex-1 max-w-xs">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input
                  value={tenantSearch}
                  onChange={e => { setTenantSearch(e.target.value); setTenantPage(1); }}
                  placeholder="Search tenants…"
                  className="w-full pl-9 pr-3 py-2 rounded-lg border border-white/10 bg-white/5 text-sm text-white placeholder-gray-600 outline-none focus:border-violet-500"
                />
              </div>
            </div>

            <div className="rounded-xl border border-white/10 overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/10 bg-white/[0.02]">
                    {["Tenant", "Plan", "Members", "Status", "Created", "Actions"].map(h => (
                      <th key={h} className="text-left text-xs text-gray-500 font-medium px-4 py-3">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {tenantsLoading ? (
                    <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-500">Loading…</td></tr>
                  ) : (tenants?.items ?? []).map((t: Tenant) => (
                    <tr key={t.id} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                      <td className="px-4 py-3">
                        <div className="font-medium text-white">{t.name}</div>
                        <div className="text-xs text-gray-500">{t.slug}</div>
                      </td>
                      <td className="px-4 py-3"><PlanBadge plan={t.plan} /></td>
                      <td className="px-4 py-3 text-gray-300">{t.member_count}</td>
                      <td className="px-4 py-3">
                        {t.is_active
                          ? <span className="flex items-center gap-1 text-emerald-400 text-xs"><CheckCircle2 className="w-3.5 h-3.5" />Active</span>
                          : <span className="flex items-center gap-1 text-red-400 text-xs"><XCircle className="w-3.5 h-3.5" />Suspended</span>
                        }
                      </td>
                      <td className="px-4 py-3 text-gray-500 text-xs">
                        {t.created_at ? new Date(t.created_at).toLocaleDateString() : "—"}
                      </td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => setEditTenant(t)}
                          className="p-1.5 rounded hover:bg-white/10 text-gray-400 hover:text-white transition-all"
                        >
                          <Pencil className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination page={tenantPage} total={tenants?.total ?? 0} perPage={20} onPage={setTenantPage} />
          </div>
        )}

        {/* Users */}
        {tab === "users" && (
          <div className="space-y-4">
            <div className="relative max-w-xs">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                value={userSearch}
                onChange={e => { setUserSearch(e.target.value); setUserPage(1); }}
                placeholder="Search users…"
                className="w-full pl-9 pr-3 py-2 rounded-lg border border-white/10 bg-white/5 text-sm text-white placeholder-gray-600 outline-none focus:border-violet-500"
              />
            </div>

            <div className="rounded-xl border border-white/10 overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/10 bg-white/[0.02]">
                    {["User", "Tenant", "Role", "Status", "Last Login"].map(h => (
                      <th key={h} className="text-left text-xs text-gray-500 font-medium px-4 py-3">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {usersLoading ? (
                    <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-500">Loading…</td></tr>
                  ) : (users?.items ?? []).map((u: User) => (
                    <tr key={u.id} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                      <td className="px-4 py-3">
                        <div className="font-medium text-white">{u.full_name || "—"}</div>
                        <div className="text-xs text-gray-500">{u.email}</div>
                      </td>
                      <td className="px-4 py-3 text-gray-300 text-xs">{u.tenant ?? "—"}</td>
                      <td className="px-4 py-3">
                        <span className="text-xs bg-white/5 border border-white/10 px-2 py-0.5 rounded-full text-gray-300">
                          {u.role ?? "—"}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        {u.is_active
                          ? <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                          : <XCircle className="w-4 h-4 text-red-400" />
                        }
                      </td>
                      <td className="px-4 py-3 text-gray-500 text-xs">
                        {u.last_login ? new Date(u.last_login).toLocaleDateString() : "Never"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination page={userPage} total={users?.total ?? 0} perPage={20} onPage={setUserPage} />
          </div>
        )}

        {/* Audit logs */}
        {tab === "logs" && (
          <div className="space-y-4">
            <div className="rounded-xl border border-white/10 overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/10 bg-white/[0.02]">
                    {["Action", "Resource", "Tenant", "User", "IP", "Time"].map(h => (
                      <th key={h} className="text-left text-xs text-gray-500 font-medium px-4 py-3">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(logs?.items ?? []).map((l: any, i: number) => (
                    <tr key={i} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                      <td className="px-4 py-2.5">
                        <code className="text-xs text-violet-300 bg-violet-500/10 px-1.5 py-0.5 rounded">
                          {l.action}
                        </code>
                      </td>
                      <td className="px-4 py-2.5 text-gray-400 text-xs">{l.resource_type ?? "—"}</td>
                      <td className="px-4 py-2.5 text-gray-400 text-xs">{l.tenant ?? "—"}</td>
                      <td className="px-4 py-2.5 text-gray-400 text-xs">{l.user_email ?? "—"}</td>
                      <td className="px-4 py-2.5 text-gray-500 text-xs font-mono">{l.ip ?? "—"}</td>
                      <td className="px-4 py-2.5 text-gray-500 text-xs">
                        {l.created_at ? new Date(l.created_at).toLocaleString() : "—"}
                      </td>
                    </tr>
                  ))}
                  {!logs?.items?.length && (
                    <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-500">No audit logs yet</td></tr>
                  )}
                </tbody>
              </table>
            </div>
            <Pagination page={logPage} total={logs?.total ?? 0} perPage={50} onPage={setLogPage} />
          </div>
        )}
      </div>
    </div>
  );
}
