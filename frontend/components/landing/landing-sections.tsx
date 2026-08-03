"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import {
  ArrowRight,
  Bot,
  CalendarDays,
  HeartPulse,
  MessageSquare,
  Pill,
  ShieldAlert,
  Sparkles,
  Stethoscope,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth";

const fadeUp = {
  initial: { opacity: 0, y: 24 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-80px" },
  transition: { duration: 0.5 },
};

export function Hero() {
  const { isAuthenticated } = useAuth();

  return (
    <section className="relative overflow-hidden pb-20 pt-16 sm:pt-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
              className="mb-6 inline-flex items-center gap-2 rounded-full border bg-card px-4 py-1.5 text-xs font-medium shadow-sm"
            >
              <Sparkles className="h-3.5 w-3.5 text-primary" />
              Multi-Agent AI Healthcare Assistant
            </motion.div>
            <h1 className="text-4xl font-bold leading-tight tracking-tight sm:text-5xl lg:text-6xl">
              Your AI health companion,{" "}
              <span className="bg-gradient-to-r from-blue-600 to-indigo-500 bg-clip-text text-transparent">
                available 24/7
              </span>
            </h1>
            <p className="mt-5 max-w-xl text-lg text-muted-foreground">
              Analyze symptoms, understand medicines, find the right specialist, and get
              emergency guidance — powered by intelligent AI agents that never replace
              professional medical care.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Button size="lg" asChild>
                <Link href={isAuthenticated ? "/dashboard/chat" : "/register"}>
                  {isAuthenticated ? "Open AI Chat" : "Get started free"} <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <Link href="#features">Explore features</Link>
              </Button>
            </div>
            <div className="mt-8 flex items-center gap-6 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <span className="flex h-2 w-2 rounded-full bg-emerald-500" /> 100% local & private
              </div>
              <div className="flex items-center gap-2">
                <span className="flex h-2 w-2 rounded-full bg-emerald-500" /> SQLite only
              </div>
              <div className="flex items-center gap-2">
                <span className="flex h-2 w-2 rounded-full bg-emerald-500" /> No cloud required
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 32 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="relative"
          >
            <div className="rounded-2xl border bg-card/80 p-6 shadow-2xl backdrop-blur">
              <div className="flex items-center gap-3 border-b pb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
                  <Bot className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm font-semibold">Symptom Analysis Agent</p>
                  <p className="text-xs text-muted-foreground">gemma-4-26b-a4b-it:free</p>
                </div>
              </div>
              <div className="space-y-4 py-4">
                <div className="flex justify-end">
                  <div className="rounded-2xl rounded-br-sm bg-primary px-4 py-2.5 text-sm text-primary-foreground">
                    I have a persistent headache and mild fever for 2 days
                  </div>
                </div>
                <div className="flex justify-start">
                  <div className="max-w-sm rounded-2xl rounded-bl-sm border bg-muted/50 px-4 py-3 text-sm">
                    <p className="mb-2 font-medium text-primary">Possible conditions</p>
                    <ul className="space-y-1 text-muted-foreground">
                      <li>• Viral infection (60% confidence, low severity)</li>
                      <li>• Tension headache (20%)</li>
                      <li>• Sinusitis (20%)</li>
                    </ul>
                    <p className="mt-3 text-xs text-muted-foreground">
                      Recommendation: consult a General Practitioner if symptoms persist
                      beyond 3 days.
                    </p>
                  </div>
                </div>
              </div>
              <div className="flex items-center justify-between border-t pt-4 text-xs text-muted-foreground">
                <span className="flex items-center gap-1.5"><ShieldAlert className="h-3.5 w-3.5 text-red-500" /> Emergency-aware</span>
                <span className="flex items-center gap-1.5"><Pill className="h-3.5 w-3.5" /> Never prescribes</span>
              </div>
            </div>
            <motion.div
              className="absolute -right-4 -top-4 rounded-xl border bg-card px-4 py-3 shadow-lg"
              animate={{ y: [0, -8, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            >
              <p className="text-xs font-medium text-muted-foreground">Emergency detected?</p>
              <p className="text-sm font-semibold text-red-600">Chest pain → Call 911</p>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

export function FeatureCards() {
  const features = [
    {
      icon: MessageSquare,
      title: "AI Chat Assistant",
      desc: "A ChatGPT-style conversational interface with streaming responses, markdown, tables and code blocks.",
    },
    {
      icon: HeartPulse,
      title: "Symptom Analysis",
      desc: "Describe your symptoms and get possible conditions with confidence scores, severity and precautions.",
    },
    {
      icon: Pill,
      title: "Medicine Information",
      desc: "Educational info about purpose, dosage, side effects, interactions and storage — never prescriptions.",
    },
    {
      icon: Stethoscope,
      title: "Doctor Recommendations",
      desc: "Find the right medical specialty with reasoning, consultation type and preparation tips.",
    },
    {
      icon: ShieldAlert,
      title: "Emergency Detection",
      desc: "Red-flag detection for chest pain, stroke signs, breathing difficulty and more, with immediate advice.",
    },
    {
      icon: CalendarDays,
      title: "Appointments",
      desc: "Book, reschedule and cancel appointments with calendar views and confirmation screens.",
    },
  ];

  return (
    <section id="features" className="relative py-20">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <motion.div {...fadeUp} className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Everything you need, one assistant</h2>
          <p className="mt-4 text-muted-foreground">
            Six specialized AI agents working together through a single LangGraph pipeline.
          </p>
        </motion.div>
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.08 }}
              className="group rounded-2xl border bg-card p-6 shadow-sm transition-all hover:-translate-y-1 hover:shadow-lg"
            >
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-primary-foreground">
                <f.icon className="h-5 w-5" />
              </div>
              <h3 className="mt-4 text-lg font-semibold">{f.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

export function HowItWorks() {
  const steps = [
    { n: "01", title: "You describe your concern", desc: "Type symptoms, a medicine name, or a general health question in natural language." },
    { n: "02", title: "Intent detection routes you", desc: "A LangGraph pipeline classifies your message and routes it to the right specialist agent." },
    { n: "03", title: "The agent consults the model router", desc: "Each agent calls a central Model Router with automatic fallback between three AI models." },
    { n: "04", title: "Structured, safe answers", desc: "You receive clear guidance with confidence scores, disclaimers and next steps." },
  ];

  return (
    <section id="how-it-works" className="relative py-20">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <motion.div {...fadeUp} className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">How it works</h2>
          <p className="mt-4 text-muted-foreground">From question to answer in four steps.</p>
        </motion.div>
        <div className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {steps.map((s, i) => (
            <motion.div
              key={s.n}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className="relative rounded-2xl border bg-card p-6"
            >
              <span className="text-4xl font-bold text-primary/20">{s.n}</span>
              <h3 className="mt-3 font-semibold">{s.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{s.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

export function AgentShowcase() {
  const agents = [
    { name: "Symptom Analysis", icon: HeartPulse, desc: "Conditions, severity, precautions", color: "text-sky-500" },
    { name: "Medicine Info", icon: Pill, desc: "Uses, dosage, interactions", color: "text-violet-500" },
    { name: "Doctor Recommender", icon: Stethoscope, desc: "Specialty + preparation tips", color: "text-emerald-500" },
    { name: "Emergency Detection", icon: ShieldAlert, desc: "Red flags, first aid, 911", color: "text-red-500" },
    { name: "Appointment Agent", icon: CalendarDays, desc: "Book, reschedule, remind", color: "text-amber-500" },
    { name: "General Chat", icon: Bot, desc: "Wellness questions & more", color: "text-indigo-500" },
  ];

  return (
    <section id="agents" className="relative py-20">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <motion.div {...fadeUp} className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Meet the agents</h2>
          <p className="mt-4 text-muted-foreground">
            Six specialist agents, one orchestrated LangGraph workflow.
          </p>
        </motion.div>
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {agents.map((a, i) => (
            <motion.div
              key={a.name}
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.4, delay: i * 0.07 }}
              className="flex items-center gap-4 rounded-2xl border bg-card p-5 transition-colors hover:border-primary/40"
            >
              <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-muted ${a.color}`}>
                <a.icon className="h-5 w-5" />
              </div>
              <div>
                <p className="font-semibold">{a.name}</p>
                <p className="text-sm text-muted-foreground">{a.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

export function Stats() {
  const stats = [
    { value: "6", label: "Specialist AI agents" },
    { value: "3", label: "Fallback model tiers" },
    { value: "10+", label: "REST API endpoints" },
    { value: "0", label: "Cloud dependencies" },
  ];

  return (
    <section className="relative py-14">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <div className="animated-gradient rounded-3xl p-8 text-white sm:p-12">
          <div className="grid gap-8 text-center sm:grid-cols-2 lg:grid-cols-4">
            {stats.map((s, i) => (
              <motion.div
                key={s.label}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.08 }}
              >
                <p className="text-4xl font-bold">{s.value}</p>
                <p className="mt-1 text-sm text-white/80">{s.label}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

export function Testimonials() {
  const items = [
    {
      quote: "The symptom analysis gave me clear guidance and pointed me to a GP before my issue escalated.",
      name: "Rahul M.",
      role: "Regular user",
    },
    {
      quote: "I love that everything runs locally. My health data never leaves my machine.",
      name: "Priya S.",
      role: "Privacy-conscious user",
    },
    {
      quote: "The emergency detection flags are smart — it correctly told me chest pain needed urgent care.",
      name: "Dr. Anita K.",
      role: "General Practitioner",
    },
  ];

  return (
    <section className="relative py-20">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <motion.div {...fadeUp} className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Trusted by users</h2>
          <p className="mt-4 text-muted-foreground">What people say about MediAssist.</p>
        </motion.div>
        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {items.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className="rounded-2xl border bg-card p-6 shadow-sm"
            >
              <p className="text-muted-foreground">&ldquo;{t.quote}&rdquo;</p>
              <div className="mt-4 flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
                  {t.name[0]}
                </div>
                <div>
                  <p className="text-sm font-medium">{t.name}</p>
                  <p className="text-xs text-muted-foreground">{t.role}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

export function Faq() {
  const faqs = [
    {
      q: "Is MediAssist a replacement for a doctor?",
      a: "No. MediAssist is an educational assistant. It never diagnoses diseases or prescribes medicines, and always recommends consulting a qualified healthcare professional.",
    },
    {
      q: "Where is my health data stored?",
      a: "Everything runs locally. Your data is stored in a local SQLite database on your machine — no cloud database is used.",
    },
    {
      q: "Which AI models power the assistant?",
      a: "A central Model Router chooses between three model tiers (primary, secondary, fallback). The default configuration uses free OpenRouter models.",
    },
    {
      q: "What happens if I report emergency symptoms?",
      a: "The Emergency Detection Agent flags red-flag symptoms like chest pain or stroke signs and immediately instructs you to call emergency services.",
    },
    {
      q: "Can I use voice input?",
      a: "Yes, the AI chat supports voice input through the Web Speech API in supported browsers.",
    },
  ];

  return (
    <section id="faq" className="relative py-20">
      <div className="mx-auto max-w-3xl px-4 sm:px-6">
        <motion.div {...fadeUp} className="text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Frequently asked questions</h2>
        </motion.div>
        <div className="mt-10 space-y-4">
          {faqs.map((f, i) => (
            <motion.details
              key={f.q}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{ duration: 0.4, delay: i * 0.05 }}
              className="group rounded-xl border bg-card p-5 [&_summary::-webkit-details-marker]:hidden"
            >
              <summary className="flex cursor-pointer items-center justify-between font-medium">
                {f.q}
                <span className="text-primary transition-transform group-open:rotate-45">+</span>
              </summary>
              <p className="mt-3 text-sm text-muted-foreground">{f.a}</p>
            </motion.details>
          ))}
        </div>
      </div>
    </section>
  );
}
