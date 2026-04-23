import { createTheme, type PaletteMode } from "@mui/material/styles";

const githubDark = {
  bg: "#0d1117",
  surface: "#161b22",
  border: "#30363d",
  muted: "#8b949e",
  text: "#e6edf3",
  accent: "#2f81f7",
  accentMuted: "#388bfd26",
};

const githubLight = {
  bg: "#ffffff",
  surface: "#f6f8fa",
  border: "#d0d7de",
  muted: "#57606a",
  text: "#1f2328",
  accent: "#0969da",
  accentMuted: "#0969da14",
};

export function createAppTheme(mode: PaletteMode) {
  const c = mode === "dark" ? githubDark : githubLight;
  return createTheme({
    palette: {
      mode,
      primary: { main: c.accent },
      background: { default: c.bg, paper: c.surface },
      text: { primary: c.text, secondary: c.muted },
      divider: c.border,
    },
    shape: { borderRadius: 6 },
    typography: {
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
      h6: { fontWeight: 600, fontSize: "1rem" },
    },
    components: {
      MuiAppBar: {
        styleOverrides: {
          root: {
            backgroundColor: c.surface,
            color: c.text,
            borderBottom: `1px solid ${c.border}`,
            boxShadow: "none",
          },
        },
      },
      MuiButton: { defaultProps: { variant: "outlined", size: "small" } },
      MuiPaper: {
        styleOverrides: {
          root: { backgroundImage: "none", border: `1px solid ${c.border}` },
        },
      },
      MuiTableCell: {
        styleOverrides: { root: { borderColor: c.border } },
      },
    },
  });
}
