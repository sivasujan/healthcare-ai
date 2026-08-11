"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CalendarDays, CalendarPlus, Loader2, MapPin, X } from "lucide-react";
import { toast } from "sonner";
import { api, errorMessage } from "@/lib/api";
import type { Appointment } from "@/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

const STATUS_VARIANTS: Record<Appointment["status"], "default" | "secondary" | "danger" | "success"> = {
  scheduled: "secondary",
  confirmed: "success",
  cancelled: "danger",
  completed: "default",
};

export default function AppointmentsPage() {
  const queryClient = useQueryClient();
  const [bookOpen, setBookOpen] = useState(false);
  const [form, setForm] = useState({
    title: "",
    doctor_name: "",
    specialty: "",
    hospital: "",
    appointment_date: "",
    appointment_time: "",
    notes: "",
  });

  const { data: appointments, isLoading } = useQuery({
    queryKey: ["appointments"],
    queryFn: async () => {
      const { data } = await api.get<{ data: Appointment[] }>("/appointments");
      return data.data;
    },
  });

  const bookMutation = useMutation({
    mutationFn: async (payload: Record<string, unknown>) => {
      const { data } = await api.post<{ data: Appointment }>("/appointments", payload);
      return data.data;
    },
    onSuccess: () => {
      toast.success("Appointment booked");
      setBookOpen(false);
      setForm({ title: "", doctor_name: "", specialty: "", hospital: "", appointment_date: "", appointment_time: "", notes: "" });
      queryClient.invalidateQueries({ queryKey: ["appointments"] });
    },
    onError: (e) => toast.error(errorMessage(e)),
  });

  const cancelMutation = useMutation({
    mutationFn: async (id: number) => {
      const { data } = await api.post<{ data: Appointment }>(`/appointments/${id}/cancel`);
      return data.data;
    },
    onSuccess: () => {
      toast.success("Appointment cancelled");
      queryClient.invalidateQueries({ queryKey: ["appointments"] });
    },
    onError: (e) => toast.error(errorMessage(e)),
  });

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title.trim() || !form.doctor_name.trim() || !form.specialty.trim() || !form.appointment_date || !form.appointment_time) {
      toast.error("Please fill in all required fields");
      return;
    }
    bookMutation.mutate({
      title: form.title.trim(),
      doctor_name: form.doctor_name.trim(),
      specialty: form.specialty.trim(),
      hospital: form.hospital.trim() || undefined,
      appointment_date: form.appointment_date,
      appointment_time: form.appointment_time,
      notes: form.notes.trim() || undefined,
    });
  };

  const sorted = [...(appointments ?? [])].sort((a, b) => a.appointment_date.localeCompare(b.appointment_date));
  const upcoming = sorted.filter((a) => a.status === "scheduled" || a.status === "confirmed");
  const past = sorted.filter((a) => a.status === "cancelled" || a.status === "completed");

  const formatDate = (d: string) =>
    new Date(d + "T00:00:00").toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric", year: "numeric" });

  const AppointmentCard = ({ a }: { a: Appointment }) => (
    <Card className="border-l-4" style={{ borderLeftColor: a.status === "cancelled" ? "var(--destructive)" : a.status === "completed" ? "var(--muted-foreground)" : "var(--primary)" }}>
      <CardContent className="flex items-start justify-between gap-4 p-4">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <p className="font-semibold">{a.title}</p>
            <Badge variant={STATUS_VARIANTS[a.status]}>{a.status}</Badge>
          </div>
          <p className="mt-1 text-sm text-muted-foreground">{a.doctor_name} · {a.specialty}</p>
          <p className="mt-0.5 flex items-center gap-1.5 text-sm text-muted-foreground">
            <CalendarDays className="h-3.5 w-3.5" /> {formatDate(a.appointment_date)} at {a.appointment_time}
          </p>
          {a.hospital && (
            <p className="mt-0.5 flex items-center gap-1.5 text-sm text-muted-foreground">
              <MapPin className="h-3.5 w-3.5" /> {a.hospital}
            </p>
          )}
          {a.notes && <p className="mt-1 text-xs text-muted-foreground">Note: {a.notes}</p>}
        </div>
        {(a.status === "scheduled" || a.status === "confirmed") && (
          <Button
            variant="outline"
            size="sm"
            className="shrink-0"
            onClick={() => cancelMutation.mutate(a.id)}
            disabled={cancelMutation.isPending}
          >
            <X className="h-3.5 w-3.5" /> Cancel
          </Button>
        )}
      </CardContent>
    </Card>
  );

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Appointments</h1>
          <p className="text-sm text-muted-foreground">Book, track and cancel your medical appointments.</p>
        </div>
        <Button onClick={() => setBookOpen(true)}>
          <CalendarPlus className="h-4 w-4" /> Book appointment
        </Button>
      </div>

      {isLoading && (
        <Card className="flex items-center justify-center p-10">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </Card>
      )}

      {!isLoading && upcoming.length === 0 && past.length === 0 && (
        <Card className="border-dashed p-10 text-center">
          <CalendarDays className="mx-auto h-10 w-10 text-muted-foreground/40" />
          <p className="mt-2 text-sm text-muted-foreground">No appointments yet — book your first one.</p>
        </Card>
      )}

      {upcoming.length > 0 && (
        <div>
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">Upcoming</h2>
          <div className="space-y-3">{upcoming.map((a) => <AppointmentCard key={a.id} a={a} />)}</div>
        </div>
      )}

      {past.length > 0 && (
        <div>
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">Past & cancelled</h2>
          <div className="space-y-3">{past.map((a) => <AppointmentCard key={a.id} a={a} />)}</div>
        </div>
      )}

      <Dialog open={bookOpen} onOpenChange={setBookOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Book an appointment</DialogTitle>
            <DialogDescription>Fill in the details below — you can book with any doctor.</DialogDescription>
          </DialogHeader>
          <form onSubmit={submit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="title">Title *</Label>
              <Input id="title" placeholder="e.g. Follow-up checkup" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label htmlFor="doctor_name">Doctor name *</Label>
                <Input id="doctor_name" placeholder="e.g. Dr. Smith" value={form.doctor_name} onChange={(e) => setForm({ ...form, doctor_name: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="specialty">Specialty *</Label>
                <Input id="specialty" placeholder="e.g. Cardiology" value={form.specialty} onChange={(e) => setForm({ ...form, specialty: e.target.value })} />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="hospital">Hospital / clinic</Label>
              <Input id="hospital" placeholder="e.g. City General Hospital" value={form.hospital} onChange={(e) => setForm({ ...form, hospital: e.target.value })} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label htmlFor="appointment_date">Date *</Label>
                <Input id="appointment_date" type="date" value={form.appointment_date} onChange={(e) => setForm({ ...form, appointment_date: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="appointment_time">Time *</Label>
                <Input id="appointment_time" type="time" value={form.appointment_time} onChange={(e) => setForm({ ...form, appointment_time: e.target.value })} />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="notes">Notes</Label>
              <Textarea id="notes" rows={2} placeholder="Anything the doctor should know…" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setBookOpen(false)}>Cancel</Button>
              <Button type="submit" disabled={bookMutation.isPending}>
                {bookMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                Book appointment
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
