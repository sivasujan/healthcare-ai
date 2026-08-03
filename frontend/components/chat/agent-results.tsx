"use client";

import { AlertTriangle, ArrowRight, HeartPulse, Pill, ShieldAlert, Stethoscope } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

type AgentData = Record<string, unknown>;

function severityColor(severity: string) {
  switch (severity?.toLowerCase()) {
    case "low":
      return "text-emerald-600 dark:text-emerald-400";
    case "moderate":
      return "text-amber-600 dark:text-amber-400";
    case "high":
    case "critical":
      return "text-red-600 dark:text-red-400";
    default:
      return "text-muted-foreground";
  }
}

function severityBadge(severity: string) {
  const v = severity?.toLowerCase();
  if (v === "high" || v === "critical") return <Badge variant="danger">{severity}</Badge>;
  if (v === "moderate") return <Badge variant="warning">{severity}</Badge>;
  if (v === "low") return <Badge variant="success">{severity}</Badge>;
  return <Badge variant="secondary">{severity || "unknown"}</Badge>;
}

export function AgentResults({ data }: { data: AgentData }) {
  const conditions = data.possible_conditions as Array<{ name: string; confidence: number; severity: string }> | undefined;
  const recommendations = data.recommendations as Array<{ title: string; detail: string }> | undefined;
  const precautions = data.precautions as string[] | undefined;
  const fields = data.fields as Record<string, string> | undefined;
  const tips = data.preparation_tips as string[] | undefined;
  const instructions = data.instructions as string[] | undefined;
  const immediateActions = data.immediate_actions as string[] | undefined;
  const emergency = Boolean(data.emergency_detected);
  const disclaimer = (data.disclaimer as string) ?? "";

  if (emergency) {
    return (
      <div className="space-y-3 rounded-xl border-2 border-red-500 bg-red-50 p-4 dark:bg-red-950/30">
        <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
          <ShieldAlert className="h-5 w-5" />
          <p className="font-bold">POSSIBLE EMERGENCY DETECTED</p>
        </div>
        {instructions && (
          <ul className="space-y-1 text-sm">
            {instructions.map((i, idx) => (
              <li key={idx} className="flex gap-2">
                <ArrowRight className="mt-0.5 h-3.5 w-3.5 shrink-0 text-red-500" />
                <span>{i}</span>
              </li>
            ))}
          </ul>
        )}
        <p className="text-xs text-red-700 dark:text-red-300">{disclaimer}</p>
      </div>
    );
  }

  if (conditions) {
    return (
      <div className="space-y-4">
        <div className="flex flex-wrap items-center gap-2">
          <HeartPulse className="h-4 w-4 text-primary" />
          <p className="font-semibold">Possible conditions</p>
          {typeof data.overall_severity === "string" && (
            <span className={cn("text-sm font-medium", severityColor(String(data.overall_severity)))}>
              Overall severity: {severityBadge(String(data.overall_severity))}
            </span>
          )}        </div>
        <div className="space-y-3">
          {conditions.map((c, i) => (
            <div key={i}>
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">{c.name}</span>
                <span className={cn("text-xs font-medium", severityColor(c.severity))}>
                  {severityBadge(c.severity)} · {Math.round((c.confidence || 0) * 100)}%
                </span>
              </div>
              <Progress value={(c.confidence || 0) * 100} className="mt-1" />
            </div>
          ))}
        </div>
        {recommendations && recommendations.length > 0 && (
          <div>
            <p className="mb-2 text-sm font-semibold">Recommendations</p>
            <ul className="space-y-2">
              {recommendations.map((r, i) => (
                <li key={i} className="rounded-lg bg-muted/60 p-3 text-sm">
                  <p className="font-medium">{r.title}</p>
                  <p className="mt-0.5 text-muted-foreground">{r.detail}</p>
                </li>
              ))}
            </ul>
          </div>
        )}
        {precautions && precautions.length > 0 && (
          <div>
            <p className="mb-2 text-sm font-semibold">Precautions</p>
            <ul className="list-disc space-y-1 pl-5 text-sm text-muted-foreground">
              {precautions.map((p, i) => (
                <li key={i}>{p}</li>
              ))}
            </ul>
          </div>
        )}
        {(typeof data.doctor_specialty === "string" || typeof data.doctor_reason === "string") && (
          <div className="rounded-lg border border-primary/20 bg-primary/5 p-3 text-sm">
            <p className="flex items-center gap-2 font-semibold text-primary">
              <Stethoscope className="h-4 w-4" /> {String(data.doctor_specialty ?? "Consult a specialist")}
            </p>
            {typeof data.doctor_reason === "string" && <p className="mt-1 text-muted-foreground">{data.doctor_reason}</p>}
          </div>
        )}
        {disclaimer && <p className="text-xs text-muted-foreground">{disclaimer}</p>}
      </div>
    );
  }

  if (data.specialty) {
    return (
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Stethoscope className="h-4 w-4 text-primary" />
          <p className="font-semibold">{String(data.specialty)}</p>
        </div>
        {typeof data.reason === "string" && <p className="text-sm text-muted-foreground">{data.reason}</p>}
        <div className="flex flex-wrap gap-2">
          <Badge variant="info">{String(data.consultation_type ?? "in-person")}</Badge>
          <Badge variant="warning">Urgency: {String(data.urgency ?? "routine")}</Badge>
        </div>
        {tips && tips.length > 0 && (
          <div>
            <p className="mb-2 text-sm font-semibold">Preparation tips</p>
            <ul className="list-disc space-y-1 pl-5 text-sm text-muted-foreground">
              {tips.map((t, i) => (
                <li key={i}>{t}</li>
              ))}
            </ul>
          </div>
        )}
        {disclaimer && <p className="text-xs text-muted-foreground">{disclaimer}</p>}
      </div>
    );
  }

  if (fields) {
    const sections: Array<[string, string]> = [
      ["Purpose", fields.purpose ?? ""],
      ["Uses", fields.uses ?? ""],
      ["Typical dosage", fields.dosage ?? ""],
      ["Warnings", fields.warnings ?? ""],
      ["Side effects", fields.side_effects ?? ""],
      ["Interactions", fields.interactions ?? ""],
      ["Storage", fields.storage ?? ""],
      ["Important notes", fields.notes ?? ""],
    ].filter(([, v]) => v) as Array<[string, string]>;

    return (
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Pill className="h-4 w-4 text-primary" />
          <p className="font-semibold">Medicine information</p>
        </div>
        {typeof data.summary === "string" && <p className="text-sm">{data.summary}</p>}
        {sections.map(([label, value]) => (
          <div key={label}>
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{label}</p>
            <p className="mt-0.5 text-sm">{value}</p>
          </div>
        ))}
        {disclaimer && <p className="text-xs text-muted-foreground">{disclaimer}</p>}
      </div>
    );
  }

  if (instructions && instructions.length > 0 && !disclaimer.includes("educational")) {
    return (
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-amber-500" />
          <p className="font-semibold">Instructions</p>
        </div>
        <ul className="space-y-1 text-sm">
          {instructions.map((i, idx) => (
            <li key={idx} className="flex gap-2">
              <ArrowRight className="mt-0.5 h-3.5 w-3.5 shrink-0" />
              <span>{i}</span>
            </li>
          ))}
        </ul>
        {immediateActions && immediateActions.length > 0 && (
          <div className="rounded-lg border border-amber-500/30 bg-amber-50 p-3 dark:bg-amber-950/30">
            <p className="mb-1 text-sm font-semibold text-amber-700 dark:text-amber-300">
              Immediate actions
            </p>
            <ul className="list-disc space-y-1 pl-5 text-sm text-amber-800 dark:text-amber-200">
              {immediateActions.map((a, i) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
          </div>
        )}
        {disclaimer && <p className="text-xs text-muted-foreground">{disclaimer}</p>}
      </div>
    );
  }

  return null;
}
