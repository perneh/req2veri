import { Alert, Box, Button, MenuItem, Paper, Stack, TextField, Typography } from "@mui/material";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { apiFetch } from "../api/client";
import type { TestMethod, VerificationTest } from "../api/types";

export function TestsNewPage() {
  const { t } = useTranslation();
  const nav = useNavigate();
  const qc = useQueryClient();
  const [key, setKey] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [precondition, setPrecondition] = useState("");
  const [action, setAction] = useState("");
  const [method, setMethod] = useState<TestMethod>("test");
  const [expected, setExpected] = useState("");
  const [err, setErr] = useState<string | null>(null);

  const m = useMutation({
    mutationFn: () =>
      apiFetch<VerificationTest>("/tests", {
        method: "POST",
        json: {
          key,
          title,
          description,
          precondition,
          action,
          method,
          requirement_id: null,
          sub_requirement_id: null,
          expected_result: expected,
        },
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["tests"] });
      nav("/tests");
    },
    onError: (e: Error) => setErr(e.message),
  });

  return (
    <Box maxWidth={560}>
      <Typography variant="h5" gutterBottom>
        {t("tests.newStandalone")}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
        {t("tests.standaloneLead")}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        {t("tests.reportLaterHint")}
      </Typography>
      {err && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {err}
        </Alert>
      )}
      <Paper sx={{ p: 2 }}>
        <Stack spacing={2}>
          <TextField label={t("requirements.key")} value={key} onChange={(e) => setKey(e.target.value)} required size="small" />
          <TextField label={t("requirements.reqTitle")} value={title} onChange={(e) => setTitle(e.target.value)} required size="small" />
          <TextField
            label={t("requirements.description")}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            multiline
            minRows={2}
            size="small"
          />
          <TextField
            label={t("tests.precondition")}
            value={precondition}
            onChange={(e) => setPrecondition(e.target.value)}
            multiline
            minRows={2}
            size="small"
          />
          <TextField
            label={t("tests.action")}
            value={action}
            onChange={(e) => setAction(e.target.value)}
            multiline
            minRows={2}
            size="small"
          />
          <TextField select label={t("tests.method")} value={method} onChange={(e) => setMethod(e.target.value as TestMethod)} size="small">
            {(["inspection", "analysis", "test", "demonstration"] as const).map((x) => (
              <MenuItem key={x} value={x}>
                {t(`method.${x}`)}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            label={t("tests.expected")}
            value={expected}
            onChange={(e) => setExpected(e.target.value)}
            multiline
            minRows={2}
            size="small"
          />
          <Button variant="contained" disabled={m.isPending || !key.trim() || !title.trim()} onClick={() => m.mutate()}>
            {t("common.create")}
          </Button>
        </Stack>
      </Paper>
    </Box>
  );
}
