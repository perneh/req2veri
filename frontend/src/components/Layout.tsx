import DarkModeOutlinedIcon from "@mui/icons-material/DarkModeOutlined";
import LightModeOutlinedIcon from "@mui/icons-material/LightModeOutlined";
import {
  AppBar,
  Box,
  Button,
  Container,
  Link as MuiLink,
  MenuItem,
  Select,
  Toolbar,
  Typography,
} from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { Link, Outlet, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { useAuth } from "../context/AuthContext";
import { useThemeMode } from "../context/ThemeModeContext";
import backgroundUrl from "../../img/background.png";

export function Layout() {
  const { t, i18n } = useTranslation();
  const theme = useTheme();
  const { mode, toggle } = useThemeMode();
  const nav = useNavigate();
  const { token, setAuthToken } = useAuth();
  const authed = !!token;

  const logout = () => {
    setAuthToken(null);
    nav("/login");
  };

  const glassPanel =
    theme.palette.mode === "dark" ? "rgba(22, 27, 34, 0.48)" : "rgba(255, 255, 255, 0.66)";

  return (
    <Box sx={{ position: "relative", minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <Box
        aria-hidden
        sx={{
          position: "fixed",
          inset: 0,
          zIndex: 0,
          backgroundImage: `url(${backgroundUrl})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
          backgroundAttachment: { xs: "scroll", md: "fixed" },
          /* Slight punch-up; photo stays visible (no heavy grey wash) */
          filter: { xs: "none", md: "saturate(1.08) contrast(1.04)" },
        }}
      />
      <Box sx={{ position: "relative", zIndex: 1, display: "flex", flexDirection: "column" }}>
        <AppBar position="sticky" color="default" elevation={0}>
          <Toolbar sx={{ gap: 2, flexWrap: "wrap" }}>
            <Typography component={Link} to="/" variant="h6" sx={{ textDecoration: "none", color: "inherit", mr: 2 }}>
              {t("app.name")}
            </Typography>
            {authed && (
              <>
                <MuiLink component={Link} to="/dashboard" underline="hover" color="inherit">
                  {t("nav.dashboard")}
                </MuiLink>
                <MuiLink component={Link} to="/requirements" underline="hover" color="inherit">
                  {t("nav.requirements")}
                </MuiLink>
                <MuiLink component={Link} to="/requirements/overview" underline="hover" color="inherit">
                  {t("nav.overview")}
                </MuiLink>
                <MuiLink component={Link} to="/tests" underline="hover" color="inherit">
                  {t("nav.tests")}
                </MuiLink>
                <MuiLink component={Link} to="/versions" underline="hover" color="inherit">
                  {t("nav.versions")}
                </MuiLink>
              </>
            )}
            <Box sx={{ flexGrow: 1 }} />
            <Select
              size="small"
              value={i18n.language}
              onChange={(e) => {
                const lng = e.target.value;
                void i18n.changeLanguage(lng);
                localStorage.setItem("req2veri_lang", lng);
              }}
              sx={{ minWidth: 120 }}
            >
              <MenuItem value="en">{t("lang.en")}</MenuItem>
              <MenuItem value="sv">{t("lang.sv")}</MenuItem>
              <MenuItem value="de">{t("lang.de")}</MenuItem>
            </Select>
            <Button
              color="inherit"
              onClick={toggle}
              startIcon={mode === "dark" ? <LightModeOutlinedIcon /> : <DarkModeOutlinedIcon />}
            >
              {mode === "dark" ? t("theme.light") : t("theme.dark")}
            </Button>
            {authed ? (
              <Button color="inherit" onClick={logout}>
                {t("nav.logout")}
              </Button>
            ) : (
              <Button component={Link} to="/login" color="inherit">
                {t("nav.login")}
              </Button>
            )}
          </Toolbar>
        </AppBar>
        <Container maxWidth="lg" sx={{ py: 3 }}>
          <Box
            sx={{
              width: "100%",
              borderRadius: 2,
              px: { xs: 1.5, sm: 2.5 },
              py: { xs: 2, sm: 2.5 },
              backdropFilter: "blur(14px) saturate(1.15)",
              WebkitBackdropFilter: "blur(14px) saturate(1.15)",
              bgcolor: glassPanel,
              border: `1px solid ${theme.palette.divider}`,
              boxShadow:
                theme.palette.mode === "dark"
                  ? "0 12px 40px rgba(0,0,0,0.35)"
                  : "0 12px 40px rgba(15, 23, 42, 0.08)",
            }}
          >
            <Outlet />
          </Box>
        </Container>
      </Box>
    </Box>
  );
}
