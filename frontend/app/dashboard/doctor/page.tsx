"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Hospital, Loader2, Stethoscope } from "lucide-react";
import { toast } from "sonner";
import { api, errorMessage } from "@/lib/api";
import type { DoctorRecommendationResult } from "@/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";

const schema = z.object({
  symptoms: z.string().min(3, "Describe your symptoms (at least 3 characters)"),
  age: z.string().optional(),
  gender: z.string().optional(),
  medical_history: z.string().optional(),
  current_medications: z.string().optional(),
});

type Values = z.infer<typeof schema>;

export default function DoctorPage() {
  const [result, setResult] = useState<DoctorRecommendationResult | null>(null);
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
      const { data } = await api.post<{ data: DoctorRecommendationResult }>("/doctor/recommend", {
        symptoms: values.symptoms,
        age: values.age ? Number(values.age) : undefined,
        gender: values.gender || undefined,
        medical_history: values.medical_history || undefined,
        current_medications: values.current_medications || undefined,
      });
      setResult(data.data);
      toast.success("Recommendation ready");
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Find the Right Doctor</h1>
        <p className="text-sm text-muted-foreground">
          Describe your symptoms and get a recommended specialty, consultation type, urgency and prep tips.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Stethoscope className="h-5 w-5 text-primary" /> Your symptoms
            </CardTitle>
            <CardDescription>All fields optional except symptoms.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="symptoms">Symptoms *</Label>
                <Textarea
                  id="symptoms"
                  rows={4}
                  placeholder="e.g. Persistent headache with blurred vision and dizziness…"
                  {...register("symptoms")}
                />
                {errors.symptoms && <p className="text-xs text-destructive">{errors.symptoms.message}</p>}
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="age">Age</Label>
                  <Input id="age" type="number" placeholder="e.g. 45" {...register("age")} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="gender">Gender</Label>
                  <Input id="gender" placeholder="Male / Female / Other" {...register("gender")} />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="medical_history">Medical history</Label>
                <Textarea id="medical_history" rows={2} placeholder="e.g. Hypertension, asthma…" {...register("medical_history")} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="current_medications">Current medications</Label>
                <Input id="current_medications" placeholder="e.g. Losartan, inhaler…" {...register("current_medications")} />
              </div>
              <Button type="submit" className="w-full" size="lg" disabled={loading}>
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Stethoscope className="h-4 w-4" />}
                {loading ? "Finding doctor…" : "Get recommendation"}
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="space-y-4">
          {!result && !loading && (
            <Card className="flex h-full items-center justify-center border-dashed p-8 text-center">
              <Stethoscope className="mx-auto h-10 w-10 text-muted-foreground/40" />
              <p className="mt-2 text-sm text-muted-foreground">Your recommendation will appear here.</p>
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
                <CardTitle className="text-base">{result.specialty}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">{result.reason}</p>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="info">{result.consultation_type}</Badge>
                  <Badge variant={result.urgency === "emergency" ? "danger" : result.urgency === "urgent" ? "warning" : "secondary"}>
                    Urgency: {result.urgency}
                  </Badge>
                </div>
                {result.preparation_tips.length > 0 && (
                  <div>
                    <p className="mb-2 text-sm font-semibold">Preparation tips</p>
                    <ul className="list-disc space-y-1 pl-5 text-sm text-muted-foreground">
                      {result.preparation_tips.map((t, i) => <li key={i}>{t}</li>)}
                    </ul>
                  </div>
                )}
                {result.nearby_hospitals.length > 0 && (
                  <div>
                    <p className="mb-2 flex items-center gap-1.5 text-sm font-semibold">
                      <Hospital className="h-4 w-4 text-primary" /> Nearby hospitals
                    </p>
                    <ul className="space-y-1 text-sm text-muted-foreground">
                      {result.nearby_hospitals.map((h, i) => <li key={i}>• {h}</li>)}
                    </ul>
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
