import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import { CssBaseline, ThemeProvider } from "@mui/material";
import type { PaletteMode } from "@mui/material/styles";

import { createAppTheme } from "../theme/githubTheme";

type Ctx = { mode: PaletteMode; toggle: () => void; setMode: (m: PaletteMode) => void };

const ThemeModeContext = createContext<Ctx | null>(null);

const storageKey = "req2veri_theme";

export function AppThemeProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<PaletteMode>(() => {
    const s = localStorage.getItem(storageKey);
    return s === "light" || s === "dark" ? s : "dark";
  });
  const setModePersist = useCallback((m: PaletteMode) => {
    setMode(m);
    localStorage.setItem(storageKey, m);
  }, []);
  const toggle = useCallback(() => {
    setModePersist(mode === "dark" ? "light" : "dark");
  }, [mode, setModePersist]);
  const theme = useMemo(() => createAppTheme(mode), [mode]);
  const value = useMemo(() => ({ mode, toggle, setMode: setModePersist }), [mode, toggle, setModePersist]);
  return (
    <ThemeModeContext.Provider value={value}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ThemeModeContext.Provider>
  );
}

export function useThemeMode() {
  const v = useContext(ThemeModeContext);
  if (!v) throw new Error("useThemeMode outside provider");
  return v;
}
