"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, errorMessage, tokenStore } from "@/lib/api";
import type { AuthResponse, Profile, User } from "@/types";

interface AuthContextValue {
  user: User | null;
  profile: Profile | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (fullName: string, email: string, password: string, phone?: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (tokenStore.getAccess()) {
      api
        .get("/profile")
        .then((res) => {
          setProfile(res.data.data);
          setUser(res.data.data);
        })
        .catch(() => tokenStore.clear())
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const { data } = await api.post<{ data: AuthResponse }>("/auth/login", { email, password });
    tokenStore.set(data.data.access_token, data.data.refresh_token);
    setUser(data.data.user);
    const profileRes = await api.get<{ data: Profile }>("/profile");
    setProfile(profileRes.data.data);
  }, []);

  const register = useCallback(
    async (fullName: string, email: string, password: string, phone?: string) => {
      const { data } = await api.post<{ data: AuthResponse }>("/auth/register", {
        full_name: fullName,
        email,
        password,
        phone,
      });
      tokenStore.set(data.data.access_token, data.data.refresh_token);
      setUser(data.data.user);
      setProfile({ ...data.data.user } as Profile);
    },
    []
  );

  const logout = useCallback(async () => {
    try {
      const refresh = tokenStore.getRefresh();
      if (refresh) {
        await api.post("/auth/logout", { refresh_token: refresh });
      }
    } catch {
      /* ignore */
    }
    tokenStore.clear();
    setUser(null);
    setProfile(null);
  }, []);

  const refreshProfile = useCallback(async () => {
    try {
      const res = await api.get<{ data: Profile }>("/profile");
      setProfile(res.data.data);
      setUser(res.data.data);
    } catch (e) {
      console.error(errorMessage(e));
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        loading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
