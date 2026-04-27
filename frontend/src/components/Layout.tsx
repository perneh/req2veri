import DarkModeOutlinedIcon from "@mui/icons-material/DarkModeOutlined";
import LightModeOutlinedIcon from "@mui/icons-material/LightModeOutlined";
import {
  AppBar,
  Box,
  Button,
  Container,
  Link as MuiLink,
  Menu,
  MenuItem,
  Select,
  Toolbar,
  Typography,
} from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { Link, Outlet, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useState } from "react";

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
  const [addEditAnchor, setAddEditAnchor] = useState<null | HTMLElement>(null);
  const [systemAnchor, setSystemAnchor] = useState<null | HTMLElement>(null);
  const [reportAnchor, setReportAnchor] = useState<null | HTMLElement>(null);

  const logout = () => {
    setAuthToken(null);
    nav("/login");
  };
  const addEditOpen = Boolean(addEditAnchor);
  const systemOpen = Boolean(systemAnchor);
  const reportOpen = Boolean(reportAnchor);

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
                <Button
                  color="inherit"
                  onClick={(e) => setAddEditAnchor(e.currentTarget)}
                  aria-haspopup="true"
                  aria-expanded={addEditOpen ? "true" : undefined}
                >
                  {t("nav.addEdit")}
                </Button>
                <Menu
                  anchorEl={addEditAnchor}
                  open={addEditOpen}
                  onClose={() => setAddEditAnchor(null)}
                  keepMounted
                >
                  <MenuItem component={Link} to="/requirements" onClick={() => setAddEditAnchor(null)}>
                    {t("nav.requirements")}
                  </MenuItem>
                  <MenuItem component={Link} to="/requirements/overview" onClick={() => setAddEditAnchor(null)}>
                    {t("nav.overview")}
                  </MenuItem>
                  <MenuItem component={Link} to="/tests" onClick={() => setAddEditAnchor(null)}>
                    {t("nav.tests")}
                  </MenuItem>
                </Menu>
                <MuiLink component={Link} to="/requirements/relations" underline="hover" color="inherit">
                  {t("nav.relations")}
                </MuiLink>
                <Button
                  color="inherit"
                  onClick={(e) => setSystemAnchor(e.currentTarget)}
                  aria-haspopup="true"
                  aria-expanded={systemOpen ? "true" : undefined}
                >
                  {t("nav.system")}
                </Button>
                <Menu anchorEl={systemAnchor} open={systemOpen} onClose={() => setSystemAnchor(null)} keepMounted>
                  <MenuItem component={Link} to="/systems/new" onClick={() => setSystemAnchor(null)}>
                    {t("nav.systemAdd")}
                  </MenuItem>
                  <MenuItem component={Link} to="/systems" onClick={() => setSystemAnchor(null)}>
                    {t("nav.systemList")}
                  </MenuItem>
                  <MenuItem component={Link} to="/systems/expand" onClick={() => setSystemAnchor(null)}>
                    {t("nav.systemExpand")}
                  </MenuItem>
                </Menu>
                <Button
                  color="inherit"
                  onClick={(e) => setReportAnchor(e.currentTarget)}
                  aria-haspopup="true"
                  aria-expanded={reportOpen ? "true" : undefined}
                >
                  {t("nav.testReport")}
                </Button>
                <Menu anchorEl={reportAnchor} open={reportOpen} onClose={() => setReportAnchor(null)} keepMounted>
                  <MenuItem component={Link} to="/test-report" onClick={() => setReportAnchor(null)}>
                    {t("nav.testReportSearch")}
                  </MenuItem>
                  <MenuItem component={Link} to="/test-report/trends" onClick={() => setReportAnchor(null)}>
                    {t("nav.testReportTrends")}
                  </MenuItem>
                </Menu>
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
