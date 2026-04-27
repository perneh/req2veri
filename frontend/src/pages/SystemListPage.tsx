import { Box, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from "@mui/material";
import { useQueries, useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import { useTranslation } from "react-i18next";

import { apiFetch } from "../api/client";
import type { TestObjectVersion, TestRun } from "../api/types";

function summarize(runs: TestRun[]) {
  return runs.reduce(
    (acc, run) => {
      acc.total += 1;
      acc[run.status] += 1;
      return acc;
    },
    { total: 0, not_run: 0, passed: 0, failed: 0, blocked: 0 },
  );
}

export function SystemListPage() {
  const { t } = useTranslation();
  const versionsQ = useQuery({
    queryKey: ["versions"],
    queryFn: () => apiFetch<TestObjectVersion[]>("/test-object-versions"),
  });

  const runsQueries = useQueries({
    queries: (versionsQ.data ?? []).map((v) => ({
      queryKey: ["runs", v.id],
      queryFn: () => apiFetch<TestRun[]>(`/test-object-versions/${v.id}/runs`),
      enabled: !!versionsQ.data,
    })),
  });

  const rows = useMemo(() => {
    return (versionsQ.data ?? []).map((v, index) => {
      const runs = runsQueries[index]?.data ?? [];
      return { version: v, summary: summarize(runs) };
    });
  }, [runsQueries, versionsQ.data]);

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        {t("systems.listTitle")}
      </Typography>
      {versionsQ.isLoading && <Typography>{t("common.loading")}</Typography>}
      {rows.length > 0 && (
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>{t("systems.key")}</TableCell>
                <TableCell>{t("systems.name")}</TableCell>
                <TableCell>{t("systems.total")}</TableCell>
                <TableCell>{t("status.passed")}</TableCell>
                <TableCell>{t("status.failed")}</TableCell>
                <TableCell>{t("status.not_run")}</TableCell>
                <TableCell>{t("status.blocked")}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map(({ version, summary }) => (
                <TableRow key={version.id}>
                  <TableCell>{version.key}</TableCell>
                  <TableCell>{version.name}</TableCell>
                  <TableCell>{summary.total}</TableCell>
                  <TableCell>{summary.passed}</TableCell>
                  <TableCell>{summary.failed}</TableCell>
                  <TableCell>{summary.not_run}</TableCell>
                  <TableCell>{summary.blocked}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}
