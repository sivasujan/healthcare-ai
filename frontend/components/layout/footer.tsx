import Link from "next/link";
import { Activity, HeartPulse } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t bg-card">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6">
        <div className="grid gap-8 md:grid-cols-4">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2">
              <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground">
                <Activity className="h-5 w-5" />
              </span>
              <span className="text-lg font-bold">
                Medi<span className="text-primary">Assist</span>
              </span>
            </div>
            <p className="mt-3 max-w-sm text-sm text-muted-foreground">
              An intelligent multi-agent AI healthcare assistant. Analyze symptoms,
              learn about medicines, find the right specialist, and detect emergencies —
              all locally, privately, and responsibly.
            </p>
            <div className="mt-4 flex items-center gap-2 text-sm text-muted-foreground">
              <HeartPulse className="h-4 w-4 text-primary" />
              Educational purposes only. Not a substitute for professional medical care.
            </div>
          </div>
          <div>
            <h4 className="mb-3 text-sm font-semibold">Product</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><Link href="/#features" className="hover:text-foreground">Features</Link></li>
              <li><Link href="/#agents" className="hover:text-foreground">AI Agents</Link></li>
              <li><Link href="/#how-it-works" className="hover:text-foreground">How it works</Link></li>
              <li><Link href="/#faq" className="hover:text-foreground">FAQ</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="mb-3 text-sm font-semibold">Get started</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><Link href="/register" className="hover:text-foreground">Create account</Link></li>
              <li><Link href="/login" className="hover:text-foreground">Sign in</Link></li>
              <li><Link href="/dashboard" className="hover:text-foreground">Dashboard</Link></li>
              <li><Link href="/dashboard/chat" className="hover:text-foreground">AI Chat</Link></li>
            </ul>
          </div>
        </div>
        <div className="mt-10 border-t pt-6 text-center text-xs text-muted-foreground">
          © {new Date().getFullYear()} MediAssist. Built with Next.js, FastAPI, LangGraph and OpenRouter.
        </div>
      </div>
    </footer>
  );
}
