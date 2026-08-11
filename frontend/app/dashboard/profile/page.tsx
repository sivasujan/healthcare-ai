"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { KeyRound, Loader2, Plus, Trash2, UserRound } from "lucide-react";
import { toast } from "sonner";
import { api, errorMessage } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { Profile } from "@/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface HistoryEntry {
  id: number;
  condition: string;
  diagnosed_year?: number | null;
  notes?: string | null;
}

export default function ProfilePage() {
  const { user, refreshProfile } = useAuth();
  const queryClient = useQueryClient();
  const [saving, setSaving] = useState(false);
  const [changingPw, setChangingPw] = useState(false);
  const [form, setForm] = useState(() => ({
    full_name: user?.full_name ?? "",
    phone: user?.phone ?? "",
    preferred_language: "en",
  }));
  const [health, setHealth] = useState(() => ({
    age: "",
    gender: "",
    height_cm: "",
    weight_kg: "",
    blood_group: "",
    medical_history: "",
    allergies: "",
    current_medications: "",
  }));
  const [pw, setPw] = useState({ current_password: "", new_password: "", confirm: "" });
  const [newCondition, setNewCondition] = useState({ condition: "", diagnosed_year: "", notes: "" });

  const { data: profile } = useQuery({
    queryKey: ["profile"],
    queryFn: async () => {
      const { data } = await api.get<{ data: Profile }>("/profile");
      setForm({
        full_name: data.data.full_name ?? "",
        phone: data.data.phone ?? "",
        preferred_language: data.data.preferred_language ?? "en",
      });
      setHealth({
        age: data.data.age?.toString() ?? "",
        gender: data.data.gender ?? "",
        height_cm: data.data.height_cm?.toString() ?? "",
        weight_kg: data.data.weight_kg?.toString() ?? "",
        blood_group: data.data.blood_group ?? "",
        medical_history: data.data.medical_history ?? "",
        allergies: data.data.allergies ?? "",
        current_medications: data.data.current_medications ?? "",
      });
      return data.data;
    },
  });

  const { data: history } = useQuery({
    queryKey: ["medical-history"],
    queryFn: async () => {
      const { data } = await api.get<{ data: HistoryEntry[] }>("/profile/medical-history");
      return data.data;
    },
  });

  const saveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.put("/profile", {
        full_name: form.full_name,
        phone: form.phone || undefined,
        preferred_language: form.preferred_language,
        profile: {
          age: health.age ? Number(health.age) : undefined,
          gender: health.gender || undefined,
          height_cm: health.height_cm ? Number(health.height_cm) : undefined,
          weight_kg: health.weight_kg ? Number(health.weight_kg) : undefined,
          blood_group: health.blood_group || undefined,
          medical_history: health.medical_history || undefined,
          allergies: health.allergies || undefined,
          current_medications: health.current_medications || undefined,
        },
      });
      toast.success("Profile updated");
      await refreshProfile();
      queryClient.invalidateQueries({ queryKey: ["profile"] });
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      setSaving(false);
    }
  };

  const changePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (pw.new_password.length < 8) {
      toast.error("New password must be at least 8 characters");
      return;
    }
    if (pw.new_password !== pw.confirm) {
      toast.error("Passwords do not match");
      return;
    }
    setChangingPw(true);
    try {
      await api.post("/profile/change-password", {
        current_password: pw.current_password,
        new_password: pw.new_password,
      });
      toast.success("Password changed");
      setPw({ current_password: "", new_password: "", confirm: "" });
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      setChangingPw(false);
    }
  };

  const addHistory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCondition.condition.trim()) return;
    try {
      await api.post("/profile/medical-history", {
        condition: newCondition.condition.trim(),
        diagnosed_year: newCondition.diagnosed_year ? Number(newCondition.diagnosed_year) : undefined,
        notes: newCondition.notes.trim() || undefined,
      });
      toast.success("Entry added");
      setNewCondition({ condition: "", diagnosed_year: "", notes: "" });
      queryClient.invalidateQueries({ queryKey: ["medical-history"] });
    } catch (e) {
      toast.error(errorMessage(e));
    }
  };

  const deleteHistory = async (id: number) => {
    try {
      await api.delete(`/profile/medical-history/${id}`);
      toast.success("Entry deleted");
      queryClient.invalidateQueries({ queryKey: ["medical-history"] });
    } catch (e) {
      toast.error(errorMessage(e));
    }
  };

  const bloodGroups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"];

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Your Profile</h1>
        <p className="text-sm text-muted-foreground">
          Manage your personal details, health profile and security settings.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <UserRound className="h-5 w-5 text-primary" /> Personal information
            </CardTitle>
            <CardDescription>{profile?.email ?? user?.email}</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={saveProfile} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="full_name">Full name</Label>
                <Input id="full_name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="phone">Phone</Label>
                <Input id="phone" placeholder="+91…" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="preferred_language">Preferred language</Label>
                <Select
                  value={form.preferred_language}
                  onValueChange={(v) => setForm({ ...form, preferred_language: v })}
                >
                  <SelectTrigger id="preferred_language"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="hi">Hindi</SelectItem>
                    <SelectItem value="ta">Tamil</SelectItem>
                    <SelectItem value="te">Telugu</SelectItem>
                    <SelectItem value="bn">Bengali</SelectItem>
                    <SelectItem value="mr">Marathi</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button type="submit" disabled={saving}>
                {saving && <Loader2 className="h-4 w-4 animate-spin" />}
                Save changes
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Health profile</CardTitle>
            <CardDescription>Used to personalize AI analysis and recommendations.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={saveProfile} className="space-y-4">
              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="age">Age</Label>
                  <Input id="age" type="number" value={health.age} onChange={(e) => setHealth({ ...health, age: e.target.value })} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="height">Height (cm)</Label>
                  <Input id="height" type="number" value={health.height_cm} onChange={(e) => setHealth({ ...health, height_cm: e.target.value })} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="weight">Weight (kg)</Label>
                  <Input id="weight" type="number" value={health.weight_kg} onChange={(e) => setHealth({ ...health, weight_kg: e.target.value })} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="gender">Gender</Label>
                  <Input id="gender" value={health.gender} onChange={(e) => setHealth({ ...health, gender: e.target.value })} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="blood_group">Blood group</Label>
                  <Select value={health.blood_group || undefined} onValueChange={(v) => setHealth({ ...health, blood_group: v })}>
                    <SelectTrigger id="blood_group">
                      <SelectValue placeholder="Select" />
                    </SelectTrigger>
                    <SelectContent>
                      {bloodGroups.map((bg) => <SelectItem key={bg} value={bg}>{bg}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="medical_history">Medical history</Label>
                <Textarea id="medical_history" rows={2} value={health.medical_history} onChange={(e) => setHealth({ ...health, medical_history: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="allergies">Allergies</Label>
                <Input id="allergies" value={health.allergies} onChange={(e) => setHealth({ ...health, allergies: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="medications">Current medications</Label>
                <Textarea id="medications" rows={2} value={health.current_medications} onChange={(e) => setHealth({ ...health, current_medications: e.target.value })} />
              </div>
              <Button type="submit" variant="secondary" disabled={saving}>
                {saving && <Loader2 className="h-4 w-4 animate-spin" />}
                Save health profile
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <KeyRound className="h-5 w-5 text-primary" /> Change password
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={changePassword} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="current_password">Current password</Label>
                <Input id="current_password" type="password" value={pw.current_password} onChange={(e) => setPw({ ...pw, current_password: e.target.value })} required />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="new_password">New password</Label>
                  <Input id="new_password" type="password" value={pw.new_password} onChange={(e) => setPw({ ...pw, new_password: e.target.value })} required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirm">Confirm new password</Label>
                  <Input id="confirm" type="password" value={pw.confirm} onChange={(e) => setPw({ ...pw, confirm: e.target.value })} required />
                </div>
              </div>
              <Button type="submit" variant="outline" disabled={changingPw}>
                {changingPw && <Loader2 className="h-4 w-4 animate-spin" />}
                Update password
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Medical history entries</CardTitle>
            <CardDescription>Track chronic conditions with diagnosis year and notes.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <form onSubmit={addHistory} className="space-y-3 rounded-lg border p-3">
              <div className="space-y-2">
                <Label htmlFor="condition">Condition</Label>
                <Input id="condition" placeholder="e.g. Type 2 diabetes" value={newCondition.condition} onChange={(e) => setNewCondition({ ...newCondition, condition: e.target.value })} />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="year">Diagnosed year</Label>
                  <Input id="year" type="number" placeholder="e.g. 2019" value={newCondition.diagnosed_year} onChange={(e) => setNewCondition({ ...newCondition, diagnosed_year: e.target.value })} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="cond-notes">Notes</Label>
                  <Input id="cond-notes" value={newCondition.notes} onChange={(e) => setNewCondition({ ...newCondition, notes: e.target.value })} />
                </div>
              </div>
              <Button type="submit" size="sm">
                <Plus className="h-4 w-4" /> Add entry
              </Button>
            </form>
            {history && history.length === 0 && (
              <p className="text-sm text-muted-foreground">No entries yet.</p>
            )}
            <ul className="space-y-2">
              {history?.map((h) => (
                <li key={h.id} className="flex items-start justify-between gap-3 rounded-lg border p-3">
                  <div>
                    <p className="text-sm font-medium">{h.condition}</p>
                    <p className="text-xs text-muted-foreground">
                      {h.diagnosed_year ? `Diagnosed ${h.diagnosed_year}` : "Year unknown"}
                      {h.notes ? ` — ${h.notes}` : ""}
                    </p>
                  </div>
                  <button onClick={() => deleteHistory(h.id)} className="text-muted-foreground hover:text-destructive" aria-label="Delete entry">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
