import {
  Alert,
  Box,
  Button,
  MenuItem,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { useSearchParams } from "react-router-dom";

import { apiFetch } from "../api/client";
import type { TestObjectVersion, TestRun, TestRunUpsert, TestStatus, VerificationTest } from "../api/types";
import { StatusChip } from "../components/StatusChip";

export function TestReportPage() {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const [searchParams] = useSearchParams();
  const [versionId, setVersionId] = useState<number | "">("");
  const [testId, setTestId] = useState<number | "">("");
  const [status, setStatus] = useState<TestStatus>("not_run");
  const [information, setInformation] = useState("");
  const [reportedAt, setReportedAt] = useState(() => new Date().toISOString().slice(0, 16));
  const [message, setMessage] = useState<string | null>(null);

  const versionsQ = useQuery({
    queryKey: ["versions"],
    queryFn: () => apiFetch<TestObjectVersion[]>("/test-object-versions"),
  });
  const testsQ = useQuery({
    queryKey: ["tests", "for-report"],
    queryFn: () => apiFetch<VerificationTest[]>("/tests?limit=500"),
  });

  const runsQ = useQuery({
    queryKey: ["runs", versionId],
    queryFn: () => apiFetch<TestRun[]>(`/test-object-versions/${versionId}/runs`),
    enabled: typeof versionId === "number",
  });

  const testById = useMemo(() => {
    const map = new Map<number, VerificationTest>();
    for (const te of testsQ.data ?? []) map.set(te.id, te);
    return map;
  }, [testsQ.data]);

  useEffect(() => {
    const v = searchParams.get("versionId");
    const tId = searchParams.get("testId");
    if (v && Number.isFinite(Number(v))) setVersionId(Number(v));
    if (tId && Number.isFinite(Number(tId))) setTestId(Number(tId));
  }, [searchParams]);

  const reportMutation = useMutation({
    mutationFn: async () => {
      if (!Number.isFinite(versionId) || !Number.isFinite(testId)) {
        throw new Error(t("testReport.chooseVersionAndTest"));
      }
      const payload: TestRunUpsert = {
        status,
        information,
        ran_at: new Date(reportedAt).toISOString(),
      };
      return apiFetch<TestRun>(`/test-object-versions/${versionId}/runs/${testId}`, {
        method: "PUT",
        json: payload,
      });
    },
    onSuccess: async () => {
      setMessage(t("testReport.saved"));
      await qc.invalidateQueries({ queryKey: ["runs", versionId] });
      await qc.invalidateQueries({ queryKey: ["versions"] });
      await qc.invalidateQueries({ queryKey: ["dashboard"] });
    },
    onError: (e: Error) => setMessage(e.message),
  });

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        {t("testReport.title")}
      </Typography>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Stack spacing={1.5}>
          <TextField
            select
            size="small"
            label={t("testReport.systemVersion")}
            value={versionId}
            onChange={(e) => setVersionId(e.target.value === "" ? "" : Number(e.target.value))}
          >
            <MenuItem value="">{t("testReport.chooseVersion")}</MenuItem>
            {(versionsQ.data ?? []).map((v) => (
              <MenuItem key={v.id} value={v.id}>
                {v.key} - {v.name}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            select
            size="small"
            label={t("testReport.testCase")}
            value={testId}
            onChange={(e) => setTestId(e.target.value === "" ? "" : Number(e.target.value))}
          >
            <MenuItem value="">{t("testReport.chooseTest")}</MenuItem>
            {(testsQ.data ?? []).map((te) => (
              <MenuItem key={te.id} value={te.id}>
                {te.key} - {te.title}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            select
            size="small"
            label={t("tests.status")}
            value={status}
            onChange={(e) => setStatus(e.target.value as TestStatus)}
          >
            <MenuItem value="not_run">{t("status.not_run")}</MenuItem>
            <MenuItem value="passed">{t("status.passed")}</MenuItem>
            <MenuItem value="failed">{t("status.failed")}</MenuItem>
            <MenuItem value="blocked">{t("status.blocked")}</MenuItem>
          </TextField>
          <TextField
            size="small"
            label={t("testReport.information")}
            value={information}
            onChange={(e) => setInformation(e.target.value)}
            multiline
            minRows={2}
          />
          <TextField
            size="small"
            type="datetime-local"
            label={t("testReport.reportDateTime")}
            value={reportedAt}
            onChange={(e) => setReportedAt(e.target.value)}
            InputLabelProps={{ shrink: true }}
          />
          <Button variant="contained" onClick={() => reportMutation.mutate()} disabled={reportMutation.isPending}>
            {t("testReport.report")}
          </Button>
          {message && <Alert severity={reportMutation.isError ? "error" : "success"}>{message}</Alert>}
        </Stack>
      </Paper>

      <Typography variant="h6" gutterBottom>
        {t("testReport.results")}
      </Typography>
      {runsQ.isLoading && <Typography>{t("common.loading")}</Typography>}
      {runsQ.data && (
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>{t("tests.title")}</TableCell>
                <TableCell>{t("tests.status")}</TableCell>
                <TableCell>{t("testReport.information")}</TableCell>
                <TableCell>{t("testReport.reportedBy")}</TableCell>
                <TableCell>{t("testReport.reportedAt")}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {runsQ.data.map((run) => {
                const te = testById.get(run.verification_test_id);
                return (
                  <TableRow key={run.id}>
                    <TableCell>{te ? `${te.key} - ${te.title}` : `#${run.verification_test_id}`}</TableCell>
                    <TableCell>
                      <StatusChip value={run.status} kind="test" />
                    </TableCell>
                    <TableCell>{run.information || "—"}</TableCell>
                    <TableCell>{run.reported_by || "—"}</TableCell>
                    <TableCell>{new Date(run.ran_at).toLocaleString()}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}
