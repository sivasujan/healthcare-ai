"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  Activity,
  ArrowRight,
  CalendarDays,
  HeartPulse,
  MessageSquare,
  Pill,
  Search,
  ShieldAlert,
  Stethoscope,
} from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/states";
import { formatDate, formatTime } from "@/lib/utils";
import type { Appointment, ChatSummary } from "@/types";

function greeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  return "Good evening";
}

export default function DashboardPage() {
  const { profile, user } = useAuth();

  const { data: chats, isLoading: chatsLoading } = useQuery({
    queryKey: ["chats"],
    queryFn: async () => (await api.get<{ data: ChatSummary[] }>("/chat")).data.data,
  });

  const { data: appointments, isLoading: apptsLoading } = useQuery({
    queryKey: ["appointments"],
    queryFn: async () => (await api.get<{ data: Appointment[] }>("/appointments")).data.data,
  });

  const quickActions = [
    { href: "/dashboard/chat", icon: MessageSquare, label: "AI Chat", desc: "Ask anything" },
    { href: "/dashboard/symptom", icon: HeartPulse, label: "Symptom Analysis", desc: "Check symptoms" },
    { href: "/dashboard/medicine", icon: Pill, label: "Medicine Info", desc: "Look up medicine" },
    { href: "/dashboard/doctor", icon: Stethoscope, label: "Find a Doctor", desc: "Get a specialist" },
    { href: "/dashboard/emergency", icon: ShieldAlert, label: "Emergency Check", desc: "Urgent?" },
    { href: "/dashboard/appointments", icon: CalendarDays, label: "Appointments", desc: "Book a visit" },
  ];

  const upcoming = (appointments ?? []).filter(
    (a) => a.status === "scheduled" || a.status === "confirmed"
  );

  const stats = [
    { label: "Chats", value: chats?.length ?? 0 },
    { label: "Appointments", value: appointments?.length ?? 0 },
    { label: "Upcoming", value: upcoming.length },
  ];

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
          {greeting()}, {profile?.full_name?.split(" ")[0] ?? user?.full_name?.split(" ")[0] ?? "there"} 👋
        </h1>
        <p className="mt-1 text-muted-foreground">
          Here&apos;s your health overview. How can MediAssist help you today?
        </p>
      </motion.div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-3">
        {stats.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <Card>
              <CardContent className="flex items-center justify-between p-5">
                <div>
                  <p className="text-sm text-muted-foreground">{s.label}</p>
                  {s.label === "Chats" && chatsLoading ? (
                    <Skeleton className="mt-1 h-7 w-12" />
                  ) : (
                    <p className="text-2xl font-bold">{s.value}</p>
                  )}
                </div>
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
                  <Activity className="h-5 w-5" />
                </span>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Quick actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {quickActions.map((a, i) => (
              <motion.div key={a.href} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 + i * 0.04 }}>
                <Link
                  href={a.href}
                  className="group flex items-center gap-3 rounded-xl border p-4 transition-all hover:border-primary/40 hover:bg-accent/50"
                >
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-primary-foreground">
                    <a.icon className="h-5 w-5" />
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-semibold">{a.label}</p>
                    <p className="text-xs text-muted-foreground">{a.desc}</p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-1" />
                </Link>
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Upcoming appointments */}
        <Card>
          <CardHeader className="flex-row items-center justify-between space-y-0">
            <CardTitle>Upcoming appointments</CardTitle>
            <Link href="/dashboard/appointments" className="text-xs font-medium text-primary hover:underline">
              View all
            </Link>
          </CardHeader>
          <CardContent>
            {apptsLoading ? (
              <div className="space-y-2">
                <Skeleton className="h-16 w-full" />
                <Skeleton className="h-16 w-full" />
              </div>
            ) : upcoming.length === 0 ? (
              <EmptyState
                icon={<CalendarDays className="h-5 w-5" />}
                title="No upcoming appointments"
                description="Book an appointment to see it here."
                action={
                  <Link href="/dashboard/appointments">
                    <Badge className="cursor-pointer" variant="info">Book now</Badge>
                  </Link>
                }
              />
            ) : (
              <div className="space-y-3">
                {upcoming.slice(0, 3).map((a) => (
                  <div key={a.id} className="flex items-center justify-between rounded-lg border p-3">
                    <div>
                      <p className="text-sm font-medium">{a.doctor_name}</p>
                      <p className="text-xs text-muted-foreground">{a.specialty}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs font-medium">{formatDate(a.appointment_date)}</p>
                      <p className="text-xs text-muted-foreground">{formatTime(a.appointment_time)}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent chats */}
        <Card>
          <CardHeader className="flex-row items-center justify-between space-y-0">
            <CardTitle>Recent chats</CardTitle>
            <Link href="/dashboard/chat" className="text-xs font-medium text-primary hover:underline">
              Open chat
            </Link>
          </CardHeader>
          <CardContent>
            {chatsLoading ? (
              <div className="space-y-2">
                <Skeleton className="h-14 w-full" />
                <Skeleton className="h-14 w-full" />
              </div>
            ) : (chats ?? []).length === 0 ? (
              <EmptyState
                icon={<MessageSquare className="h-5 w-5" />}
                title="No chats yet"
                description="Start a conversation with the AI assistant."
                action={
                  <Link href="/dashboard/chat">
                    <Badge className="cursor-pointer" variant="info">Start chatting</Badge>
                  </Link>
                }
              />
            ) : (
              <div className="space-y-2">
                {(chats ?? []).slice(0, 4).map((c) => (
                  <Link
                    key={c.id}
                    href={`/dashboard/chat/${c.id}`}
                    className="flex items-center justify-between rounded-lg border p-3 transition-colors hover:bg-accent/50"
                  >
                    <div className="flex min-w-0 items-center gap-3">
                      <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                        <MessageSquare className="h-4 w-4" />
                      </span>
                      <div className="min-w-0">
                        <p className="truncate text-sm font-medium">{c.title}</p>
                        <p className="truncate text-xs text-muted-foreground">{formatDate(c.updated_at)}</p>
                      </div>
                    </div>
                    <Badge variant="secondary" className="shrink-0">{c.agent}</Badge>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Health summary */}
      <Card>
        <CardHeader>
          <CardTitle>Health summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-lg bg-muted/60 p-4">
              <p className="text-xs text-muted-foreground">Age / Gender</p>
              <p className="mt-1 font-medium">{profile?.age ? `${profile.age} years` : "—"} / {profile?.gender ?? "—"}</p>
            </div>
            <div className="rounded-lg bg-muted/60 p-4">
              <p className="text-xs text-muted-foreground">Height / Weight</p>
              <p className="mt-1 font-medium">
                {profile?.height_cm ? `${profile.height_cm} cm` : "—"} / {profile?.weight_kg ? `${profile.weight_kg} kg` : "—"}
              </p>
            </div>
            <div className="rounded-lg bg-muted/60 p-4">
              <p className="text-xs text-muted-foreground">Blood group</p>
              <p className="mt-1 font-medium">{profile?.blood_group ?? "—"}</p>
            </div>
            <div className="rounded-lg bg-muted/60 p-4">
              <p className="text-xs text-muted-foreground">Allergies</p>
              <p className="mt-1 truncate font-medium">{profile?.allergies || "None recorded"}</p>
            </div>
          </div>
          <div className="mt-4 flex items-start gap-2 rounded-lg border border-primary/20 bg-primary/5 p-4 text-xs text-muted-foreground">
            <Search className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
            <p>
              Tip: Complete your health profile for more personalized AI responses.{" "}
              <Link href="/dashboard/profile" className="font-medium text-primary hover:underline">
                Edit profile
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
