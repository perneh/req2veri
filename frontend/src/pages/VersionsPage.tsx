import { Box, Paper, Table, TableBody, TableCell, TableHead, TableRow, Typography } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";

import { apiFetch } from "../api/client";
import type { TestObjectVersion, TestRun } from "../api/types";
import { StatusChip } from "../components/StatusChip";

export function VersionsPage() {
  const { t } = useTranslation();
  const vq = useQuery({
    queryKey: ["versions"],
    queryFn: () => apiFetch<TestObjectVersion[]>("/test-object-versions"),
  });
  const firstId = vq.data?.[0]?.id;
  const rq = useQuery({
    queryKey: ["runs", firstId],
    queryFn: () => apiFetch<TestRun[]>(`/test-object-versions/${firstId}/runs`),
    enabled: !!firstId,
  });

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        {t("versions.title")}
      </Typography>
      {vq.isLoading && <Typography>{t("common.loading")}</Typography>}
      {vq.data && (
        <Table component={Paper} size="small" sx={{ mb: 3 }}>
          <TableHead>
            <TableRow>
              <TableCell>{t("versions.key")}</TableCell>
              <TableCell>{t("versions.name")}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {vq.data.map((v) => (
              <TableRow key={v.id}>
                <TableCell>{v.key}</TableCell>
                <TableCell>{v.name}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
      {firstId && (
        <>
          <Typography variant="subtitle1" gutterBottom>
            {t("versions.runs")} (id {firstId})
          </Typography>
          {rq.isLoading && <Typography>{t("common.loading")}</Typography>}
          {rq.data && (
            <Table component={Paper} size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Test id</TableCell>
                  <TableCell>{t("tests.status")}</TableCell>
                  <TableCell>{t("requirements.reqTitle")}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rq.data.map((run) => (
                  <TableRow key={run.id}>
                    <TableCell>{run.verification_test_id}</TableCell>
                    <TableCell>
                      <StatusChip value={run.status} kind="test" />
                    </TableCell>
                    <TableCell>{run.actual_result || "—"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </>
      )}
    </Box>
  );
}
