"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import {
  Activity,
  CalendarDays,
  Coins,
  Loader2,
  MessageSquare,
  ScrollText,
  ShieldCheck,
  Users,
} from "lucide-react";
import { toast } from "sonner";
import { api, errorMessage } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type {
  AdminChatLog,
  AdminDashboardStats,
  ModelUsageRow,
  PromptLogRow,
  SystemLogRow,
  User,
} from "@/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

function StatCard({ label, value, icon }: { label: string; value: number; icon: React.ReactNode }) {
  return (
    <Card>
      <CardContent className="flex items-center gap-3 p-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary">{icon}</div>
        <div>
          <p className="text-2xl font-bold leading-none">{value.toLocaleString()}</p>
          <p className="mt-1 text-xs text-muted-foreground">{label}</p>
        </div>
      </CardContent>
    </Card>
  );
}

export default function AdminPage() {
  const { user } = useAuth();
  const router = useRouter();

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["admin-stats"],
    queryFn: async () => {
      const { data } = await api.get<{ data: AdminDashboardStats }>("/admin/dashboard");
      return data.data;
    },
  });

  const { data: users, isLoading: usersLoading } = useQuery({
    queryKey: ["admin-users"],
    queryFn: async () => {
      const { data } = await api.get<{ data: User[] }>("/admin/users");
      return data.data;
    },
  });

  const { data: chats } = useQuery({
    queryKey: ["admin-chats"],
    queryFn: async () => {
      const { data } = await api.get<{ data: AdminChatLog[] }>("/admin/chat-logs");
      return data.data;
    },
  });

  const { data: usage } = useQuery({
    queryKey: ["admin-usage"],
    queryFn: async () => {
      const { data } = await api.get<{ data: ModelUsageRow[] }>("/admin/model-usage");
      return data.data;
    },
  });

  const { data: prompts } = useQuery({
    queryKey: ["admin-prompts"],
    queryFn: async () => {
      const { data } = await api.get<{ data: PromptLogRow[] }>("/admin/prompt-logs");
      return data.data;
    },
  });

  const { data: logs } = useQuery({
    queryKey: ["admin-logs"],
    queryFn: async () => {
      const { data } = await api.get<{ data: SystemLogRow[] }>("/admin/system-logs");
      return data.data;
    },
  });

  if (!user?.is_admin) {
    return (
      <div className="flex h-64 flex-col items-center justify-center gap-3 text-center">
        <ShieldCheck className="h-12 w-12 text-muted-foreground/40" />
        <p className="font-semibold">Admins only</p>
        <p className="text-sm text-muted-foreground">You don&apos;t have permission to view this page.</p>
        <Button variant="outline" onClick={() => router.push("/dashboard")}>Back to dashboard</Button>
      </div>
    );
  }

  const toggleUser = async (id: number, current: boolean) => {
    try {
      await api.post(`/admin/users/${id}/toggle`);
      toast.success(current ? "User deactivated" : "User activated");
      window.location.reload();
    } catch (e) {
      toast.error(errorMessage(e));
    }
  };

  const fmtDate = (d: string) =>
    new Date(d).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Admin Panel</h1>
        <p className="text-sm text-muted-foreground">Platform overview, users and AI system logs.</p>
      </div>

      {statsLoading ? (
        <Card className="flex items-center justify-center p-10">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </Card>
      ) : (
        stats && (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <StatCard label="Users" value={stats.total_users} icon={<Users className="h-5 w-5" />} />
            <StatCard label="Chats" value={stats.total_chats} icon={<MessageSquare className="h-5 w-5" />} />
            <StatCard label="Messages" value={stats.total_messages} icon={<Activity className="h-5 w-5" />} />
            <StatCard label="Appointments" value={stats.total_appointments} icon={<CalendarDays className="h-5 w-5" />} />
            <StatCard label="Active appointments" value={stats.active_appointments} icon={<CalendarDays className="h-5 w-5" />} />
            <StatCard label="AI searches" value={stats.total_searches} icon={<ScrollText className="h-5 w-5" />} />
            <StatCard label="Prompt history" value={stats.total_prompts} icon={<ScrollText className="h-5 w-5" />} />
            <StatCard label="AI cost (USD)" value={Math.round((stats.total_cost_usd ?? 0) * 10000) / 10000} icon={<Coins className="h-5 w-5" />} />
          </div>
        )
      )}

      <Tabs defaultValue="users">
        <TabsList>
          <TabsTrigger value="users">Users</TabsTrigger>
          <TabsTrigger value="chats">Chats</TabsTrigger>
          <TabsTrigger value="usage">Model usage</TabsTrigger>
          <TabsTrigger value="prompts">Prompts</TabsTrigger>
          <TabsTrigger value="logs">System logs</TabsTrigger>
        </TabsList>

        <TabsContent value="users">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Registered users</CardTitle>
              <CardDescription>Activate or deactivate accounts.</CardDescription>
            </CardHeader>
            <CardContent>
              {usersLoading ? (
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b text-left text-xs uppercase tracking-wide text-muted-foreground">
                        <th className="pb-2 pr-3">Name</th>
                        <th className="pb-2 pr-3">Email</th>
                        <th className="pb-2 pr-3">Role</th>
                        <th className="pb-2 pr-3">Status</th>
                        <th className="pb-2">Joined</th>
                        <th className="pb-2"></th>
                      </tr>
                    </thead>
                    <tbody>
                      {users?.map((u) => (
                        <tr key={u.id} className="border-b last:border-0">
                          <td className="py-2 pr-3 font-medium">{u.full_name}</td>
                          <td className="py-2 pr-3 text-muted-foreground">{u.email}</td>
                          <td className="py-2 pr-3">
                            <Badge variant={u.is_admin ? "info" : "secondary"}>{u.is_admin ? "admin" : "user"}</Badge>
                          </td>
                          <td className="py-2 pr-3">
                            <Badge variant={u.is_admin ? "default" : u.role === "active" ? "success" : "danger"}>
                              {u.is_admin ? "admin" : u.role}
                            </Badge>
                          </td>
                          <td className="py-2 pr-3 text-muted-foreground">{fmtDate(u.created_at)}</td>
                          <td className="py-2 text-right">
                            {!u.is_admin && (
                              <Button variant="outline" size="sm" onClick={() => toggleUser(u.id, u.role === "active")}>
                                {u.role === "active" ? "Deactivate" : "Activate"}
                              </Button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="chats">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">All chats</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {chats?.map((c) => (
                  <div key={c.id} className="flex items-center justify-between gap-3 rounded-lg border p-3 text-sm">
                    <div className="min-w-0">
                      <p className="truncate font-medium">{c.title}</p>
                      <p className="text-xs text-muted-foreground">{c.user_email} · {c.agent}</p>
                    </div>
                    <div className="shrink-0 text-right">
                      <Badge variant="secondary">{c.message_count} msgs</Badge>
                      <p className="mt-1 text-xs text-muted-foreground">{fmtDate(c.created_at)}</p>
                    </div>
                  </div>
                ))}
                {chats && chats.length === 0 && <p className="text-sm text-muted-foreground">No chats yet.</p>}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="usage">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Model usage</CardTitle>
              <CardDescription>Per-call AI usage and cost.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-left text-xs uppercase tracking-wide text-muted-foreground">
                      <th className="pb-2 pr-3">Model</th>
                      <th className="pb-2 pr-3">Tier</th>
                      <th className="pb-2 pr-3">Agent</th>
                      <th className="pb-2 pr-3">Tokens</th>
                      <th className="pb-2 pr-3">Cost</th>
                      <th className="pb-2 pr-3">Status</th>
                      <th className="pb-2">Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {usage?.slice(0, 100).map((r) => (
                      <tr key={r.id} className="border-b last:border-0">
                        <td className="py-2 pr-3 font-mono text-xs">{r.model}</td>
                        <td className="py-2 pr-3">{r.tier ?? "-"}</td>
                        <td className="py-2 pr-3">{r.agent ?? "-"}</td>
                        <td className="py-2 pr-3">{r.total_tokens.toLocaleString()}</td>
                        <td className="py-2 pr-3">${r.cost_usd.toFixed(6)}</td>
                        <td className="py-2 pr-3">
                          <Badge variant={r.success ? "success" : "danger"}>{r.success ? "ok" : "fail"}</Badge>
                        </td>
                        <td className="py-2 text-muted-foreground">{fmtDate(r.created_at)}</td>
                      </tr>
                    ))}
                    {usage && usage.length === 0 && (
                      <tr><td colSpan={7} className="py-3 text-muted-foreground">No usage recorded yet.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="prompts">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Prompt history</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {prompts?.map((p) => (
                  <div key={p.id} className="rounded-lg border p-3 text-sm">
                    <div className="mb-1 flex items-center gap-2 text-xs text-muted-foreground">
                      <Badge variant="secondary">{p.agent ?? "unknown"}</Badge>
                      <span className="font-mono">{p.model ?? ""}</span>
                      <span className="ml-auto">{fmtDate(p.created_at)}</span>
                    </div>
                    <p className="line-clamp-3 whitespace-pre-wrap">{p.prompt}</p>
                  </div>
                ))}
                {prompts && prompts.length === 0 && <p className="text-sm text-muted-foreground">No prompts yet.</p>}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="logs">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">System logs</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-1">
                {logs?.slice(0, 200).map((l) => (
                  <div key={l.id} className="flex gap-3 rounded border-b py-1.5 text-xs last:border-0">
                    <span className="shrink-0 font-mono text-muted-foreground">{fmtDate(l.created_at)}</span>
                    <Badge
                      variant={l.level === "ERROR" ? "danger" : l.level === "WARNING" ? "warning" : "secondary"}
                      className="shrink-0"
                    >
                      {l.level}
                    </Badge>
                    <span className="min-w-0 truncate font-mono">{l.event}{l.path ? ` ${l.method} ${l.path}` : ""}</span>
                    {l.status_code && <span className="shrink-0 font-mono">{l.status_code}</span>}
                  </div>
                ))}
                {logs && logs.length === 0 && <p className="text-sm text-muted-foreground">No logs yet.</p>}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
