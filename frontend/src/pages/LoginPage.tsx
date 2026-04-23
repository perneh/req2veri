import {
  Alert,
  Box,
  Button,
  Paper,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from "@mui/material";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { apiFetch } from "../api/client";
import { useAuth } from "../context/AuthContext";

const apiBase = import.meta.env.VITE_API_BASE ?? "/api";

export function LoginPage() {
  const { t } = useTranslation();
  const { setAuthToken } = useAuth();
  const nav = useNavigate();
  const [tab, setTab] = useState(0);
  const [username, setUsername] = useState("demo");
  const [password, setPassword] = useState("demo12345");
  const [email, setEmail] = useState("demo@example.com");
  const [err, setErr] = useState<string | null>(null);

  const login = async () => {
    setErr(null);
    const body = new URLSearchParams();
    body.set("username", username);
    body.set("password", password);
    const res = await fetch(`${apiBase}/auth/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      setErr(typeof data.detail === "string" ? data.detail : "Login failed");
      return;
    }
    setAuthToken(data.access_token);
    nav("/dashboard");
  };

  const register = async () => {
    setErr(null);
    try {
      await apiFetch("/auth/register", {
        method: "POST",
        json: { username, email, password },
      });
      await login();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Register failed");
    }
  };

  return (
    <Box maxWidth={400} mx="auto" mt={6}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          {t("app.name")}
        </Typography>
        <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
          <Tab label={t("auth.signIn")} />
          <Tab label={t("auth.register")} />
        </Tabs>
        {err && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {err}
          </Alert>
        )}
        <Stack spacing={2}>
          <TextField
            label={t("auth.username")}
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            fullWidth
            autoComplete="username"
          />
          {tab === 1 && (
            <TextField
              label={t("auth.email")}
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              fullWidth
            />
          )}
          <TextField
            label={t("auth.password")}
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            fullWidth
            autoComplete={tab === 0 ? "current-password" : "new-password"}
          />
          {tab === 0 ? (
            <Button variant="contained" onClick={() => void login()}>
              {t("auth.signIn")}
            </Button>
          ) : (
            <Button variant="contained" onClick={() => void register()}>
              {t("auth.register")}
            </Button>
          )}
        </Stack>
      </Paper>
    </Box>
  );
}
