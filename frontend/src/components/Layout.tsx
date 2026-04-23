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
import { Link, Outlet, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { useAuth } from "../context/AuthContext";
import { useThemeMode } from "../context/ThemeModeContext";

export function Layout() {
  const { t, i18n } = useTranslation();
  const { mode, toggle } = useThemeMode();
  const nav = useNavigate();
  const { token, setAuthToken } = useAuth();
  const authed = !!token;

  const logout = () => {
    setAuthToken(null);
    nav("/login");
  };

  return (
    <Box sx={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <AppBar position="sticky" color="default">
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
      <Container maxWidth="lg" sx={{ py: 3, flex: 1 }}>
        <Outlet />
      </Container>
    </Box>
  );
}
