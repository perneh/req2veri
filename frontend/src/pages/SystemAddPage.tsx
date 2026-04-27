import { Alert, Box, Button, Paper, Stack, TextField, Typography } from "@mui/material";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { apiFetch } from "../api/client";
import type { TestObjectVersion } from "../api/types";

export function SystemAddPage() {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const [key, setKey] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  const createMutation = useMutation({
    mutationFn: () =>
      apiFetch<TestObjectVersion>("/test-object-versions", {
        method: "POST",
        json: { key, name, description },
      }),
    onSuccess: async () => {
      setMessage(t("systems.saved"));
      setKey("");
      setName("");
      setDescription("");
      await qc.invalidateQueries({ queryKey: ["versions"] });
    },
    onError: (e: Error) => setMessage(e.message),
  });

  return (
    <Box maxWidth={700}>
      <Typography variant="h5" gutterBottom>
        {t("systems.addTitle")}
      </Typography>
      <Paper sx={{ p: 2 }}>
        <Stack spacing={1.5}>
          <TextField size="small" label={t("systems.key")} value={key} onChange={(e) => setKey(e.target.value)} />
          <TextField size="small" label={t("systems.name")} value={name} onChange={(e) => setName(e.target.value)} />
          <TextField
            size="small"
            label={t("systems.description")}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            multiline
            minRows={3}
          />
          <Button
            variant="contained"
            onClick={() => createMutation.mutate()}
            disabled={createMutation.isPending || !key.trim() || !name.trim()}
          >
            {t("systems.addButton")}
          </Button>
          {message && <Alert severity={createMutation.isError ? "error" : "success"}>{message}</Alert>}
        </Stack>
      </Paper>
    </Box>
  );
}
