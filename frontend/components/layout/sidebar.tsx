"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  CalendarDays,
  HeartPulse,
  LayoutDashboard,
  MessageSquare,
  Pill,
  ShieldAlert,
  Stethoscope,
  User,
  Users,
  Settings,
  LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { initials } from "@/lib/utils";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

const PATIENT_LINKS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/chat", label: "AI Chat", icon: MessageSquare },
  { href: "/dashboard/symptom", label: "Symptom Analysis", icon: HeartPulse },
  { href: "/dashboard/medicine", label: "Medicine Info", icon: Pill },
  { href: "/dashboard/doctor", label: "Find a Doctor", icon: Stethoscope },
  { href: "/dashboard/emergency", label: "Emergency Check", icon: ShieldAlert },
  { href: "/dashboard/appointments", label: "Appointments", icon: CalendarDays },
  { href: "/dashboard/profile", label: "Profile", icon: User },
];

const ADMIN_LINKS = [
  { href: "/dashboard/admin", label: "Admin Panel", icon: Users },
];

export function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  const links = user?.is_admin ? [...PATIENT_LINKS, ...ADMIN_LINKS] : PATIENT_LINKS;

  const handleLogout = async () => {
    await logout();
    toast.success("Logged out");
    router.push("/");
  };

  const content = (
    <div className="flex h-full flex-col">
      <Link href="/dashboard" className="flex h-16 items-center gap-2 border-b px-5">
        <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground">
          <Activity className="h-5 w-5" />
        </span>
        <span className="text-lg font-bold tracking-tight">
          Medi<span className="text-primary">Assist</span>
        </span>
      </Link>

      <nav className="flex-1 space-y-1 overflow-y-auto p-3">
        <p className="px-3 pb-1 pt-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
          Main
        </p>
        {links.map((link) => {
          const active = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              onClick={onClose}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                active
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground"
              )}
            >
              <link.icon className="h-4 w-4 shrink-0" />
              {link.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t p-3">
        <div className="flex items-center gap-3 rounded-lg px-2 py-2">
          <Avatar className="h-9 w-9">
            <AvatarFallback>{initials(user?.full_name ?? "U")}</AvatarFallback>
          </Avatar>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">{user?.full_name}</p>
            <p className="truncate text-xs text-muted-foreground">{user?.email}</p>
          </div>
        </div>
        <div className="mt-1 flex gap-1">
          <Button variant="ghost" size="sm" className="flex-1 justify-start" asChild>
            <Link href="/dashboard/profile">
              <Settings className="h-4 w-4" /> Settings
            </Link>
          </Button>
          <Button variant="ghost" size="sm" className="flex-1 justify-start text-destructive hover:text-destructive" onClick={handleLogout}>
            <LogOut className="h-4 w-4" /> Logout
          </Button>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop */}
      <aside className="hidden w-64 shrink-0 border-r bg-card lg:block">{content}</aside>
      {/* Mobile drawer */}
      {open && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/60" onClick={onClose} />
          <aside className="absolute left-0 top-0 h-full w-72 border-r bg-card shadow-xl">{content}</aside>
        </div>
      )}
    </>
  );
}
