import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";

import { setToken as persistToken } from "../api/client";

type Auth = {
  token: string | null;
  setAuthToken: (t: string | null) => void;
};

const AuthContext = createContext<Auth | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTok] = useState<string | null>(() => localStorage.getItem("req2veri_token"));
  const setAuthToken = useCallback((t: string | null) => {
    persistToken(t);
    setTok(t);
  }, []);
  const value = useMemo(() => ({ token, setAuthToken }), [token, setAuthToken]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const v = useContext(AuthContext);
  if (!v) throw new Error("useAuth outside AuthProvider");
  return v;
}
