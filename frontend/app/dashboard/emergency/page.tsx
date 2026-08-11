"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { AlertTriangle, CheckCircle2, Loader2, Phone, Siren } from "lucide-react";
import { toast } from "sonner";
import { api, errorMessage } from "@/lib/api";
import type { EmergencyCheckResult } from "@/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";

const schema = z.object({
  symptoms: z.string().min(3, "Describe what you're feeling (at least 3 characters)"),
  age: z.string().optional(),
  medical_history: z.string().optional(),
  current_medications: z.string().optional(),
});

type Values = z.infer<typeof schema>;

export default function EmergencyPage() {
  const [result, setResult] = useState<EmergencyCheckResult | null>(null);
  const [loading, setLoading] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<Values>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: Values) => {
    setLoading(true);
    setResult(null);
    try {
      const { data } = await api.post<{ data: EmergencyCheckResult }>("/emergency/check", {
        symptoms: values.symptoms,
        age: values.age ? Number(values.age) : undefined,
        medical_history: values.medical_history || undefined,
        current_medications: values.current_medications || undefined,
      });
      setResult(data.data);
      if (data.data.emergency_detected) {
        toast.warning("Possible emergency indicators detected", { duration: 8000 });
      } else {
        toast.success("No emergency indicators found");
      }
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Emergency Check</h1>
        <p className="text-sm text-muted-foreground">
          Check your symptoms for red-flag warning signs and get immediate action guidance.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Siren className="h-5 w-5 text-red-500" /> What are you experiencing?
            </CardTitle>
            <CardDescription>Be honest and specific — this check is for red-flag symptoms.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="symptoms">Symptoms *</Label>
                <Textarea
                  id="symptoms"
                  rows={4}
                  placeholder="e.g. Sudden severe chest pain, difficulty breathing, left arm pain…"
                  {...register("symptoms")}
                />
                {errors.symptoms && <p className="text-xs text-destructive">{errors.symptoms.message}</p>}
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="age">Age</Label>
                  <Input id="age" type="number" placeholder="e.g. 60" {...register("age")} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="medical_history">Medical history</Label>
                  <Input id="medical_history" placeholder="e.g. Heart disease, diabetes…" {...register("medical_history")} />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="current_medications">Current medications</Label>
                <Input id="current_medications" placeholder="e.g. Blood thinners…" {...register("current_medications")} />
              </div>
              <Button type="submit" className="w-full" size="lg" disabled={loading}>
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Siren className="h-4 w-4" />}
                {loading ? "Checking…" : "Check for emergency signs"}
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="space-y-4">
          {!result && !loading && (
            <Card className="flex h-full items-center justify-center border-dashed p-8 text-center">
              <Siren className="mx-auto h-10 w-10 text-muted-foreground/40" />
              <p className="mt-2 text-sm text-muted-foreground">Check results will appear here.</p>
            </Card>
          )}
          {loading && (
            <Card className="flex h-full items-center justify-center p-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </Card>
          )}
          {result && (
            <Card
              className={
                result.emergency_detected
                  ? "border-2 border-red-500 bg-red-50/60 dark:bg-red-950/20"
                  : undefined
              }
            >
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  {result.emergency_detected ? (
                    <>
                      <AlertTriangle className="h-5 w-5 text-red-600" /> Possible emergency
                    </>
                  ) : (
                    <>
                      <CheckCircle2 className="h-5 w-5 text-emerald-600" /> No emergency indicators
                    </>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {result.emergency_detected && (
                  <>
                    <Badge variant="danger">Severity: {result.severity}</Badge>
                    {result.conditions.length > 0 && (
                      <ul className="list-disc space-y-1 pl-5 text-sm">
                        {result.conditions.map((c, i) => <li key={i}>{c}</li>)}
                      </ul>
                    )}
                    <div className="rounded-lg border border-red-500/40 bg-red-500/10 p-3">
                      <p className="mb-1 flex items-center gap-1.5 text-sm font-semibold text-red-700 dark:text-red-300">
                        <AlertTriangle className="h-4 w-4" /> Immediate actions
                      </p>
                      <ul className="list-disc space-y-1 pl-5 text-sm text-red-800 dark:text-red-200">
                        {result.immediate_actions.map((a, i) => <li key={i}>{a}</li>)}
                      </ul>
                    </div>
                  </>
                )}
                {result.instructions.length > 0 && (
                  <div>
                    <p className="mb-2 text-sm font-semibold">Instructions</p>
                    <ul className="space-y-1 text-sm text-muted-foreground">
                      {result.instructions.map((ins, i) => (
                        <li key={i} className="flex gap-2">
                          <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-500" />
                          <span>{ins}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {result.nearby_hospitals.length > 0 && (
                  <div>
                    <p className="mb-1 text-sm font-semibold">Nearby hospitals</p>
                    <ul className="space-y-1 text-sm text-muted-foreground">
                      {result.nearby_hospitals.map((h, i) => <li key={i}>• {h}</li>)}
                    </ul>
                  </div>
                )}
                <div className="flex items-center gap-2 rounded-lg bg-muted/60 p-3">
                  <Phone className="h-4 w-4 text-primary" />
                  <p className="text-sm font-medium">Emergency number: {result.emergency_number}</p>
                </div>
                <p className="text-xs text-muted-foreground">{result.disclaimer}</p>
                <p className="text-[10px] text-muted-foreground">Model: {result.model}</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
