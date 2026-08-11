"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bookmark, BookmarkCheck, Loader2, Pill, Search } from "lucide-react";
import { toast } from "sonner";
import { api, errorMessage } from "@/lib/api";
import type { MedicineOut, MedicineSearchResult } from "@/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

export default function MedicinePage() {
  const queryClient = useQueryClient();
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<MedicineSearchResult | null>(null);
  const [searching, setSearching] = useState(false);

  const { data: saved } = useQuery({
    queryKey: ["saved-medicines"],
    queryFn: async () => {
      const { data } = await api.get<{ data: Array<{ medicine_id: number; name: string; category?: string | null; purpose?: string | null }> }>("/medicine/saved/list");
      return data.data;
    },
  });

  const saveMutation = useMutation({
    mutationFn: async (medicineId: number) => {
      await api.post(`/medicine/${medicineId}/save`);
    },
    onSuccess: () => {
      toast.success("Saved to your medicine list");
      queryClient.invalidateQueries({ queryKey: ["saved-medicines"] });
    },
    onError: (e) => toast.error(errorMessage(e)),
  });

  const unsaveMutation = useMutation({
    mutationFn: async (medicineId: number) => {
      await api.delete(`/medicine/${medicineId}/save`);
    },
    onSuccess: () => {
      toast.success("Removed from saved list");
      queryClient.invalidateQueries({ queryKey: ["saved-medicines"] });
    },
    onError: (e) => toast.error(errorMessage(e)),
  });

  const isSaved = (id: number) => saved?.some((s) => s.medicine_id === id) ?? false;

  const search = async () => {
    const q = query.trim();
    if (q.length < 2) return;
    setSearching(true);
    setResult(null);
    try {
      const { data } = await api.get<{ data: MedicineOut[] }>("/medicine/search", { params: { q } });
      if (data.data.length > 0) {
        setResult({
          medicine: data.data[0],
          summary: null,
          disclaimer: "Educational information only. Not a substitute for professional medical advice.",
          model: "local-knowledge-base",
        });
        return;
      }
      const ai = await api.post<{ data: MedicineSearchResult }>("/medicine/search", { query: q });
      setResult(ai.data.data);
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      setSearching(false);
    }
  };

  const m = result?.medicine;
  const fields: Array<[string, string]> = [
    ["Generic name", m?.generic_name ?? ""],
    ["Category", m?.category ?? ""],
    ["Purpose", m?.purpose ?? ""],
    ["Uses", m?.uses ?? ""],
    ["Typical dosage", m?.dosage ?? ""],
    ["Warnings", m?.warnings ?? ""],
    ["Side effects", m?.side_effects ?? ""],
    ["Interactions", m?.interactions ?? ""],
    ["Storage", m?.storage ?? ""],
    ["Notes", m?.notes ?? ""],
  ].filter((f): f is [string, string] => Boolean(f[1]));

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Medicine Information</h1>
        <p className="text-sm text-muted-foreground">
          Search medicines — instant results from the local knowledge base, AI fallback for anything else.
        </p>
      </div>

      <div className="flex gap-2">
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && search()}
          placeholder="e.g. paracetamol, amoxicillin, metformin…"
          className="flex-1"
        />
        <Button onClick={search} disabled={searching || query.trim().length < 2}>
          {searching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
          Search
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          {!result && !searching && (
            <Card className="border-dashed p-8 text-center">
              <Pill className="mx-auto h-10 w-10 text-muted-foreground/40" />
              <p className="mt-2 text-sm text-muted-foreground">Search results will appear here.</p>
            </Card>
          )}
          {searching && (
            <Card className="flex items-center justify-center p-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </Card>
          )}
          {result && (
            <Card>
              <CardHeader>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <Pill className="h-5 w-5 text-primary" /> {m?.name ?? "AI summary"}
                      {result.model === "local-knowledge-base" && (
                        <Badge variant="success">Knowledge base</Badge>
                      )}
                    </CardTitle>
                    {m?.generic_name && (
                      <CardDescription className="mt-1">Generic: {m.generic_name}</CardDescription>
                    )}
                  </div>
                  {m && (
                    <Button
                      variant={isSaved(m.id) ? "default" : "outline"}
                      size="sm"
                      onClick={() => (isSaved(m.id) ? unsaveMutation.mutate(m.id) : saveMutation.mutate(m.id))}
                      disabled={saveMutation.isPending || unsaveMutation.isPending}
                    >
                      {isSaved(m.id) ? <BookmarkCheck className="h-4 w-4" /> : <Bookmark className="h-4 w-4" />}
                      {isSaved(m.id) ? "Saved" : "Save"}
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {result.summary && <p className="text-sm">{result.summary}</p>}
                {fields.map(([label, value]) => (
                  <div key={label}>
                    <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{label}</p>
                    <p className="mt-0.5 text-sm">{value}</p>
                  </div>
                ))}
                <p className="text-xs text-muted-foreground">{result.disclaimer}</p>
                <p className="text-[10px] text-muted-foreground">Source: {result.model}</p>
              </CardContent>
            </Card>
          )}
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Saved medicines</CardTitle>
            <CardDescription>Your quick-reference list</CardDescription>
          </CardHeader>
          <CardContent>
            {saved && saved.length === 0 && (
              <p className="text-sm text-muted-foreground">Nothing saved yet — tap Save on a medicine to add it here.</p>
            )}
            <ul className="space-y-3">
              {saved?.map((s) => (
                <li key={s.medicine_id} className="rounded-lg border p-3">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-medium">{s.name}</p>
                    <button
                      onClick={() => unsaveMutation.mutate(s.medicine_id)}
                      className="text-xs text-muted-foreground hover:text-destructive"
                    >
                      Remove
                    </button>
                  </div>
                  {s.category && <p className="mt-1 text-xs text-muted-foreground">{s.category}</p>}
                  {s.purpose && <p className="mt-0.5 text-xs text-muted-foreground">{s.purpose}</p>}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
