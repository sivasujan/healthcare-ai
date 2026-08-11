"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { HeartPulse, Loader2, Stethoscope } from "lucide-react";
import { toast } from "sonner";
import { api, errorMessage } from "@/lib/api";
import type { SymptomAnalysisResult } from "@/types";
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
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

const schema = z.object({
  symptoms: z.string().min(3, "Describe your symptoms (at least 3 characters)"),
  age: z.string().optional(),
  gender: z.string().optional(),
  duration: z.string().optional(),
  medical_history: z.string().optional(),
  current_medications: z.string().optional(),
  allergies: z.string().optional(),
  lifestyle: z.string().optional(),
  smoking: z.string().optional(),
  alcohol: z.string().optional(),
  exercise: z.string().optional(),
});

type Values = z.infer<typeof schema>;

function severityBadge(severity: string) {
  const v = severity.toLowerCase();
  if (v === "high" || v === "critical") return <Badge variant="danger">{severity}</Badge>;
  if (v === "moderate") return <Badge variant="warning">{severity}</Badge>;
  return <Badge variant="secondary">{severity}</Badge>;
}

export default function SymptomPage() {
  const [result, setResult] = useState<SymptomAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<Values>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: Values) => {
    setLoading(true);
    setResult(null);
    try {
      const { data } = await api.post<{ data: SymptomAnalysisResult }>("/symptom/analyze", {
        symptoms: values.symptoms,
        age: values.age ? Number(values.age) : undefined,
        gender: values.gender || undefined,
        duration: values.duration || undefined,
        medical_history: values.medical_history || undefined,
        current_medications: values.current_medications || undefined,
        allergies: values.allergies || undefined,
        lifestyle: values.lifestyle || undefined,
        smoking: values.smoking || undefined,
        alcohol: values.alcohol || undefined,
        exercise: values.exercise || undefined,
      });
      setResult(data.data);
      toast.success("Analysis complete");
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  const selectProps = (name: keyof Values) => ({
    value: watch(name) || undefined,
    onValueChange: (v: string) => setValue(name, v),
  });

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Symptom Analyzer</h1>
        <p className="text-sm text-muted-foreground">
          Describe your symptoms for an AI-powered assessment with possible conditions, severity and recommendations.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <HeartPulse className="h-5 w-5 text-primary" /> Describe your symptoms
            </CardTitle>
            <CardDescription>All fields optional except symptoms. More detail = better analysis.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="symptoms">Symptoms *</Label>
                <Textarea
                  id="symptoms"
                  rows={4}
                  placeholder="e.g. Fever, headache and body ache since 2 days, mild cough…"
                  {...register("symptoms")}
                />
                {errors.symptoms && <p className="text-xs text-destructive">{errors.symptoms.message}</p>}
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="age">Age</Label>
                  <Input id="age" type="number" placeholder="e.g. 32" {...register("age")} />
                </div>
                <div className="space-y-2">
                  <Label>Gender</Label>
                  <Select {...selectProps("gender")}>
                    <SelectTrigger><SelectValue placeholder="Select" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="male">Male</SelectItem>
                      <SelectItem value="female">Female</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="duration">How long have you had symptoms?</Label>
                <Input id="duration" placeholder="e.g. Since 2 days, intermittent for a week…" {...register("duration")} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="medical_history">Medical history</Label>
                <Textarea id="medical_history" rows={2} placeholder="e.g. Diabetes (type 2), high BP…" {...register("medical_history")} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="current_medications">Current medications</Label>
                <Input id="current_medications" placeholder="e.g. Metformin 500mg, amlodipine…" {...register("current_medications")} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="allergies">Allergies</Label>
                <Input id="allergies" placeholder="e.g. Penicillin, peanuts…" {...register("allergies")} />
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-2">
                  <Label>Smoking</Label>
                  <Select {...selectProps("smoking")}>
                    <SelectTrigger><SelectValue placeholder="No" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="no">No</SelectItem>
                      <SelectItem value="occasionally">Occasionally</SelectItem>
                      <SelectItem value="daily">Daily</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Alcohol</Label>
                  <Select {...selectProps("alcohol")}>
                    <SelectTrigger><SelectValue placeholder="No" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="no">No</SelectItem>
                      <SelectItem value="occasionally">Occasionally</SelectItem>
                      <SelectItem value="daily">Daily</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Exercise</Label>
                  <Select {...selectProps("exercise")}>
                    <SelectTrigger><SelectValue placeholder="Regular" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">None</SelectItem>
                      <SelectItem value="occasionally">Occasionally</SelectItem>
                      <SelectItem value="regular">Regular</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <Button type="submit" className="w-full" size="lg" disabled={loading}>
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <HeartPulse className="h-4 w-4" />}
                {loading ? "Analyzing…" : "Analyze symptoms"}
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="space-y-4">
          {!result && !loading && (
            <Card className="flex h-full items-center justify-center border-dashed p-8 text-center">
              <div className="space-y-2">
                <HeartPulse className="mx-auto h-10 w-10 text-muted-foreground/40" />
                <p className="text-sm text-muted-foreground">
                  Your analysis will appear here. Not a diagnosis — educational guidance only.
                </p>
              </div>
            </Card>
          )}
          {loading && (
            <Card className="flex h-full items-center justify-center p-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </Card>
          )}
          {result && (
            <Card>
              <CardHeader>
                <CardTitle className="flex flex-wrap items-center gap-2 text-base">
                  <Stethoscope className="h-5 w-5 text-primary" /> Possible conditions
                  <span className={cn("text-sm font-medium")}>
                    Severity: {severityBadge(result.overall_severity)}
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {result.possible_conditions.map((c, i) => (
                  <div key={i}>
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium">{c.name}</span>
                      <span className="text-xs text-muted-foreground">
                        {severityBadge(c.severity)} · {Math.round(c.confidence * 100)}%
                      </span>
                    </div>
                    <Progress value={c.confidence * 100} className="mt-1" />
                  </div>
                ))}
                {result.recommendations.length > 0 && (
                  <div>
                    <p className="mb-2 text-sm font-semibold">Recommendations</p>
                    <ul className="space-y-2">
                      {result.recommendations.map((r, i) => (
                        <li key={i} className="rounded-lg bg-muted/60 p-3 text-sm">
                          <p className="font-medium">{r.title}</p>
                          <p className="mt-0.5 text-muted-foreground">{r.detail}</p>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {result.precautions.length > 0 && (
                  <div>
                    <p className="mb-2 text-sm font-semibold">Precautions</p>
                    <ul className="list-disc space-y-1 pl-5 text-sm text-muted-foreground">
                      {result.precautions.map((p, i) => <li key={i}>{p}</li>)}
                    </ul>
                  </div>
                )}
                {result.doctor_specialty && (
                  <div className="rounded-lg border border-primary/20 bg-primary/5 p-3 text-sm">
                    <p className="flex items-center gap-2 font-semibold text-primary">
                      <Stethoscope className="h-4 w-4" /> {result.doctor_specialty}
                    </p>
                    {result.doctor_reason && <p className="mt-1 text-muted-foreground">{result.doctor_reason}</p>}
                  </div>
                )}
                {result.emergency_detected && (
                  <div className="rounded-lg border-2 border-red-500 bg-red-50 p-3 text-sm dark:bg-red-950/30">
                    <p className="font-semibold text-red-600 dark:text-red-400">
                      Possible emergency indicators — seek medical help immediately.
                    </p>
                    {result.emergency_instructions && (
                      <ul className="mt-2 list-disc space-y-1 pl-5 text-red-700 dark:text-red-300">
                        {result.emergency_instructions.map((ins, i) => <li key={i}>{ins}</li>)}
                      </ul>
                    )}
                  </div>
                )}
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
