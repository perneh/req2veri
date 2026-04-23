import { Alert, Box, Button, MenuItem, Paper, Stack, TextField, Typography } from "@mui/material";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { apiFetch } from "../api/client";
import type { Requirement, RequirementStatus, Priority } from "../api/types";

export function NewRequirementPage() {
  const { t } = useTranslation();
  const nav = useNavigate();
  const qc = useQueryClient();
  const [key, setKey] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState<RequirementStatus>("draft");
  const [priority, setPriority] = useState<Priority>("medium");
  const [err, setErr] = useState<string | null>(null);

  const m = useMutation({
    mutationFn: () =>
      apiFetch<Requirement>("/requirements", {
        method: "POST",
        json: { key, title, description, status, priority },
      }),
    onSuccess: (r) => {
      void qc.invalidateQueries({ queryKey: ["requirements"] });
      nav(`/requirements/${r.id}#sub`);
    },
    onError: (e: Error) => setErr(e.message),
  });

  return (
    <Box maxWidth={560}>
      <Typography variant="h5" gutterBottom>
        {t("requirements.new")}
      </Typography>
      {err && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {err}
        </Alert>
      )}
      <Paper sx={{ p: 2 }}>
        <Stack spacing={2}>
          <TextField label={t("requirements.key")} value={key} onChange={(e) => setKey(e.target.value)} required />
          <TextField label={t("requirements.reqTitle")} value={title} onChange={(e) => setTitle(e.target.value)} required />
          <TextField
            label={t("requirements.description")}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            multiline
            minRows={3}
          />
          <TextField select label={t("requirements.status")} value={status} onChange={(e) => setStatus(e.target.value as RequirementStatus)}>
            {(["draft", "approved", "implemented", "verified", "rejected"] as const).map((s) => (
              <MenuItem key={s} value={s}>
                {t(`status.${s}`)}
              </MenuItem>
            ))}
          </TextField>
          <TextField select label={t("requirements.priority")} value={priority} onChange={(e) => setPriority(e.target.value as Priority)}>
            {(["low", "medium", "high", "critical"] as const).map((p) => (
              <MenuItem key={p} value={p}>
                {t(`priority.${p}`)}
              </MenuItem>
            ))}
          </TextField>
          <Button variant="contained" disabled={m.isPending || !key || !title} onClick={() => m.mutate()}>
            {t("common.create")}
          </Button>
        </Stack>
      </Paper>
    </Box>
  );
}
